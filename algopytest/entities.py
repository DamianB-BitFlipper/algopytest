from dataclasses import dataclass
from typing import List, Optional

from algosdk.future import transaction as algosdk_transaction


@dataclass
class AlgoUser:
    """A simple Algorand user storing an address and private key."""

    address: str
    private_key: Optional[str] = None


NullUser = AlgoUser(address="")


class MultisigAccount(AlgoUser):
    """An Algorand user subclass representing a multi-signature account."""

    def __init__(self, version: int, threshold: int, owner_accounts: List[AlgoUser]):
        # Save the passed in values privately
        self._version = version
        self._threshold = threshold
        self._owner_accounts = owner_accounts

        # Instantiate the super `AlgoUser` class
        super().__init__(address=self.attributes.address())

    @property
    def attributes(self) -> algosdk_transaction.Multisig:
        # Return a fresh `Multisig` object every time `self.attributes` is called.
        # This is because if the attributes are used to sign a `MultisigTransaction`,
        # they may no longer be reused to sign a different `MultisigTransaction`
        owners_pub_keys = [owner.address for owner in self._owner_accounts]
        return algosdk_transaction.Multisig(
            self._version, self._threshold, owners_pub_keys
        )
