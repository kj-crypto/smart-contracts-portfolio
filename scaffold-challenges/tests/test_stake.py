import brownie
import pytest
import requests
import brownie.network.web3 as web3
from brownie import accounts, Staker, ExternalContract, Wei


STAKING_TIME = 120

def send_evm_increase_time(seconds):
    # send raw rpc to ganache cli in order to increase time
    resp = requests.post(
        url="http://localhost:8545",
        json={
            "jsonrpc": "2.0",
            "method": "evm_increaseTime",
            "params": [seconds],
            "id": 1
        }
    )
    assert resp.status_code == 200, f'Some error occurred {resp.text}'


@pytest.fixture #(scope='module', autouse=True)
def external_contract():
    return ExternalContract.deploy({'from': accounts[0]})


@pytest.fixture #(scope='module')
def stake_contract(external_contract):
    return Staker.deploy(STAKING_TIME, external_contract.address, {'from': accounts[0]})


def test_deposit_stake(stake_contract):
    stake_value = 5
    account = accounts[1]
    # stake some found
    tx = stake_contract.stake({'from': account, 'value': stake_value})

    # check balance of account
    assert stake_contract.balances(account.address) == stake_value

    # check emitted event
    assert tx.events['Stake']['from'] == account.address
    assert tx.events['Stake']['deposit'] == stake_value

    # stake again and check
    tx = stake_contract.stake({'from': account, 'value': stake_value * 2})
    assert stake_contract.balances(account.address) == stake_value * 3

    # check emitted event
    assert tx.events['Stake']['from'] == account.address
    assert tx.events['Stake']['deposit'] == stake_value * 2

def test_time_left(stake_contract):
    left_time = stake_contract.timeLeft({'from': accounts[1]})
    assert left_time == STAKING_TIME

    send_evm_increase_time(int(0.5 *STAKING_TIME))
    accounts[1].transfer(to=stake_contract.address, amount=10)
    left_time = stake_contract.timeLeft({'from': accounts[1]})
    assert left_time <= int(0.5 * STAKING_TIME)

    send_evm_increase_time(int(0.6 *STAKING_TIME))
    accounts[1].transfer(to=stake_contract.address, amount=10)
    with brownie.reverts():
        stake_contract.timeLeft({'from': accounts[1]})

def test_zero_deposit_stake(stake_contract):
    account = accounts[2]
    with brownie.reverts('Accept deposit > 0'):
        stake_contract.stake({'from': account, 'value': 0})

def test_stake_complete(external_contract, stake_contract):
    # send via stake method
    stake_contract.stake({'from': accounts[1], 'value': Wei('0.8 ether')})
    assert web3.eth.getBalance(stake_contract.address) == Wei('0.8 ether')

    # move time after staking deadline
    send_evm_increase_time(STAKING_TIME + 1)
    stake_contract.stake({'from': accounts[1], 'value': Wei('0.1 ether')})

    with brownie.reverts('Balance under the threshold'):
        stake_contract.execute({'from': accounts[1]})

    # transfer via receive method
    accounts[2].transfer(to=stake_contract.address, amount=Wei('0.3 ether'))
    assert web3.eth.getBalance(stake_contract.address) == Wei('1.2 ether')

    stake_contract.execute({'from': accounts[1]})
    assert web3.eth.getBalance(stake_contract.address) == 0
    assert web3.eth.getBalance(external_contract.address) == Wei('1.2 ether')

def test_early_withdrawal(stake_contract):
    stake_contract.stake({'from': accounts[1], 'value': Wei('0.8 ether')})
    assert stake_contract.balances(accounts[1].address) == Wei('0.8 ether')

    with brownie.reverts('Stake is immature'):
        stake_contract.withdraw({'from': accounts[1]})

    send_evm_increase_time(STAKING_TIME + 1)
    stake_contract.stake({'from': accounts[1], 'value': Wei('0.1 ether')})
    assert stake_contract.balances(accounts[1].address) == Wei('0.9 ether')

    stake_contract.withdraw({'from': accounts[1]})
    assert stake_contract.balances(accounts[1].address) == 0
