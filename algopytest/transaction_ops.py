from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from algosdk import account
from algosdk.future import transaction

from .client_ops import pending_transaction_info, process_transactions, suggested_params
from .entities import AlgoUser, NullUser
from .type_stubs import PyTEAL


def transaction_boilerplate(
    no_log: bool = False,
    no_params: bool = False,
    no_send: bool = False,
    no_sign: bool = False,
    format_finish: Optional[Callable] = None,
    return_fn: Optional[Callable] = None,
) -> Callable:
    """A decorator to handle all of the transaction boilerplate."""

    def decorator(func: Callable) -> Callable:
        """The actual decorator since it takes the arguments above."""

        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            # Filter all decorator arguments identified by `__` at the
            # start and remove them from the `kwargs`
            decorator_args = {k: v for k, v in kwargs.items() if k.startswith("__")}
            for decorator_key in decorator_args:
                del kwargs[decorator_key]

            # Pre-process the `decorator_args` and `kwargs` as necessary
            log: Callable[..., None] = print
            if decorator_args.get("__no_log", no_log):
                # Disable logging
                def ignore(*args: Any) -> None:
                    return None

                log = ignore

            # If `params` was not supplied, insert the suggested
            # parameters unless disabled by `no_params`
            if kwargs.get("params", None) is None and not decorator_args.get(
                "__no_params", no_params
            ):
                kwargs["params"] = suggested_params(flat_fee=True, fee=1000)

            log(f"Running {func.__name__}")

            # Create unsigned transaction
            signer, txn = func(*args, **kwargs)

            # Return the `signer` and `txn` if no sending was requested
            if decorator_args.get("__no_send", no_send):
                return signer, txn

            if decorator_args.get("__no_sign", no_sign):
                # Send the `txn` as is
                output_to_send = txn
            else:
                # Sign the `txn`
                output_to_send = txn.sign(signer.private_key)

            # If the `output_to_send` is not a list, wrap it
            # in one as a singular transaction to be sent
            if type(output_to_send) is not list:
                output_to_send = [output_to_send]

            # Send the transaction and await for confirmation
            tx_id = process_transactions(output_to_send)

            # Display results
            transaction_response = pending_transaction_info(tx_id)

            if format_finish is not None:
                log(
                    f"Finished {func.__name__} with: ",
                    format_finish(transaction_response),
                )
            else:
                log(f"Finished {func.__name__}")

            if return_fn is not None:
                return return_fn(transaction_response)
            else:
                return None

        return wrapped

    return decorator


# The return type is `int` modified by `return_fn`
@transaction_boilerplate(
    format_finish=lambda txinfo: f'app-id={txinfo["application-index"]}',
    return_fn=lambda txinfo: txinfo["application-index"],
)
def create_app(
    owner: AlgoUser,
    approval_compiled: bytes,
    clear_compiled: bytes,
    global_schema: transaction.StateSchema,
    local_schema: transaction.StateSchema,
    params: Optional[transaction.SuggestedParams],
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Deploy a smart contract from the supplied details.

    Parameters
    ----------
    owner
        The user who will be the creator and owner of the smart contract.
    approval_compiled
        The TEAL compiled binary code of the approval program.
    clear_compiled
        The TEAL compiled binary code of the clear program.
    global_schema
        The global state schema details.
    local_schema
        The local state schema details.
    params
        Transaction parameters to use when sending the ``ApplicationCreateTxn`` into the Algorand network.

    Returns
    -------
    int
        The application ID of the deployed smart contract.
    """
    # Declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # Create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        owner.address,
        params,
        on_complete,
        approval_compiled,
        clear_compiled,
        global_schema,
        local_schema,
    )

    return owner, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def delete_app(
    owner: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Delete a deployed smart contract.

    Parameters
    ----------
    owner
        The creator of the smart contract
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationDeleteTxn`` into the Algorand network.

    Returns
    -------
    None
    """
    txn = transaction.ApplicationDeleteTxn(owner.address, params, app_id)
    return owner, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def update_app(
    owner: AlgoUser,
    app_id: int,
    approval_compiled: bytes,
    clear_compiled: bytes,
    params: Optional[transaction.SuggestedParams],
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Update a deployed smart contract.

    Parameters
    ----------
    owner
        The creator of the smart contract
    app_id
        The application ID of the deployed smart contract.
    approval_compiled
        The TEAL compiled binary code of the approval program.
    clear_compiled
        The TEAL compiled binary code of the clear program.
    params
        Transaction parameters to use when sending the ``ApplicationUpdateTxn`` into the Algorand network.

    Returns
    -------
    None
    """
    txn = transaction.ApplicationUpdateTxn(
        owner.address, params, app_id, approval_compiled, clear_compiled
    )

    return owner, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def opt_in_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Opt-in to a deployed smart contract.

    Parameters
    ----------
    sender
        The account to opt-in to the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationOptInTxn`` into the Algorand network.

    Returns
    -------
    None
    """
    txn = transaction.ApplicationOptInTxn(sender.address, params, app_id)
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def close_out_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Close-out from a deployed smart contract.

    Parameters
    ----------
    sender
        The account to close-out from the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationCloseOutTxn`` into the Algorand network.

    Returns
    -------
    None
    """
    txn = transaction.ApplicationCloseOutTxn(sender.address, params, app_id)
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def clear_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Clear from a deployed smart contract.

    Parameters
    ----------
    sender
        The account to clear from the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationClearStateTxn`` into the Algorand network.

    Returns
    -------
    None
    """
    txn = transaction.ApplicationClearStateTxn(sender.address, params, app_id)
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def call_app(
    sender: AlgoUser,
    app_id: int,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[List[str]] = None,
    accounts: Optional[List[str]] = None,
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Perform an application call to a deployed smart contract.

    Parameters
    ----------
    sender
        The account to perform the application call to the smart contract.
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationNoOpTxn`` into the Algorand network.
    app_args
        Any arguments to pass along with the application call.
    accounts
        Any Algorand account addresses to pass along with the application call.

    Returns
    -------
    None
    """
    txn = transaction.ApplicationNoOpTxn(
        sender.address,
        params,
        app_id,
        app_args,
        accounts,
    )
    return sender, txn


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate()
def payment_transaction(
    sender: AlgoUser,
    receiver: AlgoUser,
    amount: int,
    *,
    params: Optional[transaction.SuggestedParams],
    close_remainder_to: AlgoUser = NullUser,
    note: str = "",
    lease: str = "",
    rekey_to: str = "",
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Perform an Algorand payment transaction.

    Parameters
    ----------
    sender
        The account to send the Algorand transaction payment.
    receiver
        The account to receive the Algorand transaction payment
    amount
        The amount of microAlgos (10e-6 Algos) to transact.
    params
        Transaction parameters to use when sending the ``PaymentTxn`` into the Algorand network.
    close_remainder_to
        An Algorand address to close any remainder to.
    note
        A note to attach along with the payment transaction.
    lease
        A unique lease where no other transaction from the same sender and same lease
        can be confirmed during the transactions valid rounds.
    rekey_to
        An Algorand address to rekey the sender to.

    Returns
    -------
    None
    """
    txn = transaction.PaymentTxn(
        sender.address,
        params,
        receiver.address,
        amount,
        close_remainder_to=close_remainder_to.address,
        note=note.encode(),
        lease=lease.encode(),
        rekey_to=rekey_to,
    )
    return sender, txn


@transaction_boilerplate(
    no_sign=True,
)
def smart_signature_transaction(
    smart_signature: bytes,
    txn: transaction.Transaction,
    params: Optional[transaction.SuggestedParams],
) -> Tuple[AlgoUser, transaction.Transaction]:
    """Write docs here: TODO!"""
    logic_txn = transaction.LogicSigTransaction(txn, smart_signature)
    return NullUser, logic_txn


def group_elem(txn_factory: Callable) -> Callable:
    def no_send_factory(
        *args: Any, **kwargs: Any
    ) -> Tuple[AlgoUser, transaction.Transaction]:
        # Disable signing and logging within the `txn_factory`
        return txn_factory(*args, __no_send=True, __no_log=True, **kwargs)

    return no_send_factory


class _GroupTxn:
    def __init__(self, transactions: List[Tuple[AlgoUser, transaction.Transaction]]):
        # Separate out the `signers` and the `txns`
        signers = [signer for signer, _ in transactions]
        txns = [txn for _, txn in transactions]

        # Save the `signers` and `txns` with the group ID set
        self.signers = signers
        self.txns = transaction.assign_group_id(txns)

    def sign(self, _: str) -> List[transaction.SignedTransaction]:
        # Sign all of the transactions
        signed_txns = []
        for signer, txn in zip(self.signers, self.txns):
            signed_txns.append(txn.sign(signer.private_key))

        return signed_txns


@transaction_boilerplate(
    no_params=True,
)
def group_transaction(
    *transactions: Tuple[AlgoUser, transaction.Transaction],
) -> Tuple[AlgoUser, _GroupTxn]:
    # The signers are already included as the first elements
    # of the tuples in `transactions`, so return the `NullUser`
    # as the signer of this group transaction
    return NullUser, _GroupTxn(list(transactions))
