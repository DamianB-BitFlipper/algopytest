import time

import pytest
from algosdk.error import IndexerHTTPError

import algopytest
from algopytest.client_ops import _get_kmd_account_private_key, _wait_for_indexer
from algopytest.config_params import ConfigParams


def test_get_kmd_account_private_key_raises(monkeypatch):
    # Set the `ConfigParams.kmd_wallet_name` to a non-existent wallet name
    nonexistent_wallet = "non-existent-wallet-name"
    monkeypatch.setattr(ConfigParams, "kmd_wallet_name", nonexistent_wallet)

    with pytest.raises(ValueError, match=f"Wallet not found: {nonexistent_wallet}"):
        _get_kmd_account_private_key("RandomAddress")


def test_wait_for_indexer_raises(monkeypatch):
    # Set the `ConfigParams.indexer_timeout` to something quick
    monkeypatch.setattr(ConfigParams, "indexer_timeout", 1)

    start_time = time.time()
    with pytest.raises(
        IndexerHTTPError, match=r".*Invalid format for parameter asset-id.*"
    ):
        # A negative number is an invalid asset id, so this will always raise an `IndexerHTTPError`
        algopytest.asset_info(-1)
    end_time = time.time()

    # Assert that the `_wait_for_indexer` decorator waited at least 1 second before giving up
    assert end_time - start_time > 1


def test_initial_funds_account_raises(monkeypatch):
    # Set the `ConfigParams.initial_funds_account` to `None`
    monkeypatch.setattr(ConfigParams, "initial_funds_account", None)

    class MockIndexerClient:
        def accounts(self):
            # Return no accounts at all
            return {}

        def health(self):
            # Simulate the health of the indexer to be in sync with the algod client
            return {
                "round": algopytest.client_ops._algod_client().status()["last-round"]
            }

    # Override the `_indexer_client` to not return any accounts either
    monkeypatch.setattr(algopytest.client_ops, "_indexer_client", MockIndexerClient)

    with pytest.raises(RuntimeError, match="Initial funds account not yet created!"):
        algopytest.client_ops._initial_funds_account()
