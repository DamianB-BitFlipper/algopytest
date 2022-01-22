from dataclasses import dataclass

@dataclass
class AlgoUser:
    """A simple Algorand user storing an address and private key"""
    private_key: str
    address: str
