import sys
from typing import TYPE_CHECKING, Generator, TypeVar, Union

import algosdk.transaction

# The `ParamSpec` does not have native support before Python v3.10
if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

if TYPE_CHECKING:
    from .transaction_ops import _GroupTxn, _MultisigTxn

P = ParamSpec("P")
T = TypeVar("T")

# Type for PyTest fixtures which yield a fixture themselves
YieldFixture = Generator[T, None, None]

TransactionT = Union[
    algosdk.transaction.Transaction,
    algosdk.transaction.LogicSigTransaction,
    "_MultisigTxn",
    "_GroupTxn",
]
