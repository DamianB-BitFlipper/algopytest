# So that sphinx picks up on the type aliases
from __future__ import annotations

from typing import Any, Optional

from algosdk.future import transaction
from pyteal import Mode

from .client_ops import compile_program
from .type_stubs import PyTEAL


# Namespace the global variables
class _ProgramStore:
    # Declare application state storage (immutable)
    global_schema: Optional[transaction.StateSchema] = None
    local_schema: Optional[transaction.StateSchema] = None

    # Variables to hold the compiled contracts
    approval_compiled: Optional[bytes] = None
    clear_compiled: Optional[bytes] = None

    def _populate(
        self,
        approval_program: PyTEAL,
        clear_program: PyTEAL,
        mode: Mode,
        version: int,
        local_ints: int,
        local_bytes: int,
        global_ints: int,
        global_bytes: int,
    ) -> None:
        # Set the schema variables in `self`
        self.global_schema = transaction.StateSchema(global_ints, global_bytes)
        self.local_schema = transaction.StateSchema(local_ints, local_bytes)

        # Compile the contracts
        self.approval_compiled = compile_program(approval_program, mode, version)
        self.clear_compiled = compile_program(clear_program, mode, version)


# Create an empty `_ProgramStore` instance at first
ProgramStore = _ProgramStore()


# Expose the `populate` method of `_ProgramStore`
def initialize(
    approval_program: PyTEAL,
    clear_program: PyTEAL,
    smart_signature: Optional[PyTEAL] = None,
    mode: Mode = Mode.Application,
    version: int = 5,
    local_ints: int = 0,
    local_bytes: int = 0,
    global_ints: int = 0,
    global_bytes: int = 0,
) -> None:
    """Initialize AlgoPytest with the Algorand Smart Contract/Signature to be tested.

    Initialization must occur before any Pytest test run. This is most easily achieved
    by creating a file named ``conftest.py`` and calling ``initialize`` from within a
    function named ``pytest_configure``.

    Example
    -------
    .. code-block:: python

        # File: conftets.py
        def pytest_configure(config):
            initialize(approval_program=diploma_program,
                       clear_program=clear_program,
                       local_bytes=1, global_bytes=1)

    Parameters
    ----------
    approval_program
        A function which generates the approval program of the smart contract as a PyTEAL expression.
    clear_program
        A function which generates the clear program of the smart contract as a PyTEAL expression.
    smart_signature
        Note: Not supported yet! A function which generates the smart signature as a PyTEAL expression.
    mode
        The mode with which to compile the supplied PyTEAL programs.
    version
        The version with which to compile the supplied PyTEAL programs.
    local_ints
        The local state integers schema count.
    local_bytes
        The local state bytes schema count.
    global_ints
        The global state integers schema count.
    global_bytes
        The global state bytes schema count.
    """

    # Sanity check that either both `approval_program`
    # and `clear_program` are set or `smart_signature`
    # assert (approval_program is not None and clear_program is not None) or (
    #    smart_signature is not None
    # )

    # TODO
    if smart_signature is not None:
        raise NotImplementedError("Smart signature testing to be implemented!")

    # Populate the `ProgramStore` with the appropriate values
    ProgramStore._populate(
        approval_program,
        clear_program,
        mode,
        version,
        local_ints,
        local_bytes,
        global_ints,
        global_bytes,
    )
