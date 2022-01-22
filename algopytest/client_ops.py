"""
Module containing helper functions for accessing Algorand blockchain.

Inspired from: https://github.com/ipaleka/algorand-contracts-testing/blob/main/helpers.py
"""

import base64
import pty
import subprocess
import time

from algosdk import mnemonic
from algosdk.encoding import encode_address
from algosdk.error import IndexerHTTPError
from algosdk.future.transaction import LogicSig, LogicSigTransaction, PaymentTxn
from algosdk.v2client import algod, indexer
from pyteal import Mode, compileTeal

from .config_params import ConfigParams
from .entities import AlgoUser


## CLIENTS
def _algod_client():
    """Instantiate and return Algod client object."""
    return algod.AlgodClient(ConfigParams.algod_token, ConfigParams.algod_address)


def _indexer_client():
    """Instantiate and return Indexer client object."""
    return indexer.IndexerClient(
        ConfigParams.indexer_token, ConfigParams.indexer_address
    )


## SANDBOX
def _cli_passphrase_for_account(address):
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


def _sandbox_executable():
    """Return full path to Algorand's sandbox executable."""
    return ConfigParams.sandbox_dir / "sandbox"


def call_sandbox_command(*args):
    """Call and return sandbox command composed from provided arguments."""
    return subprocess.run(
        [_sandbox_executable(), *args], stdin=pty.openpty()[1], capture_output=True
    )


## TRANSACTIONS
def _wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception("pool error: {}".format(pending_txn["pool-error"]))
        client.status_after_block(current_round)
        current_round += 1
    raise Exception(
        "pending tx not found in timeout rounds, timeout value = : {}".format(timeout)
    )


def process_logic_sig_transaction(logic_sig, payment_transaction):
    """Create logic signature transaction and send it to the network."""
    client = _algod_client()
    logic_sig_transaction = LogicSigTransaction(payment_transaction, logic_sig)
    transaction_id = client.send_transaction(logic_sig_transaction)
    _wait_for_confirmation(client, transaction_id, 4)
    return transaction_id


def process_transactions(transactions):
    """Send provided grouped `transactions` to network and wait for confirmation."""
    client = _algod_client()
    transaction_id = client.send_transactions(transactions)
    _wait_for_confirmation(client, transaction_id, 4)
    return transaction_id


def suggested_params():
    """Return the suggested params from the algod client."""
    return _algod_client().suggested_params()


def pending_transaction_info(transaction_id):
    """Return info on the pending transaction status."""
    client = _algod_client()
    return client.pending_transaction_info(transaction_id)


## INDEXER RETRIEVAL
def _wait_for_indexer(func):
    """A decorator function to automatically wait for indexer timeout
    when running `func`.
    """

    def wrapped(*args, **kwargs):
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
def _initial_funds_account():
    """Get the account initially created by the sandbox.

    Such an account is used to transfer initial funds for the accounts
    created by this pytest plugin.
    """
    initial_address = next(
        (
            account.get("address")
            for account in _indexer_client().accounts().get("accounts", [{}, {}])
            if account.get("created-at-round") == 0
            and account.get("status") == "Online"  # "Online" for devMode
        ),
        None,
    )
    passphrase = _cli_passphrase_for_account(initial_address)
    private_key = mnemonic.to_private_key(passphrase)

    # Return an `AlgoUser` of the initial account
    return AlgoUser(initial_address, private_key)


@_wait_for_indexer
def transaction_info(transaction_id):
    """Return transaction with provided id."""
    return _indexer_client().transaction(transaction_id)


@_wait_for_indexer
def application_global_state(app_id, addresses=[]):
    """Read the global state of an application.

    The `addresses` are the keys where the value is expected
    to be an Algorand address. Address values need to be
    encoded to get their human-readable forms.
    """
    app = _indexer_client().applications(app_id)
    app_global_state = app["application"]["params"]["global-state"]
    return _convert_algo_dict(app_global_state, addresses)


@_wait_for_indexer
def account_balance(address):
    """Return the balance amount for the provided `address`."""
    account = _indexer_client().account_info(address)["account"]
    return account["amount"]


## UTILITY
def _compile_source(source):
    """Compile and return teal binary code."""
    compile_response = _algod_client().compile(source)
    return base64.b64decode(compile_response["result"])


def compile_program(program, mode=Mode.Application, version=5):
    """Compiles a PyTEAL smart contract program to the teal binary code."""
    source = compileTeal(program(), mode=mode, version=version)
    return _compile_source(source)


def logic_signature(teal_source):
    """Create and return logic signature for provided `teal_source`."""
    compiled_binary = _compile_source(teal_source)
    return LogicSig(compiled_binary)


def _convert_algo_dict(algo_dict, addresses):
    """Converts an Algorand dictionary to a Python one."""
    ret = {}
    for entry in algo_dict:
        key = base64.b64decode(entry["key"])

        value_type = entry["value"]["type"]

        if value_type == 0:  # Integer
            value = entry["value"]["uint"]
        elif value_type == 1:  # Bytes
            value = base64.b64decode(entry["value"]["bytes"])
        else:
            raise ValueError(f"Unknown value type for key: {key}")

        ret[key] = value

    # Encode the `addresses` supplied to get
    # their human-readable forms
    for address in addresses:
        ret[address] = encode_address(ret[address])

    return ret
