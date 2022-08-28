from typing import Generator, TypeVar

# Type for PyTest fixtures which yield a fixture themselves
T = TypeVar("T")
YieldFixture = Generator[T, None, None]
