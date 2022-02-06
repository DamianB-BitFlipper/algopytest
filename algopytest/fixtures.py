# So that sphinx picks up on the type aliases
from __future__ import annotations

from typing import Callable, Generator

import pytest

from .account_ops import add_standalone_account, defund_account
from .entities import AlgoUser
from .transaction_ops import create_app, delete_app
from .type_stubs import YieldFixture


@pytest.fixture()
def owner() -> YieldFixture[AlgoUser]:
    """An owner account."""
    owner = add_standalone_account()

    yield owner

    # Clean up
    defund_account(owner)


@pytest.fixture()
def user1() -> YieldFixture[AlgoUser]:
    """A user account."""
    user = add_standalone_account()

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def user2() -> YieldFixture[AlgoUser]:
    """A second user account."""
    user = add_standalone_account()

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def user3() -> YieldFixture[AlgoUser]:
    """A third user account."""
    user = add_standalone_account()

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def user4() -> YieldFixture[AlgoUser]:
    """A fourth user account."""
    user = add_standalone_account()

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def create_user() -> YieldFixture[Callable]:
    """A factory fixture to create an `AlgoUser`."""
    created_users = []

    def _create_user(funded: bool = True) -> AlgoUser:
        user = add_standalone_account(funded=funded)
        created_users.append(user)
        return user

    yield _create_user

    # Clean up by de-funding all of the `created_users`
    for user in created_users:
        defund_account(user)


@pytest.fixture()
def smart_contract_id(owner: AlgoUser) -> YieldFixture[int]:
    """A smart contract instance."""
    app_id = create_app(owner)

    # This is where the testing happens
    yield app_id

    # Clean up the smart contract
    delete_app(owner, app_id)
