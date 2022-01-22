import algosdk

from .client_ops import _initial_funds_account
from .transaction_ops import payment_transaction
from .entities import AlgoUser

## CREATING
def add_standalone_account(funded=True):
    """Create standalone account and return two-tuple of its private key and address."""
    private_key, address = algosdk.account.generate_account()
    account = AlgoUser(private_key, address)

    if funded:
        fund_account(account)

    return account

def fund_account(account, initial_funds=1_000_000_000):
    """Fund the provided `account` with `initial_funds` amount of microAlgos."""
    initial_account = _initial_funds_account()
    if initial_account is None:
        raise Exception("Initial funds weren't transferred!")

    payment_transaction(
        initial_account.private_key,
        account.address,
        initial_funds,
        note="Initial funds",
    )

def defund_account(account):
    """Return the entire balance of `account` back to the `initial_account`."""
    initial_account = _initial_funds_account()
    if initial_account is None:
        raise Exception("Initial funds weren't transferred!")

    payment_transaction(
        account.private_key,
        initial_account.address,
        0,
        note="Returning funds",
        close_remainder_to=initial_account.address,
    )
