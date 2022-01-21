import os
from pathlib import Path

from algosdk.future import transaction
from pyteal import Mode, compileTeal

# Namespace the global variables
class _Inits:
    # Default client specific parameters
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    indexer_address = "http://localhost:8980"
    indexer_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    # Assume that the sandbox is the sibling directory of this project
    sandbox_dir = Path(__file__).resolve().parent.parent / "sandbox"

    # Timeout to use when querying the indexer, in seconds
    indexer_timeout = 10

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

        self.sandbox_dir = os.environ.get("SANDBOX_DIR") or self.sandbox_dir
        self.indexer_timeout = os.environ.get("INDEXER_TIMEOUT") or self.indexer_timeout

    def _initialize(self, approval_program, clear_program, 
                    mode, version,
                    local_ints, local_bytes, 
                    global_ints, global_bytes):
        # Set the schema variables in `self`
        self.global_schema = transaction.StateSchema(global_ints, global_bytes)
        self.local_schema = transaction.StateSchema(local_ints, local_bytes)
        
        # Compile the contracts
        self.approval_compiled = compile_program(approval_program, mode, version)
        self.clear_compiled = compile_program(clear_program, mode, version)

Inits = _Inits()

# Expose the `_initialize` method of `_Inits`
def initialize(approval_program, clear_program, 
               mode=Mode.Application, version=5,
               local_ints=0, local_bytes=0, 
               global_ints=0, global_bytes=0):
    return Inits._initialize(approval_program, clear_program,
                             mode, version, 
                             local_ints, local_bytes,
                             global_ints, global_bytes)
