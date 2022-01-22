from algosdk.future import transaction
from algosdk import account

from .client_ops import (
    suggested_params,
    process_transactions,
    pending_transaction_info,
)

def transaction_boilerplate(private_key_argidx, format_finish=None, return_fn=None):
    """A decorator to handle all of the transaction boilerplate."""
    def decorator(func):
        """The actual decorator since it takes the arguments above."""
        def wrapped(*args, **kwargs):
            print(f"Running {func.__name__}")

            # Extract the private key from the function arguments
            sender_private_key = args[private_key_argidx]

            # Define sender as creator
            sender = account.address_from_private_key(sender_private_key)

            # Get node suggested parameters
            params = suggested_params()
            params.flat_fee = True
            params.fee = 1000

            # Augment the `kwargs` with the `sender` and `params`
            kwargs['_sender'] = sender
            kwargs['_params'] = params

            # Create unsigned transaction
            txn = func(*args, **kwargs)

            # Sign transaction
            signed_txn = txn.sign(sender_private_key)

            # Send the transaction and await for confirmation
            tx_id = process_transactions([signed_txn])

            # Display results
            transaction_response = pending_transaction_info(tx_id)

            if format_finish is not None:
                print(f"Finished {func.__name__} with: ", 
                      format_finish(transaction_response))
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
    private_key_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["application-index"]}',
    return_fn=lambda txinfo: txinfo["application-index"],
)
def create_app(owner_private_key, 
               approval_program, clear_program, 
               global_schema, local_schema,
               _sender, _params): 
    # Declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real           

    # Create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        _sender, _params, on_complete, \
        approval_program, clear_program, \
        global_schema, local_schema)

    return txn

# Delete application
@transaction_boilerplate(
    private_key_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def delete_app(owner_private_key, app_id,
               _sender, _params):
    return transaction.ApplicationDeleteTxn(_sender, _params, app_id)

# Update existing application
@transaction_boilerplate(
    private_key_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def update_app(owner_private_key, app_id, 
               approval_program, clear_program,
               _sender, _params): 
    return transaction.ApplicationUpdateTxn(
        _sender, _params, app_id, \
        approval_program, clear_program
    )

# Opt-in to application
@transaction_boilerplate(
    private_key_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def opt_in_app(sender_private_key, app_id,
               _sender, _params): 
    return transaction.ApplicationOptInTxn(_sender, _params, app_id)

# Close out from application
@transaction_boilerplate(
    private_key_argidx=0,
    format_finish=lambda txinfo: f'app-id={txinfo["txn"]["txn"]["apid"]}',
)
def close_out_app(sender_private_key, app_id,
                  _sender, _params): 
    return transaction.ApplicationCloseOutTxn(_sender, _params, app_id)

# Send a payment transaction
@transaction_boilerplate(
    private_key_argidx=0,
)
def payment_transaction(sender_private_key, receiver, amount,
                        _sender, _params, note="", close_remainder_to=""):
    return transaction.PaymentTxn(
        _sender, 
        _params,
        receiver,
        amount,
        note=note.encode(),
        close_remainder_to=close_remainder_to,
    )
