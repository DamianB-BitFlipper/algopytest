from dataclasses import dataclass


@dataclass
class AlgoUser:
    """A simple Algorand user storing an address and private key"""

    address: str
    private_key: str = ""


NullUser = AlgoUser(address="")
