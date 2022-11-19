from types import TracebackType
from typing import List, Optional, Type, Union

import pyteal
import typing_extensions
from algosdk.future import transaction as algosdk_transaction
from pyteal import Mode

from .client_ops import compile_program
from .entities import AlgoUser
from .transaction_ops import create_app, delete_app


class DeployedSmartContractID(int):
    """Subclass the `int` so that it can be used as a context manager or directly."""

    owner: AlgoUser

    def __new__(cls, app_id: int, owner: AlgoUser):
        _app_id = int.__new__(cls, app_id)
        _app_id.owner = owner
        return _app_id

    def __enter__(self) -> int:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> typing_extensions.Literal[False]:
        delete_app(self.owner, self)
        return False


def deploy_smart_contract(
    owner: AlgoUser,
    approval_program: pyteal.Expr,
    clear_program: pyteal.Expr,
    version: int = 5,
    local_ints: int = 0,
    local_bytes: int = 0,
    global_ints: int = 0,
    global_bytes: int = 0,
    *,
    app_args: Optional[List[Union[str, int]]] = None,
    accounts: Optional[List[AlgoUser]] = None,
    foreign_apps: Optional[List[int]] = None,
    foreign_assets: Optional[List[int]] = None,
    note: str = "",
    lease: str = "",
    rekey_to: Optional[AlgoUser] = None,
    extra_pages: int = 0,
) -> int:
    approval_compiled = compile_program(approval_program, Mode.Application, version)
    clear_compiled = compile_program(clear_program, Mode.Application, version)
    global_schema = algosdk_transaction.StateSchema(global_ints, global_bytes)
    local_schema = algosdk_transaction.StateSchema(local_ints, local_bytes)

    # Deploy the smart contract
    app_id = create_app(
        owner,
        approval_compiled,
        clear_compiled,
        global_schema,
        local_schema,
        app_args=app_args,
        accounts=accounts,
        foreign_apps=foreign_apps,
        foreign_assets=foreign_assets,
        note=note,
        lease=lease,
        rekey_to=rekey_to,
        extra_pages=extra_pages,
    )

    return DeployedSmartContractID(app_id, owner)
