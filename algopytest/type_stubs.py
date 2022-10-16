import sys
from typing import Generator, TypeVar

# The `ParamSpec` does not have native support before Python v3.10
if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

# Type for PyTest fixtures which yield a fixture themselves
YieldFixture = Generator[T, None, None]
