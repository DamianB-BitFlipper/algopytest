"""
Module containing helper functions for accessing Algorand blockchain.

Inspired from: https://github.com/ipaleka/algorand-contracts-testing/blob/main/helpers.py
"""

import base64
import pty
import subprocess
import time

from algosdk import account, mnemonic
from algosdk.error import IndexerHTTPError
from algosdk.future.transaction import LogicSig, LogicSigTransaction, PaymentTxn
from algosdk.v2client import algod, indexer
from pyteal import Mode, compileTeal

from .plugin_initialization import Inits
from .entities import AlgoUser

## CLIENTS
def _algod_client():
    """Instantiate and return Algod client object."""
    return algod.AlgodClient(Inits.algod_address,
                             Inits.algod_token)


def _indexer_client():
    """Instantiate and return Indexer client object."""
    return indexer.IndexerClient(Inits.indexer_address,
                                 Inits.indexer_token)


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


def _cli_balance_of_account(address):
    """Return the balance amount for the provided `address`."""
    process = call_sandbox_command("goal", "account", "balance", "-a", address)

    if process.stderr:
        raise RuntimeError(process.stderr.decode("utf8"))

    parts = process.stdout.decode("utf8").split()
    if len(parts) > 1:
        return int(parts[0])
    else:
        raise ValueError(
            "Can't retrieve balance from the address: %s\noutput: %s"
            % (address, process.stdout.decode("utf8"))
        )

def _sandbox_executable():
    """Return full path to Algorand's sandbox executable."""
    return Inits.sandbox_dir + "/sandbox"


def call_sandbox_command(*args):
    """Call and return sandbox command composed from provided arguments."""
    return subprocess.run(
        [_sandbox_executable(), *args], stdin=pty.openpty()[1], capture_output=True
    )


## TRANSACTIONS
def _add_transaction(sender, receiver, amount, priv_key=None, passphrase=None, note="", close_remainder_to=""):
    """Create and sign transaction from provided arguments.

    Returned non-empty tuple carries field where error was raised and description.
    If the first item is None then the error is non-field/integration error.
    Returned two-tuple of empty strings marks successful transaction.
    """
    client = _algod_client()
    params = client.suggested_params()
    unsigned_txn = PaymentTxn(
        sender,
        params,
        receiver,
        amount,
        note=note.encode(), 
        close_remainder_to=close_remainder_to,
    )
    
    if priv_key is not None:
        private_key = priv_key
    elif passphrase is not None:
        private_key = mnemonic.to_private_key(passphrase)
    else:
        raise ValueError("A private key or passphrase must be passed in.")

    signed_txn = unsigned_txn.sign(private_key)
    transaction_id = client.send_transaction(signed_txn)
    _wait_for_confirmation(client, transaction_id, 4)
    return transaction_id


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


def create_payment_transaction(escrow_address, params, receiver, amount):
    """Create and return payment transaction from provided arguments."""
    return PaymentTxn(escrow_address, params, receiver, amount)


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

## CREATING
def add_standalone_account(funded=True):
    """Create standalone account and return two-tuple of its private key and address."""
    private_key, address = account.generate_account()

    if funded:
        fund_account(address)

    return AlgoUser(private_key, address)


def fund_account(address, initial_funds=1_000_000_000):
    """Fund provided `address` with `initial_funds` amount of microAlgos."""
    initial_funds_address = _initial_funds_address()
    if initial_funds_address is None:
        raise Exception("Initial funds weren't transferred!")
    _add_transaction(
        initial_funds_address,
        address,
        initial_funds,
        passphrase=_cli_passphrase_for_account(initial_funds_address),
        note="Initial funds",
    )


def defund_account(sender_priv):
    """Return the entire balance of `sender_priv` back to the `initial_fund_address`."""
    initial_funds_address = _initial_funds_address()
    if initial_funds_address is None:
        raise Exception("Initial funds weren't transferred!")

    sender_addr = account.address_from_private_key(sender_priv)
    _add_transaction(
        sender_addr,
        initial_funds_address,
        0,
        priv_key=sender_priv,
        note="Returning funds",
        close_remainder_to=initial_funds_address,
    )


## RETRIEVING
def _initial_funds_address():
    """Get the address of initially created account having enough funds.

    Such an account is used to transfer initial funds for the accounts
    created in this tutorial.
    """
    return next(
        (
            account.get("address")
            for account in _indexer_client().accounts().get("accounts", [{}, {}])
            if account.get("created-at-round") == 0
            and account.get("status") == "Online"  # "Online" for devMode
        ),
        None,
    )


def account_balance(address):
    """Return funds balance of the account having provided address."""
    account_info = _algod_client().account_info(address)
    return account_info.get("amount")

def _wait_for_indexer(func):
    """A decorator function to automatically wait for indexer timeout 
    when running `func`.
    """
    def wrapped(*args, **kwargs):
        timeout = 0
        while timeout < Inits.indexer_timeout:
            try:
                ret = func(*args, **kwargs)
                break
            except IndexerHTTPError:
                time.sleep(1)
                timeout += 1
        else:
            raise TimeoutError(
                "Timeout reached waiting for indexer."
            )

        return ret

    return wrapped

@_wait_for_indexer
def transaction_info(transaction_id):
    """Return transaction with provided id."""
    return _indexer_client().transaction(transaction_id)

def _convert_algo_dict(algo_dict):
    """Converts an Algorand dictionary to a Python one."""
    ret = {}
    for entry in algo_dict:
        key = base64.b64decode(entry['key'])

        value_type = entry['value']['type']

        if value_type == 0: # Integer
            value = entry['value']['uint']
        elif value_type == 1: # Bytes
            value = base64.b64decode(entry['value']['bytes'])
        else:
            raise ValueError(f'Unknown value type for key: {key}')

        ret[key] = value

    return ret

@_wait_for_indexer
def application_global_state(app_id):
    """Read the global state of an application.

    If `address` is supplied, then read the local state of that
    account for the respective application.
    """
    app = _indexer_client().applications(app_id)
    app_global_state = app['application']['params']['global-state']
    return _convert_algo_dict(app_global_state)

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
