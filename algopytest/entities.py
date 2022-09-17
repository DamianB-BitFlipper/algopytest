from dataclasses import dataclass
from typing import Optional, List

from algosdk.future import transaction


@dataclass
class AlgoUser:
    """A simple Algorand user storing an address and private key."""

    address: str
    private_key: Optional[str] = None


NullUser = AlgoUser(address="")


class MultisigAccount(AlgoUser):
    """An Algorand user subclass representing a multi-signature account."""

    def __init__(self, version: int, threshold: int, owner_accounts: List[AlgoUser]):
        # Create the multisig attributes relating to the multisig account
        owners_pub_keys = [owner.address for owner in owner_accounts]
        self.attributes = transaction.Multisig(version, threshold, owners_pub_keys)

        # Instantiate the super `AlgoUser` class 
        super().__init__(address=self.attributes.address())
