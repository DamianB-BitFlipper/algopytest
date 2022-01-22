import algosdk

from .client_ops import _initial_funds_account
from .transaction_ops import payment_transaction
from .entities import AlgoUser

## CREATING
def add_standalone_account(funded=True):
    """Create standalone account and return two-tuple of its private key and address."""
    private_key, address = algosdk.account.generate_account()
    account = AlgoUser(address, private_key)

    if funded:
        fund_account(account)

    return account

def fund_account(receiving_account, initial_funds=1_000_000_000):
    """Fund the `receiving_account` with `initial_funds` amount of microAlgos."""
    initial_account = _initial_funds_account()
    if initial_account is None:
        raise Exception("Initial funds weren't transferred!")

    payment_transaction(
        initial_account,
        receiving_account,
        initial_funds,
        note="Initial funds",
    )

def defund_account(defunding_account):
    """Return the entire balance of `defunding_account` back to the `initial_account`."""
    initial_account = _initial_funds_account()
    if initial_account is None:
        raise Exception("Initial funds weren't transferred!")

    payment_transaction(
        defunding_account,
        initial_account,
        0,
        note="Returning funds",
        close_remainder_to=initial_account,
    )
