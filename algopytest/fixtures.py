import pytest

from .transaction_ops import (
    create_app,
    delete_app,
)

from .account_ops import (
    defund_account,
    add_standalone_account,
)

from .program_store import (
    ProgramStore,
)
 
@pytest.fixture()
def owner():
    """An owner account."""
    owner = add_standalone_account()
    
    yield owner

    # Clean up
    defund_account(owner)

@pytest.fixture()
def user1():
    """A user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user)

@pytest.fixture()
def user2():
    """A second user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user)

@pytest.fixture()
def user3():
    """A third user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user)

@pytest.fixture()
def user4():
    """A fourth user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user)

@pytest.fixture()
def create_user():
    """A factory fixture to create an `AlgoUser`."""
    created_users = []

    def _create_user(funded=True):
        user = add_standalone_account(funded=funded)
        created_users.append(user)
        return user

    yield _create_user

    # Clean up by de-funding all of the `created_users`
    for user in created_users:
        defund_account(user)

@pytest.fixture()
def smart_contract_id(owner):
    """A smart contract instance."""
    # Create the smart contract
    app_id = create_app(
        owner,
        ProgramStore.approval_compiled,
        ProgramStore.clear_compiled,
        ProgramStore.global_schema,
        ProgramStore.local_schema,
    )

    # This is where the testing happens
    yield app_id

    # Clean up the smart contract
    delete_app(owner, app_id)
