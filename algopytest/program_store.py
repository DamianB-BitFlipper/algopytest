# So that sphinx picks up on the type aliases
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from algosdk.future import transaction
from pyteal import Mode

from .client_ops import compile_program
from .type_stubs import PyTEAL


@dataclass
class _SmartContract:
    # Variables to hold the compiled contracts
    approval_compiled: bytes
    clear_compiled: bytes

    # Declare application state storage (immutable)
    global_schema: transaction.StateSchema
    local_schema: transaction.StateSchema


# Namespace the global variables
class _ProgramsStore:
    # TODO: Support smart signatures as well
    programs: Dict[str, _SmartContract]

    def __init__(self) -> None:
        self.programs = {}

    def _register_smart_contract(
        self,
        name: str,
        approval_program: PyTEAL,
        clear_program: PyTEAL,
        mode: Mode,
        version: int,
        local_ints: int,
        local_bytes: int,
        global_ints: int,
        global_bytes: int,
    ) -> None:
        # Sanity check that `name` has not already been registered
        if name in self.programs:
            raise ValueError(f"Smart contract with name: '{name}' already registered")

        program = _SmartContract(
            approval_compiled=compile_program(approval_program, mode, version),
            clear_compiled=compile_program(clear_program, mode, version),
            global_schema=transaction.StateSchema(global_ints, global_bytes),
            local_schema=transaction.StateSchema(local_ints, local_bytes),
        )
        self.programs[name] = program


# Create an empty `_ProgramsStore` instance at first
ProgramsStore = _ProgramsStore()


# Expose the `populate` method of `_ProgramsStore`
def register_smart_contract(
    name: str,
    approval_program: PyTEAL,
    clear_program: PyTEAL,
    mode: Mode = Mode.Application,
    version: int = 5,
    local_ints: int = 0,
    local_bytes: int = 0,
    global_ints: int = 0,
    global_bytes: int = 0,
) -> None:
    """Register an Algorand Smart Contract/Signature with AlgoPytest to be tested.

    Registration must occur before any Pytest test run. This is most easily achieved
    by creating a file named ``conftest.py`` and calling ``initialize`` from within a
    function named ``pytest_configure``.

    Example
    -------
    .. code-block:: python

        # File: conftets.py
        def pytest_configure(config):
            register_smart_contract(
                name="diploma_contract",
                approval_program=diploma_program,
                clear_program=clear_program,
                local_bytes=1,
                global_bytes=1
            )

    Parameters
    ----------
    approval_program
        A function which generates the approval program of the smart contract as a PyTEAL expression.
    clear_program
        A function which generates the clear program of the smart contract as a PyTEAL expression.
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
    # Populate the `ProgramsStore` with the appropriate values
    ProgramsStore._register_smart_contract(
        name,
        approval_program,
        clear_program,
        mode,
        version,
        local_ints,
        local_bytes,
        global_ints,
        global_bytes,
    )


def register_smart_signature(
    name: str,
    smart_signature: Optional[PyTEAL] = None,
) -> None:
    """Make this work: TODO"""
    raise NotImplementedError("Smart signature testing to be implemented!")
