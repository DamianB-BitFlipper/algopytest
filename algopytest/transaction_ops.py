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


# Create new application
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


def create_app(owner: AlgoUser) -> transaction.Transaction:
    """Set up the smart contract using the details in ``ProgramStore``."""
    return create_custom_app(
        owner,
        ProgramStore.approval_compiled,
        ProgramStore.clear_compiled,
        ProgramStore.global_schema,
        ProgramStore.local_schema,
    )


# Delete application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def delete_app(
    owner: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
    return transaction.ApplicationDeleteTxn(owner.address, params, app_id)


# Update existing application
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
    # Use the values in `ProgramStore` if the programs are set to `None`
    approval_compiled = approval_compiled or ProgramStore.approval_compiled
    clear_compiled = clear_compiled or ProgramStore.clear_compiled

    return transaction.ApplicationUpdateTxn(
        owner.address, params, app_id, approval_compiled, clear_compiled
    )


# Opt-in to application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def opt_in_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
    return transaction.ApplicationOptInTxn(sender.address, params, app_id)


# Close out from application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def close_out_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
    return transaction.ApplicationCloseOutTxn(sender.address, params, app_id)


# Clear from the application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def clear_app(
    sender: AlgoUser, app_id: int, params: Optional[transaction.SuggestedParams]
) -> transaction.Transaction:
    return transaction.ApplicationClearStateTxn(sender.address, params, app_id)


# Perform an application call
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
    return transaction.ApplicationNoOpTxn(
        sender.address,
        params,
        app_id,
        app_args,
        accounts,
    )


# Send a payment transaction
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
    return transaction.PaymentTxn(
        sender.address,
        params,
        receiver.address,
        amount,
        note=note.encode(),
        close_remainder_to=close_remainder_to.address,
    )
