# So that sphinx picks up on the type aliases
from __future__ import annotations

from typing import Callable, Optional

import pytest
from pyteal import Mode

from .account_ops import add_standalone_account, defund_account
from .client_ops import compile_program
from .entities import AlgoUser
from .transaction_ops import create_app, delete_app
from .type_stubs import YieldFixture


@pytest.fixture()
def owner() -> YieldFixture[AlgoUser]:
    """A funded owner account.

    This is a regular Algorand account that is automatically funded upon creation.
    Its name implies that its main purpose is as the creator and administrator
    account of an Algorand smart contract application.

    Yields
    ------
    AlgoUser
    """
    owner = add_standalone_account(name="owner")

    yield owner

    # Clean up
    defund_account(owner)


@pytest.fixture()
def user1() -> YieldFixture[AlgoUser]:
    """A funded user account.

    This is an Algorand account that is automatically funded upon creation.

    Yields
    ------
    AlgoUser
    """
    user = add_standalone_account(name="user1")

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def user2() -> YieldFixture[AlgoUser]:
    """A second funded user account.

    This is an Algorand account that is automatically funded upon creation.

    Yields
    ------
    AlgoUser
    """
    user = add_standalone_account(name="user2")

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def user3() -> YieldFixture[AlgoUser]:
    """A third funded user account.

    This is an Algorand account that is automatically funded upon creation.

    Yields
    ------
    AlgoUser
    """
    user = add_standalone_account(name="user3")

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def user4() -> YieldFixture[AlgoUser]:
    """A fourth funded user account.

    This is an Algorand account that is automatically funded upon creation.

    Yields
    ------
    AlgoUser
    """
    user = add_standalone_account(name="user4")

    yield user

    # Clean up
    defund_account(user)


@pytest.fixture()
def create_user() -> YieldFixture[Callable]:
    """A factory fixture to create funded user accounts.

    Every time this factory fixture is called, a new funded Algorand account is created.

    Example
    -------
    .. code-block:: python

        def test_vote_from_many_users(smart_contract_id, create_user):
            users = []

            # Create 10 separate users
            for i in range(10):
                users.append(create_user())

            # Everyone votes for the first user
            for user in users:
                call_app(user, smart_contract_id, app_args=[\"vote\"], accounts=[user[0]])

    Yields
    ------
    Callable[[], AlgoUser]
        A function taking no arguments and producing an ``AlgoUser``.
    """
    created_users = []

    def _create_user(funded: bool = True, name: Optional[str] = None) -> AlgoUser:
        user = add_standalone_account(funded=funded, name=name)
        created_users.append(user)
        return user

    yield _create_user

    # Clean up by de-funding all of the `created_users`
    for user in created_users:
        defund_account(user)
