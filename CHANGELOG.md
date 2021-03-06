# Change Log

## [Unreleased] - yyyy-mm-dd

Here we write upgrading notes for brands. It's a team effort to make them as
straightforward as possible.

### Added
- Function `application_local_state` to read the local state of an account relating to a deployed application
- Function `group_transaction` to send group transactions

## [1.0.0] - 2022-02-09

The first release of AlgoPytest. Includes many functions to write usable tests as well as a good foundation to expand this library

### Added
- File `account_ops.py` includes functions which facilitate the creation, funding and defunding of an Algorand User within this framework
- File `client_ops.py` includes all sorts of functions which ultimately interact with either algod or the indexer. Functions include sending transaction, reading the applications' global state, compiling PyTEAL source, etc.
- File `config_params.py` holds a class `_ConfigParams` for reading environment variables to configure AlgoPytest
- File `entities.py` holds a class `AlgoUser` defining an Algorand User within this framework
- File `fixtures.py` defines a few fixtures which automatically are available in a Pytest test suite when AlgoPytest is installed. They mainly focus on creating test users and a fresh smart contract
- File `program_store.py` holds a class `_ProgramStore` which stores all of the necessary details required to deploy the smart contract to be tested
- File `transaction_ops.py` includes functions which help send various transaction types such as Application call to Payment transaction into the network.
- File `type_stubs.py` holds any custom types used in type annotating AlgoPytest
