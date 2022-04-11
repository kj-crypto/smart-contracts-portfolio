# based on https://github.com/scaffold-eth/scaffold-eth-challenges/tree/challenge-2-token-vendor

import brownie
import pytest
from brownie import accounts, Token, Vendor

INITIAL_AMOUNT = 1000

@pytest.fixture
def token():
    return Token.deploy(INITIAL_AMOUNT, {'from': accounts[0]})

@pytest.fixture
def vendor(token):
    return Vendor.deploy(token.address, {'from': accounts[0]})

def test_checkpoint_2(token):
    # 1. check init balance
    assert token.balanceOf(accounts[0].address, {'from': accounts[0]}) == INITIAL_AMOUNT

    # 2. transfer and check balance
    n = 10
    token.transfer(accounts[1].address, n, {'from': accounts[0]})
    assert token.balanceOf(accounts[1].address, {'from': accounts[1]}) == n

def test_checkpoint_3(token, vendor):
    # 1. error, vendor balance is zero
    with brownie.reverts('ERC20: transfer amount exceeds balance'):
        vendor.buyTokens({'from': accounts[1], 'value': '1 ether'})
    assert token.balanceOf(vendor.address, {'from': accounts[1]}) == 0

    # 2. send token to vendor and then buy
    token.transfer(vendor.address, INITIAL_AMOUNT // 2, {'from': accounts[0]})
    tx = vendor.buyTokens({'from': accounts[1], 'value': '1 ether'})
    event = tx.events['BuyTokens']
    assert event['buyer'] == accounts[1].address
    assert event['amountOfETH'] == 1
    assert event['amountOfTokens'] == 100

    # 3. buy 10 tokens for 0.1 eth
    tx = vendor.buyTokens({'from': accounts[2], 'value': '0.1 ether'})
    event = tx.events['BuyTokens']
    assert event['buyer'] == accounts[2].address
    assert event['amountOfETH'] == 0
    assert event['amountOfTokens'] == 10

    # 4. transfer bought token to another address
    assert token.balanceOf(accounts[2].address, {'from': accounts[2]}) == 10
    token.transfer(accounts[3].address, 7, {'from': accounts[2]})
    assert token.balanceOf(accounts[2].address, {'from': accounts[2]}) == 3
    assert token.balanceOf(accounts[3].address, {'from': accounts[3]}) == 7

    # 5. check ownership
    assert vendor.owner({'from': accounts[0]}) == accounts[0].address

    # 6. withdraw token from vendor
    with brownie.reverts('Ownable: caller is not the owner'):
        vendor.withdraw({'from': accounts[1]})

    assert token.balanceOf(vendor.address, {'from': accounts[1]}) != 0
    vendor.withdraw({'from': accounts[0]})
    assert token.balanceOf(vendor.address, {'from': accounts[1]}) == 0

def test_checkpoint_4(token, vendor):
    # 1. sell token by vendor
    with brownie.reverts('ERC20: transfer amount exceeds balance'):
        vendor.sellTokens(10, {'from': accounts[1]})

    # token.transfer(INITIAL_AMOUNT // 2, vendor.address, {'from': accounts})
    token.approve(vendor.address, INITIAL_AMOUNT // 2, {'from': accounts[0]})

    assert token.balanceOf(vendor.address, {'from': accounts[1]}) == 0
    vendor.sellTokens(10, {'from': accounts[0]})
    assert token.balanceOf(vendor.address, {'from': accounts[1]}) == 10
