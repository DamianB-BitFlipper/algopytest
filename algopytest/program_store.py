from algosdk.future import transaction
from pyteal import Mode

from .client_ops import compile_program

# Namespace the global variables
class _ProgramStore:
    # Declare application state storage (immutable)
    global_schema = None
    local_schema = None

    # Variables to hold the compiled contracts
    approval_compiled = None
    clear_compiled = None    

    def _populate(self, approval_program, clear_program, 
                  mode, version,
                  local_ints, local_bytes, 
                  global_ints, global_bytes):
        # Set the schema variables in `self`
        self.global_schema = transaction.StateSchema(global_ints, global_bytes)
        self.local_schema = transaction.StateSchema(local_ints, local_bytes)
        
        # Compile the contracts
        self.approval_compiled = compile_program(approval_program, mode, version)
        self.clear_compiled = compile_program(clear_program, mode, version)

# Create an empty `_ProgramStore` instance at first
ProgramStore = _ProgramStore()

# Expose the `populate` method of `_ProgramStore`
def initialize(approval_program=None, clear_program=None, 
               smart_signature=None, mode=Mode.Application, 
               version=5, local_ints=0, local_bytes=0, 
               global_ints=0, global_bytes=0):
    # Sanity check that either both `approval_program` 
    # and `clear_program` are set or `smart_signature`
    assert(
        (approval_program is not None and clear_program is not None) or 
        (smart_signature is not None)
    )

    # Populate the `ProgramStore` with the appropriate values
    ProgramStore._populate(approval_program, clear_program,
                           mode, version, 
                           local_ints, local_bytes,
                           global_ints, global_bytes)
