import pytest

from algopytest import AlgoUser, MultisigAccount, SmartContractAccount

ADDR1 = "ERLRVRONJFKTDRXPNXO6DIX6R3BPVGQ7EXWIDXZFUMMWMNANZ2FC5I5UTQ"
PRIV_KEY1 = "jqjLb87XuQK71/u9Lac9eKJWUhsrzgWv5wots9xeZPgkVxrFzUlVMcbvbd3hov6OwvqaHyXsgd8loxlmNA3Oig=="
ADDR2 = "VAIPNEM5XL2RCDCTDYHUINI7RYIEVX46ULNDZ2DV7GIK5LSAXYSSMKP2GU"
PRIV_KEY2 = "gCB2O/DWNqFvPCX/NIGH8ljxOx7Wo4hQhJLeC0iIalioEPaRnbr1EQxTHg9ENR+OEErfnqLaPOh1+ZCurkC+JQ=="


@pytest.fixture
def algouser_alice():
    return AlgoUser(ADDR1, PRIV_KEY1, "Alice")


@pytest.fixture
def algouser_bob():
    return AlgoUser(ADDR2, PRIV_KEY2, "Bob")


@pytest.fixture
def smart_contract_account():
    return SmartContractAccount(42, "Answer to the Universe")


@pytest.fixture
def multisig_account(algouser_alice, algouser_bob):
    return MultisigAccount(
        version=1,
        threshold=1,
        owner_accounts=[algouser_alice, algouser_bob],
        name="Family Account",
    )


@pytest.fixture
def multisig_account_no_name(algouser_alice, algouser_bob):
    return MultisigAccount(
        version=1,
        threshold=1,
        owner_accounts=[algouser_alice, algouser_bob],
    )


@pytest.mark.parametrize(
    "entity_name, expected",
    [
        ("algouser_alice", "AlgoUser('Alice')"),
        ("smart_contract_account", "SmartContractAccount('Answer to the Universe')"),
        ("multisig_account", "MultisigAccount('Family Account')"),
        (
            "multisig_account_no_name",
            "MultisigAccount(AlgoUser('Alice'), AlgoUser('Bob'))",
        ),
    ],
)
def test_entity_str_method(entity_name, expected, request):
    entity = request.getfixturevalue(entity_name)
    assert str(entity) == expected


@pytest.mark.parametrize(
    "entity_name, expected",
    [
        (
            "algouser_alice",
            f"AlgoUser(address='{ADDR1}', private_key='{PRIV_KEY1}', name='Alice')",
        ),
        (
            "smart_contract_account",
            "SmartContractAccount(app_id=42, name='Answer to the Universe')",
        ),
        (
            "multisig_account",
            f"MultisigAccount(version=1, threshold=1, owner_accounts=[AlgoUser(address='{ADDR1}', private_key='{PRIV_KEY1}', name='Alice'), AlgoUser(address='{ADDR2}', private_key='{PRIV_KEY2}', name='Bob')], name='Family Account')",
        ),
        (
            "multisig_account_no_name",
            f"MultisigAccount(version=1, threshold=1, owner_accounts=[AlgoUser(address='{ADDR1}', private_key='{PRIV_KEY1}', name='Alice'), AlgoUser(address='{ADDR2}', private_key='{PRIV_KEY2}', name='Bob')], name=None)",
        ),
    ],
)
def test_entity_repr_method(entity_name, expected, request):
    entity = request.getfixturevalue(entity_name)
    assert repr(entity) == expected
