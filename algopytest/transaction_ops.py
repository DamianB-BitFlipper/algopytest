from functools import wraps
from typing import Any, Callable, Optional

from algosdk import account
from algosdk.future import transaction

from .client_ops import pending_transaction_info, process_transactions, suggested_params
from .entities import AlgoUser, NullUser
from .program_store import ProgramStore
from .type_stubs import PyTEAL


def transaction_boilerplate(
    sender_account_argidx: int,
    format_finish: Optional[Callable] = None,
    return_fn: Optional[Callable] = None,
) -> Callable:
    """A decorator to handle all of the transaction boilerplate."""

    def decorator(func: Callable) -> Callable:
        """The actual decorator since it takes the arguments above."""

        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            print(f"Running {func.__name__}")

            # Extract the account from the function arguments
            sender = args[sender_account_argidx]

            # If `params` was not supplied, insert the suggested parameters
            if "params" not in kwargs or kwargs["params"] is None:
                kwargs["params"] = suggested_params(flat_fee=True, fee=1000)

            # Create unsigned transaction
            txn = func(*args, **kwargs)

            # Sign transaction
            signed_txn = txn.sign(sender.private_key)

            # Send the transaction and await for confirmation
            tx_id = process_transactions([signed_txn])

            # Display results
            transaction_response = pending_transaction_info(tx_id)

            if format_finish is not None:
                print(
                    f"Finished {func.__name__} with: ",
                    format_finish(transaction_response),
                )
            else:
                print(f"Finished {func.__name__}")

            if return_fn is not None:
                return return_fn(transaction_response)
            else:
                return None

        return wrapped

    return decorator


# The return type is `int` modified by `return_fn`
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["application-index"]}',
    return_fn=lambda txinfo: txinfo["application-index"],
)
def create_custom_app(
    owner: AlgoUser,
    approval_compiled: bytes,
    clear_compiled: bytes,
    global_schema: transaction.StateSchema,
    local_schema: transaction.StateSchema,
    params: Optional[transaction.SuggestedParams],
) -> transaction.Transaction:
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

    return txn


def create_app(owner: AlgoUser) -> int:
    """Deploy the smart contract from the details supplied during initialization of `AlgoPytest`.

    Parameters
    ----------
    owner
        The user who will be the creator and owner of the smart contract.

    Returns
    -------
    int
        The application ID of the deployed smart contract.
    """
    return create_custom_app(
        owner,
        ProgramStore.approval_compiled,
        ProgramStore.clear_compiled,
        ProgramStore.global_schema,
        ProgramStore.local_schema,
    )


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def delete_app(
    owner: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
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
    return transaction.ApplicationDeleteTxn(owner.address, params, app_id)


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def update_app(
    owner: AlgoUser,
    app_id: int,
    params: Optional[transaction.SuggestedParams],
    approval_compiled: Optional[bytes] = None,
    clear_compiled: Optional[bytes] = None,
) -> transaction.Transaction:
    """Update a deployed smart contract.

    Parameters
    ----------
    owner
        The creator of the smart contract
    app_id
        The application ID of the deployed smart contract.
    params
        Transaction parameters to use when sending the ``ApplicationUpdateTxn`` into the Algorand network.
    approval_compiled
        The TEAL compiled binary code of the approval program.
    clear_compiled
        The TEAL compiled binary code of the clear program.

    Returns
    -------
    None
    """
    # Use the values in `ProgramStore` if the programs are set to `None`
    approval_compiled = approval_compiled or ProgramStore.approval_compiled
    clear_compiled = clear_compiled or ProgramStore.clear_compiled

    return transaction.ApplicationUpdateTxn(
        owner.address, params, app_id, approval_compiled, clear_compiled
    )


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def opt_in_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
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
    return transaction.ApplicationOptInTxn(sender.address, params, app_id)


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def close_out_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
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
    return transaction.ApplicationCloseOutTxn(sender.address, params, app_id)


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def clear_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
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
    return transaction.ApplicationClearStateTxn(sender.address, params, app_id)


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def call_app(
    sender: AlgoUser,
    app_id: int,
    params: Optional[transaction.SuggestedParams],
    app_args: Optional[list[str]] = None,
    accounts: Optional[list[str]] = None,
) -> transaction.Transaction:
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
    return transaction.ApplicationNoOpTxn(
        sender.address,
        params,
        app_id,
        app_args,
        accounts,
    )


# Returns `None` because of the `transaction_boilerplate` decorator
@transaction_boilerplate(
    sender_account_argidx=0,
)
def payment_transaction(
    sender: AlgoUser,
    receiver: AlgoUser,
    amount: int,
    params: Optional[transaction.SuggestedParams],
    note: str = "",
    close_remainder_to: AlgoUser = NullUser,
) -> transaction.Transaction:
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
    note
        A note to attach along with the payment transaction.
    close_remainder_to
        An Algorand address to close any remainder to.

    Returns
    -------
    None
    """
    return transaction.PaymentTxn(
        sender.address,
        params,
        receiver.address,
        amount,
        note=note.encode(),
        close_remainder_to=close_remainder_to.address,
    )
