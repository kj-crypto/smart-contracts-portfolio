import os

import brownie
import pytest
from brownie import FundMe, MockV3Aggregator, Wei, accounts, network
from utils import publish

DECIMALS = 8
INITIAL_PRICE = 123.9876 * 10**DECIMALS


@pytest.fixture(scope="module")
def aggregator_address():
    if network.show_active() == "development":
        return MockV3Aggregator.deploy(
            DECIMALS, INITIAL_PRICE, {"from": accounts[0]}
        ).address
    raise NotImplementedError("Unknown network")


@pytest.fixture
def contract(aggregator_address):
    if network.show_active() == "development":
        contract = FundMe.deploy(aggregator_address, {"from": accounts[0]})
        if os.environ.get("BLOCKSCOUT_PUBLISH", "").lower() == "true":
            publish(FundMe, contract.address, aggregator_address)
        return contract
    raise NotImplementedError("Unknown network")


def test_fund(contract):
    assert contract.getBalance() == 0

    # try to fund below required minimum
    min_amount = contract.minPriceInUSD() * 10**DECIMALS / INITIAL_PRICE

    with brownie.reverts("Not enough funds"):
        contract.fund({"from": accounts[1], "value": Wei(f"{0.9 * min_amount} ether")})

    # fund twice by the same funder
    contract.fund({"from": accounts[1], "value": Wei(f"{1.1 * min_amount} ether")})
    contract.fund({"from": accounts[1], "value": Wei(f"{1.2 * min_amount} ether")})
    assert len(contract.getAllFunders()) == 1
    assert contract.funders(0) == accounts[1].address
    assert contract.balances(accounts[1].address) == contract.getBalance()

    # another funds
    contract.fund({"from": accounts[2], "value": Wei(f"{1.3 * min_amount} ether")})
    contract.fund({"from": accounts[3], "value": Wei(f"{1.4 * min_amount} ether")})
    assert len(contract.getAllFunders()) == 3
    assert contract.balances(accounts[2].address) == Wei(f"{1.3 * min_amount} ether")

    # test withdraw
    with brownie.reverts("Ownable: caller is not the owner"):
        contract.withdraw({"from": accounts[1]})

    assert contract.getBalance() > 0
    contract.withdraw({"from": accounts[0]})
    assert contract.getBalance() == 0
    assert len(contract.getAllFunders()) == 0
    assert contract.balances(accounts[2].address) == 0
