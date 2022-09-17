# CHANGELOG

## [Unreleased] - yyyy-mm-dd

Here we write upgrading notes for brands. It's a team effort to make them as
straightforward as possible.

### New Features
- Function ``application_local_state`` to read the local state of an account relating to a deployed application
- Function ``group_transaction`` to send group transactions
- Removed ``ProgramStore`` class and replaced it with ``deploy_smart_contract`` which the user would call directly in a user-defined fixture to retrieve the smart contract app ID for testing
- Implemented support for group transactions to hold both ``Transaction`` and ``LogicSigTransaction``
- All transaction operations take all possible parameters, even the less commonly used ones.
- Support ASA operations with the following transaction operations ``create_asset``, ``destroy_asset``, ``update_asset``, ``freeze_asset``, ``transfer_asset``, ``opt_in_asset`` and ``close_out_asset``.
- Implemented asset related utility functions ``asset_balance`` and ``asset_info``.
- Support multi-signature transaction with the ``multisig_transaction`` transaction operation.

### Bug Fixes
- Removed typing subscripts to be compatible with Python 3.8

### Other Changes
- Inputs which accept ``PyTEAL`` directly take the ``pyteal.Expr`` and not a function which generates a ``pyteal.Expr``

## [1.0.0] - 2022-02-09

The first release of AlgoPytest. Includes many functions to write usable tests as well as a good foundation to expand this library

### New Features
- File ``account_ops.py`` includes functions which facilitate the creation, funding and defunding of an Algorand User within this framework
- File ``client_ops.py`` includes all sorts of functions which ultimately interact with either algod or the indexer. Functions include sending transaction, reading the applications' global state, compiling PyTEAL source, etc.
- File ``config_params.py`` holds a class ``_ConfigParams`` for reading environment variables to configure AlgoPytest
- File ``entities.py`` holds a class ``AlgoUser`` defining an Algorand User within this framework
- File ``fixtures.py`` defines a few fixtures which automatically are available in a Pytest test suite when AlgoPytest is installed. They mainly focus on creating test users and a fresh smart contract
- File ``program_store.py`` holds a class ``_ProgramStore`` which stores all of the necessary details required to deploy the smart contract to be tested
- File ``transaction_ops.py`` includes functions which help send various transaction types such as Application call to Payment transaction into the network.
- File ``type_stubs.py`` holds any custom types used in type annotating AlgoPytest
