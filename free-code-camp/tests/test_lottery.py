import os

import brownie
import pytest
from brownie import (LinkToken, Lottery, MockV3Aggregator, VRFCoordinatorMock,
                     Wei, accounts, network)
from utils import publish

DECIMALS = 8
INITIAL_PRICE = 102.213 * 10**DECIMALS
FEE = 0.1 * 10**DECIMALS


@pytest.fixture(scope="module")
def aggregator_address():
    if network.show_active() == "development":
        return MockV3Aggregator.deploy(
            DECIMALS, INITIAL_PRICE, {"from": accounts[0]}
        ).address
    raise NotImplementedError("Unknown network")


@pytest.fixture(scope="module")
def link_token_address():
    if network.show_active() == "development":
        return LinkToken.deploy({"from": accounts[0]}).address
    raise NotImplementedError("Unknown network")


@pytest.fixture(scope="module")
def vrf_coordinator(link_token_address):
    if network.show_active() == "development":
        return VRFCoordinatorMock.deploy(link_token_address, {"from": accounts[0]})
    raise NotImplementedError("Unknown network")


@pytest.fixture(scope="module")
def lottery(aggregator_address, vrf_coordinator, link_token_address):
    if network.show_active() == "development":
        contract = Lottery.deploy(
            aggregator_address,
            vrf_coordinator.address,
            link_token_address,
            FEE,
            "0x" + 20 * "a1",
            {"from": accounts[0]},
        )
        if os.environ.get("BLOCKSCOUT_PUBLISH", "").lower() == "true":
            publish(
                Lottery,
                contract.address,
                aggregator_address,
                vrf_coordinator.address,
                link_token_address,
                int(FEE),
                bytes.fromhex(20 * "a1"),
            )
        return contract
    raise NotImplementedError("Unknown network")


def test_lottery(lottery, vrf_coordinator):
    # start lottery
    assert lottery.currentState() == 0
    with brownie.reverts("Ownable: caller is not the owner"):
        lottery.startLottery({"from": accounts[1]})

    lottery.startLottery({"from": accounts[0]})
    assert lottery.currentState() == 1

    # enter lottery
    min_enter_amount = lottery.entryFeeInUSD() * 10**DECIMALS / INITIAL_PRICE

    with brownie.reverts("Not enough funds to enter lottery"):
        lottery.enter(
            {"from": accounts[1], "value": Wei(f"{0.9 * min_enter_amount} ether")}
        )

    for account in accounts[1:]:
        lottery.enter(
            {"from": account, "value": Wei(f"{1.1 * min_enter_amount} ether")}
        )

    accounts_dict = {
        acc.address: {"acc": acc, "balance": acc.balance()} for acc in accounts
    }

    # end lottery
    total_lottery_balance = lottery.balance()
    assert total_lottery_balance > 0
    tx = lottery.endLottery({"from": accounts[0]})
    assert lottery.lastWinner() == brownie.ZERO_ADDRESS

    # mock randomness
    request_id = tx.events["RequestedRandomness"]["requestId"]
    random = int(os.urandom(10).hex(), 16)

    assert lottery.currentState() == 2
    brownie.ZERO_ADDRESS
    vrf_coordinator.callBackWithRandomness(
        request_id, random, lottery.address, {"from": accounts[0]}
    )

    # check end lottery states
    assert lottery.currentState() == 0
    assert lottery.balance() == 0
    winner_account = accounts_dict[lottery.lastWinner()]
    assert (
        winner_account["acc"].balance()
        == winner_account["balance"] + total_lottery_balance
    )

    # test errors in lottery states
    with brownie.reverts("Cannot end lottery"):
        lottery.endLottery({"from": accounts[0]})

    with brownie.reverts("Cannot enter not running lottery"):
        lottery.enter({"from": accounts[0]})

    lottery.startLottery({"from": accounts[0]})
    with brownie.reverts("Cannot start lottery"):
        lottery.startLottery({"from": accounts[0]})
