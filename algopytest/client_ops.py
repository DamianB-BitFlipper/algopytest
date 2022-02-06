"""
Module containing helper functions for accessing Algorand blockchain.

Inspired from: https://github.com/ipaleka/algorand-contracts-testing/blob/main/helpers.py
"""
# So that sphinx picks up on the type aliases
from __future__ import annotations

import base64
import pty
import subprocess
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from algosdk import mnemonic
from algosdk.encoding import encode_address
from algosdk.error import IndexerHTTPError
from algosdk.future import transaction
from algosdk.future.transaction import (
    LogicSig,
    LogicSigTransaction,
    PaymentTxn,
    wait_for_confirmation,
)
from algosdk.v2client import algod, indexer
from pyteal import Mode, compileTeal

from .config_params import ConfigParams
from .entities import AlgoUser
from .type_stubs import PyTEAL


## CLIENTS
def _algod_client() -> algod.AlgodClient:
    """Instantiate and return Algod client object."""
    return algod.AlgodClient(ConfigParams.algod_token, ConfigParams.algod_address)


def _indexer_client() -> indexer.IndexerClient:
    """Instantiate and return Indexer client object."""
    return indexer.IndexerClient(
        ConfigParams.indexer_token, ConfigParams.indexer_address
    )


## SANDBOX
def _cli_passphrase_for_account(address: str) -> str:
    """Return passphrase for provided `address`."""
    process = call_sandbox_command("goal", "account", "export", "-a", address)

    if process.stderr:
        raise RuntimeError(process.stderr.decode("utf8"))

    passphrase = ""
    parts = process.stdout.decode("utf8").split('"')
    if len(parts) > 1:
        passphrase = parts[1]
    if passphrase == "":
        raise ValueError(
            "Can't retrieve passphrase from the address: %s\noutput: %s"
            % (address, process.stdout.decode("utf8"))
        )
    return passphrase


def _sandbox_executable() -> Path:
    """Return full path to Algorand's sandbox executable."""
    return ConfigParams.sandbox_dir / "sandbox"


def call_sandbox_command(*args: str) -> subprocess.CompletedProcess:
    """Call and return sandbox command composed from provided arguments."""
    return subprocess.run(
        [_sandbox_executable(), *args], stdin=pty.openpty()[1], capture_output=True
    )


## TRANSACTIONS
def process_logic_sig_transaction(logic_sig: Any, payment_transaction: Any) -> Any:
    """Create logic signature transaction and send it to the network."""
    # TODO: Typing and general behavior

    client = _algod_client()
    logic_sig_transaction = LogicSigTransaction(payment_transaction, logic_sig)
    transaction_id = client.send_transaction(logic_sig_transaction)
    wait_for_confirmation(client, transaction_id, 4)
    return transaction_id


def process_transactions(transactions: list[transaction.Transaction]) -> int:
    """Send provided grouped `transactions` to network and wait for confirmation."""
    client = _algod_client()
    transaction_id = client.send_transactions(transactions)
    wait_for_confirmation(client, transaction_id, 4)
    return transaction_id


def suggested_params(**kwargs: Any) -> transaction.SuggestedParams:
    """Return the suggested params from the algod client.

    Set the provided attributes in ``kwargs`` in the suggested parameters.
    """
    params = _algod_client().suggested_params()

    for key, value in kwargs.items():
        setattr(params, key, value)

    return params


def pending_transaction_info(transaction_id: int) -> dict[str, Any]:
    """Return info on the pending transaction status."""
    client = _algod_client()
    return client.pending_transaction_info(transaction_id)


## INDEXER RETRIEVAL
def _wait_for_indexer(func: Callable) -> Callable:
    """A decorator function to automatically wait for indexer timeout
    when running `func`.
    """
    # To preserve the original type signature of `func` in the sphinx docs
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        timeout = 0
        while timeout < ConfigParams.indexer_timeout:
            try:
                ret = func(*args, **kwargs)
                break
            except IndexerHTTPError:
                time.sleep(1)
                timeout += 1
        else:
            raise TimeoutError("Timeout reached waiting for indexer.")

        return ret

    return wrapped


@_wait_for_indexer
def _initial_funds_account() -> AlgoUser:
    """Get the account initially created by the sandbox.

    Such an account is used to transfer initial funds for the accounts
    created by this pytest plugin.
    """
    initial_address: Optional[str] = None
    # Use the configured value, if available
    if ConfigParams.initial_funds_account is not None:
        initial_address = ConfigParams.initial_funds_account
    else:
        # Make an educated guess for the `initial_address` by
        # reading addresses from the indexer
        initial_address = next(
            (
                account.get("address")
                for account in _indexer_client().accounts().get("accounts", [{}, {}])
                if account.get("created-at-round") == 0
                and account.get("status") == "Online"
            ),
            None,
        )

    # Sanity check
    if initial_address is None:
        raise Exception("Initial funds account not yet created!")

    passphrase = _cli_passphrase_for_account(initial_address)
    private_key = mnemonic.to_private_key(passphrase)

    # Return an `AlgoUser` of the initial account
    return AlgoUser(initial_address, private_key)


@_wait_for_indexer
def transaction_info(transaction_id: int) -> dict[str, Any]:
    """Return transaction with provided id."""
    return _indexer_client().transaction(transaction_id)


@_wait_for_indexer
def application_global_state(app_id: int, addresses: list[str] = []) -> dict[str, str]:
    """Read the global state of an application.

    The ``addresses`` are the keys where the value is expected
    to be an Algorand address. Address values need to be
    encoded to get their human-readable forms.
    """
    app = _indexer_client().applications(app_id)
    app_global_state = app["application"]["params"]["global-state"]
    return _convert_algo_dict(app_global_state, addresses)


@_wait_for_indexer
def account_balance(address: str) -> int:
    """Return the balance amount for the provided `address`."""
    account = _indexer_client().account_info(address)["account"]
    return account["amount"]


## UTILITY
def _compile_source(source: str) -> bytes:
    """Compile and return teal binary code."""
    compile_response = _algod_client().compile(source)
    return base64.b64decode(compile_response["result"])


def compile_program(
    program: PyTEAL, mode: Mode = Mode.Application, version: int = 5
) -> bytes:
    """Compiles a PyTEAL smart contract program to the teal binary code."""
    source = compileTeal(program(), mode=mode, version=version)
    return _compile_source(source)


def logic_signature(teal_source: Any) -> Any:
    """Create and return logic signature for provided `teal_source`."""
    # TODO: Typing and general behavior
    compiled_binary = _compile_source(teal_source)
    return LogicSig(compiled_binary)


def _base64_to_str(b64: str) -> str:
    """Converts a b64 encoded string to a normal UTF-8 string."""
    # Decode the base64 to bytes and then decode them as a UTF-8 string
    byte_decoding = base64.b64decode(b64)
    return byte_decoding.decode("utf-8")


def _convert_algo_dict(
    algo_dict: list[dict[str, Any]], addresses: list[str]
) -> dict[str, str]:
    """Converts an Algorand dictionary to a Python one."""
    ret = {}
    for entry in algo_dict:
        key = _base64_to_str(entry["key"])

        value_type = entry["value"]["type"]

        if value_type == 0:  # Integer
            value = entry["value"]["uint"]
        elif value_type == 1 and key not in addresses:  # Bytes non-address
            value = _base64_to_str(entry["value"]["bytes"])
        elif value_type == 1 and key in addresses:  # Bytes address
            value = encode_address(base64.b64decode(entry["value"]["bytes"]))
        else:
            raise ValueError(f"Unknown value type for key: {key}")

        ret[key] = value

    return ret
