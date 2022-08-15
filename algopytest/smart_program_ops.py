from typing import Callable, Tuple

from algosdk.future import transaction
from pyteal import Mode

from .client_ops import compile_program
from .entities import AlgoUser
from .transaction_ops import create_app, delete_app
from .type_stubs import PyTEAL


class DeployedSmartContract:
    def __init__(self, owner: AlgoUser, app_id: int):
        self.owner = owner
        self.app_id = app_id

    def __enter__(self):
        return self.app_id

    def __exit__(self, exc_type, exc_value, exc_traceback):
        delete_app(self.owner, self.app_id)


def deploy_smart_contract(
    owner: AlgoUser,
    approval_program: PyTEAL,
    clear_program: PyTEAL,
    version: int = 5,
    local_ints: int = 0,
    local_bytes: int = 0,
    global_ints: int = 0,
    global_bytes: int = 0,
) -> DeployedSmartContract:
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

    return DeployedSmartContract(owner, app_id)
