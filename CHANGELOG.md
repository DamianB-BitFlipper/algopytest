# CHANGELOG

## [Unreleased] - yyyy-mm-dd

Here we write upgrading notes for brands. It's a team effort to make them as
straightforward as possible.

### New Features
- Function ``application_local_state`` to read the local state of an account relating to a deployed application
- Function ``group_transaction`` to send group transactions
- Removed ``ProgramStore`` class and replaced it with ``deploy_smart_contract`` which the user would call directly in a user-defined fixture to retrieve the smart contract app ID for testing
- Implemented support for group transactions to hold both ``Transaction`` and ``LogicSigTransaction``
- Support ASA operations with the following transaction operations ``create_asset``, ``destroy_asset``, ``update_asset``, ``freeze_asset``, ``transfer_asset``, ``opt_in_asset`` and ``close_out_asset``.
- Implemented asset related utility functions ``asset_balance`` and ``asset_info``.
- Support multi-signature transaction with the ``multisig_transaction`` transaction operation.
- Implemented a ``SmartContractAccount`` entity to hold the address of a smart contract as an ``AlgoUser``.
- Utilize the ``KMD`` to access account private keys of the sandbox.
- AlgoPytest user entities implement a ``name`` field for a more human-friendly debugging and logging experience
- Implemented a ``TxnElemsContext`` context manager which alters all transaction operations to return an unsent transaction object rather than send the transaction.
- Implemented a ``TxnIDContext`` context manager which alters all transaction operations to return the ``txn_id`` associated with the sent transaction.
- Functions ``create_app`` and ``create_compiled_app`` are int sub-classed context managers that may be used in a ``with`` clause or cleaned up manually with ``delete_app``.
- Function ``create_asset`` returns an int sub-classed context manager that can handle clean up within a ``with`` clause.

### Bug Fixes
- Removed typing subscripts to be compatible with Python 3.8
- The ``application_local_state`` no longer fails when attempting to read a deleted local field.

### Other Changes
- Inputs which accept ``PyTEAL`` directly take the ``pyteal.Expr`` and not a function which generates a ``pyteal.Expr``
- Renamed the ``group_elem`` function to a more generic ``txn_name`` since this function applies also to smart signatures and multi-signature transactions, not solely group transactions.
- All transaction operations take all possible parameters, even the less commonly used ones.
- The AlgoPytest API accepts ``AlgoUser`` as a user input anywhere whenever an address is requested.
- Sped up the ``AlgoPytest`` test suite runtime by caching the ``_initial_funds_account``.
- Altered arguments of ``smart_signature_transaction`` to accept transaction tuple
- Replaced simply ``print`` with a proper ``logging.logger`` in the ``transaction_boilerplate`` decorator.
- Migrated code to support py-algorand-sdk v2.0.0

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
