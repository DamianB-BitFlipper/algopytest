Configuration Options
=====================

Configuring `AlgoPytest` is controlled by environment variables. These environment variables must be set before executing `pytest` for them to take any effect. If an environment variable is omitted, `AlgoPytest` takes on the default value, if there is one.

* ``ALGOD_ADDRESS``: The address where ``algod`` is listening on. (Default: ``"http://localhost:4001"``)
* ``ALGOD_TOKEN``: The secret token used to connect to ``algod``. (Default: ``"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"``)
* ``INDEXER_ADDRESS``: The address where the ``indexer`` is listening on. (Default: ``"http://localhost:8980"``)
* ``INDEXER_TOKEN``: The secret token used to connect to the ``indexer``.
* ``KMD_ADDRESS``: The address where ``kmd`` is listening on. (Default: ``"http://localhost:4002"``)
* ``KMD_TOKEN``: The secret token used to connect to ``kmd``. (Default: ``"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"``)
* ``KMD_WALLET_NAME``: The name of the wallet in ``kmd`` from which all of the accounts are generated. (Default: ``"unencrypted-default-wallet"``)
* ``KMD_WALLET_PASSWORD``: The password used to access the wallet in ``kmd`` from which all of the accounts are generated. (Default: ``""``)
* ``INITIAL_FUNDS_ACCOUNT``: The address in your ``sandbox`` which was allocated the initial funds. (Default: The first "Online" address in your ``sandbox``)
* ``INDEXER_TIMEOUT``: The timeout in seconds to use when querying the indexer before raising an exception. (Default: ``61``)

