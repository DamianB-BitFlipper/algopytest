from typing import Callable, Generator, TypeVar

import pyteal

from .entities import AlgoUser

# Type for a PyTEAL program
# PyTEAL = Callable[[], pyteal.Expr]
PyTEAL = pyteal.Expr

# Type for PyTest fixtures which yield a fixture themselves
T = TypeVar("T")
YieldFixture = Generator[T, None, None]
