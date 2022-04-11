# dex of 2 ERC20 tokens based on https://medium.com/@austin_48503/%EF%B8%8F-minimum-viable-exchange-d84f30bd0c90
from brownie import accounts, DexToken, Dex
import pytest
import brownie


@pytest.fixture
def token_a():
    return DexToken.deploy('Token_A', 'A', 1000, {'from': accounts[0]})

@pytest.fixture
def token_b():
    return DexToken.deploy('Token_B', 'B', 2000, {'from': accounts[0]})

def test_dex(token_a, token_b):
    # check initial setup
    assert token_a.name() == 'Token_A' and token_a.symbol() == 'A'
    assert token_a.balanceOf(accounts[0].address) == 1000
    assert token_b.name() == 'Token_B' and token_b.symbol() == 'B'
    assert token_b.balanceOf(accounts[0].address) == 2000

    # provide liquidity to DEX
    dex = Dex.deploy(token_a.address, token_b.address, {'from': accounts[2]})
    token_a.approve(dex.address, 800, {'from': accounts[0]})
    token_b.approve(dex.address, 1200, {'from': accounts[0]})

    dex.initDex(800, 1200, {'from': accounts[0]})
    assert dex.totalLiquidityTokenA() == 800
    assert dex.totalLiquidityTokenB() == 1200

    # can't initialize DEX again
    with brownie.reverts('Cannot init DEX'):
        dex.initDex(800, 1200, {'from': accounts[2]})

    # swap token_a to token_b
    token_b_amount = dex.swap(token_a.address, 300, {'from': accounts[2]}).return_value
    assert dex.totalLiquidityTokenA() == 800 - 300
    assert dex.totalLiquidityTokenB() == 1200 + token_b_amount

    # swap token_b to token_a
    token_a_amount = dex.swap(token_b.address, 400, {'from': accounts[2]}).return_value
    assert dex.totalLiquidityTokenA() == 800 - 300 + token_a_amount
    assert dex.totalLiquidityTokenB() == 1200 + token_b_amount - 400

    # test swap errors
    with brownie.reverts('Too much to swap'):
        dex.swap(token_a.address, 1000, {'from': accounts[2]})

    with brownie.reverts('Too much to swap'):
        dex.swap(token_b.address, 2000, {'from': accounts[2]})

    with brownie.reverts('Wrong token'):
        dex.swap(dex.address, 2000, {'from': accounts[2]})
