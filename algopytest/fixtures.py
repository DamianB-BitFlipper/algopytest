import pytest

from .transaction_ops import (
    create_app,
    delete_app,
)

from .helpers import (
    defund_account,
    add_standalone_account,
)

from .plugin_initialization import (
    Inits,
)
 
@pytest.fixture()
def owner():
    """Create an owner account."""
    owner = add_standalone_account()
    
    yield owner

    # Clean up
    defund_account(owner.private_key)

@pytest.fixture()
def user1():
    """Create a user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user.private_key)

@pytest.fixture()
def user2():
    """Create a second user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user.private_key)

@pytest.fixture()
def user3():
    """Create a third user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user.private_key)

@pytest.fixture()
def user4():
    """Create a fourth user account."""
    user = add_standalone_account()
    
    yield user

    # Clean up
    defund_account(user.private_key)

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
        defund_account(user.private_key)

@pytest.fixture()
def smart_contract_id(owner):
    """Create, yield and clean up the smart contract."""
    # Create the smart contract
    app_id = create_app(
        owner.private_key,
        Inits.approval_compiled,
        Inits.clear_compiled,
        Inits.global_schema,
        Inits.local_schema,
    )

    # This is where the testing happens
    yield app_id

    # Clean up the smart contract
    delete_app(owner.private_key, app_id)
