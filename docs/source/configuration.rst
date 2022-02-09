Configuration Options
=====================

Configuring `AlgoPytest` is controlled by environemnt variables. These environment variables must be set before executing `pytest` for them to take any effect. If an environment variable is omitted, `AlgoPytest` takes on the default value, if there is one.

* ``ALGOD_ADDRESS``: The address where ``algod`` is listening on. (Default: ``"http://localhost:4001"``)
* ``ALGOD_TOKEN``: The secret token used to connect to ``algod``. (Default: ``"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"``)
* ``INDEXER_ADDRESS``: The address where the ``indexer`` is listening on. (Default: ``"http://localhost:8980"``)
* ``INDEXER_TOKEN``: The secret token used to connect to the ``indexer``.
* ``SANDBOX_DIR``: The path to the Algorand sandbox directory. (Default: ``"../sandbox/"``)
* ``INITIAL_FUNDS_ACCOUNT``: The address in your ``sandbox`` which was allocated the initial funds. (Default: The first "Online" address in your ``sandbox``)

