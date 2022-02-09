# AlgoPytest &mdash; Framework for Testing Algorand Smart Contracts using PyTest

*AlgoPytest* is a Pytest plugin framework which hides away all of the complexity and repetitiveness that comes with testing Algorand Smart Contracts. 

A lot of boilerplate code is necessary in order to setup a suitable test environment. *AlgoPytest* takes care of all that. It handles deploying the smart contract, creating and funding any necessary user accounts and then using those accounts to interact with the smart contract itself. Additionally, each test is a run in a freshly deployed smart contract, facilitating a clean slate which prevents any stateful interference from any previously run tests. 

## Getting Started

The most relevant information needed for getting off the ground are:
- [Read-The-Docs documentation](https://algopytest.readthedocs.io/en/latest/)
- [Installation](#installation)
- [Simplified Usage](#simplified-usage)
- [Demos](#demos)

This project's Read-The-Docs page is especially useful, since it lists and describes all of the available methods and fixtures provided to you by *AlgoPytest*.

## Installation

### Prerequisites

- Python 3 and `pip`
- Install the Algorand [sandbox](https://github.com/algorand/sandbox).

### Installing AlgoPytest
```bash
pip install algopytest-framework
```

## Simplified Usage
Make sure the sandbox is up and running. Preferably use a local network for your testing. Note: There is currently an issue with the `dev` sandbox which makes it work not too well with *AlgoPytest*. Networks `release` and `nightly` are more recommended.
```bash
# Spin up the `release` network
./sanbox up release
```
---
Set any necessary environment variables. 
```bash
# The path to your sandbox so that AlgoPytest may interact with the sandbox
export SANDBOX_DIR=/path/to/installation/of/sandbox/

# The address in your `sanbox` which was allocated the initial funds
export INITIAL_FUNDS_ACCOUNT=4BJAN3J32NDMZJWU3DPIPGCPBQIUTXL3UB2LEG5Z3CFPRJZOOZC2GH5DMQ
```
- List of environment variables recognized by *AlgoPytest*: [documentation](TODO).

----
Create a `conftest.py` file in your Pytest `tests` directory and initialize *AlgoPytest* within as so:

```python
# File: conftest.py
from algopytest import initialize

# Load the smart contracts from this project. The path to find these
# imports can be set by the environment variable `$PYTHONPATH`.
# e.g. `export PYTHONPATH=.../smart-contract-project/assets`
from approval_program import approval_program
from clear_program import clear_program

def pytest_configure(config):
    """Initialize algopytest before the pytest tests run."""
    initialize(approval_program=approval_program, 
               clear_program=clear_program,
               local_ints=0, local_bytes=1, 
               global_ints=0, global_bytes=1)
```

Now, any Pytest tests you write automatically have access to the *AlgoPytest* fixtures. Additionally, you can import and utilize the various helper functions that ship with the framework.

- List of available fixtures: [documentation](https://algopytest.readthedocs.io/en/latest/fixtures.html)
- Provided helper functions: [documentation](https://algopytest.readthedocs.io/en/latest/algopytest.html)
----
A simple test to make sure that the creator of the smart contract can update the application is provided below. It uses the *AlgoPytest* fixtures `owner` and `smart_contract_id` and the helper function `update_app`.

```python
# File: test_behavior.py
def test_update_from_owner(owner, smart_contract_id):
    update_app(owner, smart_contract_id)
```

## Demos

This *AlgoPytest* project includes [demos](https://algopytest.readthedocs.io/en/latest/demos.html) of Algorand Smart Contract projects that utilize this package to implement their test suite. These demo projects give examples of how a real-world project may use *AlgoPytest* for its testing. They provide greater context for how to integrate *AlgoPytest* into your project. The tests and the `initialization` code of the demos may be found within their respective `tests` directory. Therein, you will see how the fixtures are used to extensively stress test the Smart Contract code and life-cycle. 

For example, a semi-involved test in one of the demos, [algo-diploma](https://github.com/DamianB-BitFlipper/algo-diploma), showcases *AlgoPytest* utilizing the power of Pytest fixtures:

```python
@pytest.fixture
def owner_in(owner, smart_contract_id):
    """Create an ``owner`` fixture that has already opted in to ``smart_contract_id``."""
    opt_in_app(owner, smart_contract_id)
    
    # The test runs here
    yield owner

    # Clean up by closing out of the application
    close_out_app(owner, smart_contract_id)

@pytest.fixture
def user1_in(user1, smart_contract_id):
    """Create a ``user1`` fixture that has already opted in to ``smart_contract_id``."""
    opt_in_app(user1, smart_contract_id)

    # The test runs here
    yield user1

    # Clean up by closing out of the application
    close_out_app(user1, smart_contract_id)

def test_issue_diploma(owner_in, user1_in, smart_contract_id):
    diploma_metadata = "Damian Barabonkov :: MIT :: BSc Computer Science and Engineering :: 2020"

    # The application arguments and account to be passed in to 
    # the smart contract as it expects
    app_args = ['issue_diploma', diploma_metadata]
    accounts = [user1_in.address]

    # Issue the `diploma_metadata` to the recipient `user1`
    call_app(owner_in, smart_contract_id, app_args=app_args, accounts=accounts)
```

Original source may be found [here](https://github.com/DamianB-BitFlipper/algo-diploma/blob/master/tests/test_interaction.py).

## Detailed Usage
Refer to the [Documentation References](#documentation-references) below for more specific explanations of key topics.

### AlgoPytest Initialization
Firstly, you must follow the Pytest directory structure. Essentially, all tests will be found within a `tests` directory in the root of your project.

Before being able to write Pytest tests for your Algorand Smart Contract, you need to initialize the *AlgoPytest* plugin. Before any Pytest tests run, you must declare to *AlgoPytest* the smart contract code to be tested as well as its storage requirements. This is most easily achieved by creating a `conftest.py` file and calling `algopytest.initialize`from within a function named `pytest_configure`. Pytest understands `pytest_configure` and will execute the function before any tests run.

For example:
```bash
# Sample project file structure
smart-contract-project/
├── assets
│   ├── approval_program.py
│   ├── clear_program.py
└── tests
        ├── conftest.py
        └── test_behavior.py
```

```python
# File: conftest.py
from algopytest import initialize

# Load the smart contracts from this project. The path to find these
# imports can be set by the environment variable `$PYTHONPATH`.
# e.g. `export PYTHONPATH=.../smart-contract-project/assets`
from approval_program import approval_program
from clear_program import clear_program

def pytest_configure(config):
    """Initialize algopytest before the pytest tests run."""
    initialize(approval_program=approval_program, 
               clear_program=clear_program,
               local_ints=0, local_bytes=1, 
               global_ints=0, global_bytes=1)
```

The `approval_program` and `clear_program` must be Python functions which return a `pyteal.Expr`. 

For example, the simplest clear program in this format is:
```python
# File: clear_program.py
def clear_program():
    """A clear program that always approves."""
    return Return(Int(1))
```

### Writing Pytest Tests

The *AlgoPytest* package is written as a Pytest plugin. This allows *AlgoPytest* to automatically register fixtures without you needing to import anything.  You may simply use the fixtures directly in the function signature.

These fixtures make testing Algorand Smart Contracts significantly easier for you as the developer. Fixtures such as the user ones: `owner`, `user1`, `user2`, etc. automatically create users with funded balances and cleans them up at the end of the test. The `smart_contract_id` fixture automatically deploys (and cleans up) the smart contract supplied to the `initialize` function above with `owner` as its creator. Before, writing a test even as simple as checking that the owner of an application can update their application, required non-negligible boilerplate code. Now, in order to write this test, all of the necessary boilerplate code is taken care of; you only have to focus only on the testing code at hand and nothing else.

```python
# File: test_behavior.py
def test_update_from_owner(owner, smart_contract_id):
    "The `owner` and `smart_contract_id` are AlgoPytest fixtures."
    update_app(owner, smart_contract_id)
```

### Documentation References
- Pytest directory structure: [documentation](https://docs.pytest.org/en/6.2.x/goodpractices.html#choosing-a-test-layout-import-rules)
- Pytest `pytest_configure`: [documentation](https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_configure)
- Pytest `conftest.py`: [documentation](https://docs.pytest.org/en/latest/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files)
- *AlgoPytest* `initialize`: [documentation](https://algopytest.readthedocs.io/en/latest/algopytest.html#algopytest.initialize)

## Dev Installation
```bash
git clone https://github.com/DamianB-BitFlipper/algopytest.git
cd algopytest
conda env create -f environment.yml
pre-commit install
pip install -e .
```

Please submit a Pull Request for any suggested changes you would like to make.

## Disclaimer
**This package and smart contract(s) in this codebase have NOT been professionally audited. Therefore, they should not be used as a production application.****
