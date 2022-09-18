"""
Module containing helper functions for accessing Algorand blockchain.
"""
# So that sphinx picks up on the type aliases
from __future__ import annotations

import base64
import time
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, Optional

import pyteal
from algosdk import mnemonic
from algosdk.error import IndexerHTTPError
from algosdk.future import transaction as algosdk_transaction
from algosdk.future.transaction import LogicSig, PaymentTxn, wait_for_confirmation
from algosdk.kmd import KMDClient
from algosdk.v2client import algod, indexer
from pyteal import Mode, compileTeal

from .config_params import ConfigParams
from .entities import AlgoUser
from .utils import _convert_algo_dict


## CLIENTS
def _algod_client() -> algod.AlgodClient:
    """Instantiate and return Algod client object."""
    return algod.AlgodClient(ConfigParams.algod_token, ConfigParams.algod_address)


def _indexer_client() -> indexer.IndexerClient:
    """Instantiate and return Indexer client object."""
    return indexer.IndexerClient(
        ConfigParams.indexer_token, ConfigParams.indexer_address
    )


## KMD
def _get_kmd_account_private_key(address: str) -> str:
    """Return passphrase for provided ``address``."""
    # Inspired by https://github.com/algorand-devrel/demo-avm1.1/blob/master/demos/utils/sandbox.py
    kmd = KMDClient(ConfigParams.kmd_token, ConfigParams.kmd_address)
    wallets = kmd.list_wallets()

    wallet_id = None
    for wallet in wallets:
        if wallet["name"] == ConfigParams.kmd_wallet_name:
            wallet_id = wallet["id"]
            break

    if wallet_id is None:
        raise ValueError(f"Wallet not found: {ConfigParams.kmd_wallet_name}")

    wallet_handle = kmd.init_wallet_handle(wallet_id, ConfigParams.kmd_wallet_password)

    try:
        private_key = kmd.export_key(
            wallet_handle, ConfigParams.kmd_wallet_password, address
        )
    finally:
        kmd.release_wallet_handle(wallet_handle)

    return private_key


## TRANSACTIONS
def process_transactions(transactions: list[algosdk_transaction.Transaction]) -> int:
    """Send provided grouped ``transactions`` to network and wait for confirmation."""
    client = _algod_client()
    transaction_id = client.send_transactions(transactions)
    wait_for_confirmation(client, transaction_id, 4)
    return transaction_id


def suggested_params(**kwargs: Any) -> algosdk_transaction.SuggestedParams:
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
    when running ``func``.
    """
    # To preserve the original type signature of `func` in the sphinx docs
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        sleep_step = 0.1

        # First wait for the indexer to catch up with the latest `algod_round`
        algod_round = _algod_client().status()["last-round"]
        while _indexer_client().health()["round"] < algod_round:
            time.sleep(sleep_step)

        # Give the indexer a number of tries before raising an error
        timeout = 0.0
        while timeout < ConfigParams.indexer_timeout:
            try:
                ret = func(*args, **kwargs)
                break
            except IndexerHTTPError:
                time.sleep(sleep_step)
                timeout += sleep_step
        else:
            raise TimeoutError("Timeout reached waiting for indexer.")

        return ret

    return wrapped


@_wait_for_indexer
@lru_cache(maxsize=1)
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
        raise RuntimeError("Initial funds account not yet created!")

    private_key = _get_kmd_account_private_key(initial_address)

    # Return an `AlgoUser` of the initial account
    return AlgoUser(initial_address, private_key)


@_wait_for_indexer
def transaction_info(transaction_id: int) -> dict[str, Any]:
    """Return transaction with provided ``transaction_id``."""
    return _indexer_client().transaction(transaction_id)


@_wait_for_indexer
def application_global_state(
    app_id: int, address_fields: Optional[list[str]] = None
) -> dict[str, str]:
    """Read the global state of an application.

    Parameters
    ----------
    app_id
       The ID of the application to query for its global state.
    address_fields
       The keys where the value is expected to be an Algorand address. Address values need to be encoded to get them in human-readable format.

    Returns
    -------
    dict[str, str]
        The global state query results.
    """
    app = _indexer_client().applications(app_id)
    app_global_state = app["application"]["params"]["global-state"]
    return _convert_algo_dict(app_global_state, address_fields)


@_wait_for_indexer
def application_local_state(
    app_id: int, account: AlgoUser, address_fields: Optional[list[str]] = None
) -> dict[str, str]:
    """Read the local sate of an account relating to an application.

    Parameters
    ----------
    app_id
       The ID of the application to query for the local state.
    account
       The user whose local state to read.
    address_fields
       The keys where the value is expected to be an Algorand address. Address values need to be encoded to get them in human-readable format.

    Returns
    -------
    dict[str, str]
        The local state query results.
    """
    account_data = _indexer_client().account_info(account.address)["account"]

    # Use get to index `account` since it may not have any local states yet
    ret = {}
    for local_state in account_data.get("apps-local-state", []):
        if local_state["id"] == app_id:
            ret = _convert_algo_dict(local_state["key-value"], address_fields)
            break

    return ret


@_wait_for_indexer
def account_balance(account: AlgoUser) -> int:
    """Return the balance amount for the provided ``account``."""
    account_data = _indexer_client().account_info(account.address)["account"]
    return account_data["amount"]


@_wait_for_indexer
def asset_balance(account: AlgoUser, asset_id: int) -> Optional[int]:
    """Return the asset balance amount for the provided ``account`` and ``asset_id``."""
    account_data = _indexer_client().account_info(account.address)["account"]
    assets = account_data.get("assets", [])

    # Search for the `asset_id` in `assets`
    for asset in assets:
        if asset["asset-id"] == asset_id:
            return asset["amount"]

    # No `asset_id` was found, so return `None`
    return None


@_wait_for_indexer
def asset_info(asset_id: int) -> Dict[str, Any]:
    """Return the asset information for the provided ``asset_id``."""
    return _indexer_client().asset_info(asset_id)


def _compile_source(source: str) -> bytes:
    """Compile and return teal binary code."""
    compile_response = _algod_client().compile(source)
    return base64.b64decode(compile_response["result"])


def compile_program(program: pyteal.Expr, mode: Mode, version: int = 5) -> bytes:
    """Compiles a PyTeal smart contract program to the TEAL binary code.

    Parameters
    ----------
    program
        A PyTeal expression representing an Algorand program.
    mode
        The mode with which to compile the supplied PyTeal program.
    version
        The version with which to compile the supplied PyTeal program.

    Returns
    -------
    bytes
        The TEAL compiled binary code.
    """
    source = compileTeal(program, mode=mode, version=version)
    return _compile_source(source)
