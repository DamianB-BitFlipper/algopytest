from typing import Callable, Tuple

from algosdk.future import transaction
from pyteal import Mode

from .client_ops import compile_program
from .entities import AlgoUser
from .transaction_ops import create_app, delete_app
from .type_stubs import PyTEAL


def deploy_smart_contract(
    owner: AlgoUser,
    approval_program: PyTEAL,
    clear_program: PyTEAL,
    version: int = 5,
    local_ints: int = 0,
    local_bytes: int = 0,
    global_ints: int = 0,
    global_bytes: int = 0,
) -> Tuple[int, Callable]:
    approval_compiled = compile_program(approval_program, Mode.Application, version)
    clear_compiled = compile_program(clear_program, Mode.Application, version)
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # Deploy the smart contract
    app_id = create_app(
        owner,
        approval_compiled,
        clear_compiled,
        global_schema,
        local_schema,
    )

    def clean_up_fn() -> None:
        delete_app(owner, app_id)

    return app_id, clean_up_fn
