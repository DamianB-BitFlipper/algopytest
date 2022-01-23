from typing import Callable, Generator, TypeVar

import pyteal

from .entities import AlgoUser

# Alias the type for a PyTEAL program
PyTEAL = Callable[[], pyteal.Expr]

T = TypeVar("T")
YieldFixture = Generator[T, None, None]
