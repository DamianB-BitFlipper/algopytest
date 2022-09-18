import os
from typing import Optional


# Namespace the global variables
class _ConfigParams:
    # Default client specific parameters
    algod_address: str = "http://localhost:4001"
    algod_token: str = (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )

    indexer_address: str = "http://localhost:8980"
    indexer_token: str = ""

    kmd_address: str = "http://localhost:4002"
    kmd_token: str = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    kmd_wallet_name: str = "unencrypted-default-wallet"
    kmd_wallet_password: str = ""

    initial_funds_account: Optional[str] = None

    # Timeout to use when querying the indexer, in seconds
    indexer_timeout: int = 61

    def __init__(self) -> None:
        # Overwrite any of the parameters if environment variables are set
        self.algod_address = os.environ.get("ALGOD_ADDRESS") or self.algod_address
        self.algod_token = os.environ.get("ALGOD_TOKEN") or self.algod_token
        self.indexer_address = os.environ.get("INDEXER_ADDRESS") or self.indexer_address
        self.indexer_token = os.environ.get("INDEXER_TOKEN") or self.indexer_token
        self.kmd_address = os.environ.get("KMD_ADDRESS") or self.kmd_address
        self.kmd_token = os.environ.get("KMD_TOKEN") or self.kmd_token
        self.kmd_wallet_name = os.environ.get("KMD_WALLET_NAME") or self.kmd_wallet_name
        self.kmd_wallet_password = (
            os.environ.get("KMD_WALLET_PASSWORD") or self.kmd_wallet_password
        )
        self.initial_funds_account = (
            os.environ.get("INITIAL_FUNDS_ACCOUNT") or self.initial_funds_account
        )

        # Convert the `INDEXER_TIMEOUT` to an `int` if it exists
        env_indexer_timeout = os.environ.get("INDEXER_TIMEOUT")
        if env_indexer_timeout is not None:
            self.indexer_timeout = int(env_indexer_timeout)


ConfigParams = _ConfigParams()
