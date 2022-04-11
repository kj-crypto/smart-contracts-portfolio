import brownie
import pytest
from brownie import (BasicErc223, Sink, TokenReceiver, TokenReceiverErc223,
                     accounts)
from conftest import TOTAL_SUPPLY


@pytest.fixture
def sink():
    return Sink.deploy({"from": accounts[0]})


@pytest.fixture
def token_receiver():
    return TokenReceiver.deploy({"from": accounts[0]})


@pytest.fixture
def erc223_token():
    return BasicErc223.deploy(TOTAL_SUPPLY, {"from": accounts[0]})


@pytest.fixture
def erc223_token_receiver():
    return TokenReceiverErc223.deploy({"from": accounts[0]})


def test_locked_token(basic_token, sink):
    """This test shows that when we send tokens to contract address they are locked and cannot be withdraw, we lost this tokens"""
    # sink contract cannot handle ether neither ERC20 token
    # sending some ether to sink contract should raise an error
    with brownie.reverts():
        accounts[0].transfer(to=sink.address, amount=10)

    # sending ERC20 tokens to sink contract does not raise an error
    basic_token.transfer(sink.address, 15, {"from": accounts[0]})
    assert basic_token.balanceOf(sink.address, {"from": accounts[0]}) == 15


def test_simple_token_receiver(token_receiver, basic_token):
    """Test withdrawing of ERC20 token from contract address"""
    token_to_transfer = 16
    basic_token.transfer(
        token_receiver.address, token_to_transfer, {"from": accounts[0]}
    )
    assert (
        basic_token.balanceOf(token_receiver, {"from": accounts[0]})
        == token_to_transfer
    )

    eoa_account = accounts[-1]
    # withdraw tokens from contract account
    token_receiver.withdraw(basic_token.address, eoa_account.address)
    assert basic_token.balanceOf(token_receiver.address, {"from": accounts[0]}) == 0
    assert (
        basic_token.balanceOf(eoa_account.address, {"from": accounts[0]})
        == token_to_transfer
    )


def test_erc223_token_no_data_bytes(
    erc223_token, token_receiver, erc223_token_receiver
):
    # check token transfer to EOA
    tx = erc223_token.transfer(accounts[1].address, 12, {"from": accounts[0]})
    transfer = tx.events["Transfer"]
    assert transfer["_value"] == 12
    assert erc223_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 12
    assert transfer["_from"] and transfer["_to"]

    # check token transfer to contract not supporting ERC223 standard
    with brownie.reverts("Contract does not support tokenFallback interface"):
        erc223_token.transfer(token_receiver.address, 8, {"from": accounts[1]})

    # check successful transfer token to erc223 contract
    tx = erc223_token.transfer(erc223_token_receiver.address, 8, {"from": accounts[1]})
    transfer = tx.events["Transfer"]
    assert transfer["_value"] == 8
    # compare hex strings
    assert transfer["_data"] == "0x" + "".encode("ascii").hex()
    assert transfer["_from"] and transfer["_to"]

    assert (
        erc223_token.balanceOf(erc223_token_receiver.address, {"from": accounts[1]})
        == 8
    )
    assert erc223_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 12 - 8


def test_erc223_token_empty_data_bytes(
    erc223_token, token_receiver, erc223_token_receiver
):
    _data = "".encode("ascii")
    # check token transfer to EOA with empty data
    tx = erc223_token.transfer(accounts[1].address, 15, _data, {"from": accounts[0]})
    transfer = tx.events["Transfer"]
    assert transfer["_value"] == 15
    assert erc223_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 15
    assert transfer["_from"] and transfer["_to"]

    # check token transfer to contract not supporting ERC223 standard
    with brownie.reverts("Contract does not support tokenFallback interface"):
        erc223_token.transfer(token_receiver.address, 8, _data, {"from": accounts[1]})

    # check successful transfer token to erc223 contract
    tx = erc223_token.transfer(erc223_token_receiver.address, 8, {"from": accounts[1]})
    transfer = tx.events["Transfer"]
    assert transfer["_value"] == 8
    # compare hex strings
    assert transfer["_data"] == "0x" + _data.hex()
    assert transfer["_from"] and transfer["_to"]

    assert (
        erc223_token.balanceOf(erc223_token_receiver.address, {"from": accounts[1]})
        == 8
    )
    assert erc223_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 15 - 8


def test_erc223_token_with_data_bytes(
    erc223_token, token_receiver, erc223_token_receiver
):
    _data = "some test data string".encode("ascii")
    # cannot make transfer to EOA with non empty data
    with brownie.reverts("Cannot transfer _data field to EOA"):
        erc223_token.transfer(accounts[1].address, 18, _data, {"from": accounts[0]})

    # check not enough token amount
    assert erc223_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 0
    with brownie.reverts("Not enough token"):
        erc223_token.transfer(
            erc223_token_receiver.address, 8, _data, {"from": accounts[1]}
        )

    erc223_token.transfer(accounts[1].address, 18, {"from": accounts[0]})

    # check token transfer to contract not supporting ERC223 standard
    with brownie.reverts("Contract does not support tokenFallback interface"):
        erc223_token.transfer(token_receiver.address, 8, _data, {"from": accounts[1]})

    # check successful transfer token to erc223 contract
    tx = erc223_token.transfer(
        erc223_token_receiver.address, 8, _data, {"from": accounts[1]}
    )
    transfer = tx.events["Transfer"]
    assert transfer["_value"] == 8
    # compare hex strings
    assert transfer["_data"] == "0x" + _data.hex()
    assert transfer["_from"] and transfer["_to"]

    assert (
        erc223_token.balanceOf(erc223_token_receiver.address, {"from": accounts[1]})
        == 8
    )
    assert erc223_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 18 - 8
