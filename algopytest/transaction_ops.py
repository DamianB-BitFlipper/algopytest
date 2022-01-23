from typing import Any, Callable, Optional

from algosdk import account
from algosdk.future import transaction

from .client_ops import pending_transaction_info, process_transactions, suggested_params
from .entities import AlgoUser, NullUser
from .type_stubs import PyTEAL


def transaction_boilerplate(
    sender_account_argidx: int,
    format_finish: Optional[Callable] = None,
    return_fn: Optional[Callable] = None,
) -> Callable:
    """A decorator to handle all of the transaction boilerplate."""

    def decorator(func: Callable) -> Callable:
        """The actual decorator since it takes the arguments above."""

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            print(f"Running {func.__name__}")

            # Extract the account from the function arguments
            sender = args[sender_account_argidx]

            # Get node suggested parameters
            params = suggested_params()
            params.flat_fee = True
            params.fee = 1000

            # Augment the `kwargs` with the suggested `params`
            kwargs["_params"] = params

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
def create_app(
    owner: AlgoUser,
    approval_program: PyTEAL,
    clear_program: PyTEAL,
    global_schema: transaction.StateSchema,
    local_schema: transaction.StateSchema,
    _params: transaction.SuggestedParams,
) -> transaction.Transaction:
    # Declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # Create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        owner.address,
        _params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    return txn


# Delete application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def delete_app(
    owner: AlgoUser, app_id: int, _params: transaction.SuggestedParams
) -> transaction.Transaction:
    return transaction.ApplicationDeleteTxn(owner.address, _params, app_id)


# Update existing application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def update_app(
    owner: AlgoUser,
    app_id: int,
    approval_program: PyTEAL,
    clear_program: PyTEAL,
    _params: transaction.SuggestedParams,
) -> transaction.Transaction:
    return transaction.ApplicationUpdateTxn(
        owner.address, _params, app_id, approval_program, clear_program
    )


# Opt-in to application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def opt_in_app(
    sender: AlgoUser, app_id: int, _params: transaction.SuggestedParams
) -> transaction.Transaction:
    return transaction.ApplicationOptInTxn(sender.address, _params, app_id)


# Close out from application
@transaction_boilerplate(
    sender_account_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def close_out_app(
    sender: AlgoUser, app_id: int, _params: transaction.SuggestedParams
) -> transaction.Transaction:
    return transaction.ApplicationCloseOutTxn(sender.address, _params, app_id)


# Send a payment transaction
@transaction_boilerplate(
    sender_account_argidx=0,
)
def payment_transaction(
    sender: AlgoUser,
    receiver: AlgoUser,
    amount: int,
    _params: transaction.SuggestedParams,
    note: str = "",
    close_remainder_to: AlgoUser = NullUser,
) -> transaction.Transaction:
    return transaction.PaymentTxn(
        sender.address,
        _params,
        receiver.address,
        amount,
        note=note.encode(),
        close_remainder_to=close_remainder_to.address,
    )
