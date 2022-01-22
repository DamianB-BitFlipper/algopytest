import os
from pathlib import Path

from algosdk.future import transaction
from pyteal import Mode

# Namespace the global variables
class _Inits:
    # Default client specific parameters
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    indexer_address = "http://localhost:8980"
    indexer_token = ""

    # Assume that the sandbox is the sibling directory of this project
    sandbox_dir = Path('.').resolve().parent / "sandbox"

    # Timeout to use when querying the indexer, in seconds
    indexer_timeout = 61

    # Declare application state storage (immutable)
    global_schema = None
    local_schema = None

    # Variables to hold the compiled contracts
    approval_compiled = None
    clear_compiled = None

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

    def _initialize(self, approval_program, clear_program, 
                    mode, version,
                    local_ints, local_bytes, 
                    global_ints, global_bytes):
        # TODO: Split this class into `_ConfigParams` and `_ContractStore`
        from .client_ops import compile_program

        # Set the schema variables in `self`
        self.global_schema = transaction.StateSchema(global_ints, global_bytes)
        self.local_schema = transaction.StateSchema(local_ints, local_bytes)
        
        # Compile the contracts
        self.approval_compiled = compile_program(approval_program, mode, version)
        self.clear_compiled = compile_program(clear_program, mode, version)

Inits = _Inits()

# Expose the `_initialize` method of `_Inits`
def initialize(approval_program=None, clear_program=None, 
               smart_signature=None, mode=Mode.Application, 
               version=5,local_ints=0, local_bytes=0, 
               global_ints=0, global_bytes=0):
    # Sanity check that either both `approval_program` 
    # and `clear_program` are set or `smart_signature`
    assert(
        (approval_program is not None and clear_program is not None) or 
        (smart_signature is not None)
    )

    return Inits._initialize(approval_program, clear_program,
                             mode, version, 
                             local_ints, local_bytes,
                             global_ints, global_bytes)
