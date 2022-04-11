import brownie
import pytest
from brownie import Mintable, accounts

TOTAL_SUPPLY = 25


@pytest.fixture
def deployed_token():
    return Mintable.deploy(
        TOTAL_SUPPLY, "Mintable token", "MT", 0, {"from": accounts[0]}
    )


def test_minting_token(deployed_token):
    # check initial supply
    assert deployed_token.totalSupply() == TOTAL_SUPPLY
    assert deployed_token.balanceOf(accounts[0].address) == TOTAL_SUPPLY

    mint_amount = 15
    # mint token by owner
    deployed_token.mint(mint_amount, {"from": accounts[0]})
    assert deployed_token.totalSupply() == TOTAL_SUPPLY + mint_amount
    assert deployed_token.balanceOf(accounts[0].address) == TOTAL_SUPPLY + mint_amount


def test_minting_only_by_owner(deployed_token):
    # miniting can be performed only by owner
    deployed_token.mint(12, {"from": accounts[0]})

    # otherwise the transaction should be reverted
    with brownie.reverts("Not the owner"):
        deployed_token.mint(11, {"from": accounts[1]})


def test_token_burn(deployed_token):
    account = accounts[1]
    initial_amount = 10
    burn_amount = 7
    # check initial condition
    assert deployed_token.balanceOf(account.address) == 0
    assert deployed_token.totalSupply({"from": account}) == TOTAL_SUPPLY

    # try to burn too much tokens
    with brownie.reverts("Cannot burn"):
        deployed_token.burn(burn_amount, {"from": account})

    deployed_token.transfer(account.address, initial_amount, {"from": accounts[0]})
    assert deployed_token.balanceOf(account.address) == initial_amount

    # again try to burn too much tokens
    with brownie.reverts("Cannot burn"):
        deployed_token.burn(2 * initial_amount, {"from": account})

    # burn some tokens
    # burning decrease totalSupply value and emit Burn event
    tx = deployed_token.burn(burn_amount, {"from": account})
    burn_event = tx.events["Burned"]
    assert burn_event["account"] == account.address
    assert burn_event["amount"] == burn_amount

    # check balances after token burning
    assert (
        deployed_token.balanceOf(account.address, {"from": account})
        == initial_amount - burn_amount
    )
    assert deployed_token.totalSupply({"from": account}) == TOTAL_SUPPLY - burn_amount
