from dataclasses import dataclass
from typing import Optional


@dataclass
class AlgoUser:
    """A simple Algorand user storing an address and private key"""

    address: str
    private_key: Optional[str] = None


NullUser = AlgoUser(address="")
