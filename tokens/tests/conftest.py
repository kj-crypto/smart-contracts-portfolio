import pytest
from brownie import BasicErc20, accounts

TOTAL_SUPPLY = 100


@pytest.fixture
def basic_token():
    return BasicErc20.deploy(TOTAL_SUPPLY, {"from": accounts[0]})
