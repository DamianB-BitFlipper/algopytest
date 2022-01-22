import os
from pathlib import Path

# Namespace the global variables
class _ConfigParams:
    # Default client specific parameters
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    indexer_address = "http://localhost:8980"
    indexer_token = ""

    # Assume that the sandbox is the sibling directory of this project
    sandbox_dir = Path('.').resolve().parent / "sandbox"

    # Timeout to use when querying the indexer, in seconds
    indexer_timeout = 61

    def __init__(self):
        # Overwrite any of the parameters if environment variables are set
        self.algod_address = os.environ.get("ALGOD_ADDRESS") or self.algod_address
        self.algod_token = os.environ.get("ALGOD_TOKEN") or self.algod_token
        self.indexer_address = os.environ.get("INDEXER_ADDRESS") or self.indexer_address
        self.indexer_token = os.environ.get("INDEXER_TOKEN") or self.indexer_token

        # Convert the `SANDBOX_DIR` to a pathlib.Path if it exists
        env_sandbox_dir = os.environ.get("SANDBOX_DIR")
        if env_sandbox_dir is not None:
            self.sandbox_dir = Path(env_sandbox_dir)

        # Convert the `INDEXER_TIMEOUT` to an int if it exists
        env_indexer_timeout = os.environ.get("INDEXER_TIMEOUT")
        if env_indexer_timeout is not None:
            self.indexer_timeout = int(env_indexer_timeout)

ConfigParams = _ConfigParams()
