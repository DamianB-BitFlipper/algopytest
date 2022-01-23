from typing import Callable

import pyteal

# Alias the type for a PyTEAL program
PyTEAL = Callable[[], pyteal.Expr]
