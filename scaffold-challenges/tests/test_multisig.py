# based on https://github.com/scaffold-eth/scaffold-eth-challenges/tree/challenge-3-multi-sig
from brownie import accounts, Multisig, Wei
from brownie.network import web3
import brownie
import os

def deploy(N, M):
    return Multisig.deploy(N, M, {'from': accounts[0]})

def test_deploy():
    with brownie.reverts('Wrong N of M'):
        deploy(0, 1)

    with brownie.reverts('Wrong N of M'):
        deploy(1, 0)

    with brownie.reverts('Wrong N of M'):
        deploy(2, 1)

    wallet = deploy(1, 2)
    assert wallet.N() == 1
    assert wallet.M() == 2


def test_multisig_wallet():
    # test 3 of 5 multisig
    wallet = deploy(3, 5)
    assert wallet.N() == 3
    assert wallet.M() == 5

    with brownie.reverts('Not enough funds'):
        wallet.transferEth(accounts[-1].address, 10, {'from': accounts[0]})
    accounts[-1].transfer(wallet.address, Wei('5 ether'))
    # check balance
    assert web3.eth.get_balance(wallet.address) == Wei('5 ether')

    for account in accounts[0:4]:
        wallet.addSigner(account.address, {'from': accounts[0]})

    # create destination account
    destination = accounts.add(os.urandom(256 // 8))
    assert destination.balance() == 0

    with brownie.reverts('Wrong N of M signers'):
        wallet.transferEth(destination.address, Wei('3 ether'), {'from': accounts[-1]})

    wallet.addSigner(accounts[4].address, {'from': accounts[0]})

    with brownie.reverts('Wrong N of M signers'):
        wallet.transferEth(destination.address, Wei('3 ether'), {'from': accounts[-1]})

    wallet.approve({'from': accounts[5]})
    wallet.approve({'from': accounts[6]})

    with brownie.reverts('Wrong N of M signers'):
        wallet.transferEth(destination.address, Wei('3 ether'), {'from': accounts[-1]})

    for account in accounts[0:4]:
        wallet.approve({'from': account})

    with brownie.reverts('Not enough funds'):
        wallet.transferEth(destination.address, Wei('6 ether'), {'from': accounts[-1]})

    wallet.transferEth(destination.address, Wei('3 ether'), {'from': accounts[-1]})
    assert destination.balance() == Wei('3 ether')
    assert web3.eth.get_balance(wallet.address) == Wei('2 ether')
