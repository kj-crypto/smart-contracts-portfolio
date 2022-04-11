import brownie
import pytest
from brownie import (BasicErc677, BytesToUint, PeopleStorage,
                     PeopleStorageErc677, accounts)

STORAGE_COST = 3


@pytest.fixture
def storage(basic_token):
    return PeopleStorage.deploy(
        basic_token.address, STORAGE_COST, {"from": accounts[0]}
    )


@pytest.fixture
def storage_data():
    return [
        {
            "name": "Alice",
            "age": 21,
        },
        {
            "name": "Bob",
            "age": 22,
        },
        {
            "name": "John",
            "age": 23,
        },
        {
            "name": "Marry",
            "age": 24,
        },
    ]


def test_free_storage(storage, storage_data):
    # check initial conditions
    assert len(storage.getAllPeople({"from": accounts[1]})) == 0

    # store data
    for item in storage_data:
        storage.freeStore(item["name"], item["age"], {"from": accounts[0]})

    stored_data = storage.getAllPeople({"from": accounts[0]})
    assert len(stored_data) == len(storage_data)
    item_index = 1
    assert item_index >= 0 and item_index < len(stored_data)
    assert (
        stored_data[item_index]
        == tuple(storage_data[item_index].values())
        == storage.people(item_index, {"from": accounts[1]})
    )


def test_erc20_payment_errors(basic_token, storage, storage_data):
    # 1. Account 1 has 0 token so approve and transferFrom are not possible
    assert basic_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 0
    with brownie.reverts("Not enough tokens"):
        basic_token.approve(storage.address, 10, {"from": accounts[1]})

    with brownie.reverts("Not allowed operation"):
        basic_token.transferFrom(
            accounts[1], storage.address, 10, {"from": accounts[1]}
        )

    # 2. Account 1 has some balance and can be approved
    basic_token.transfer(accounts[1].address, 10, {"from": accounts[0]})
    assert basic_token.balanceOf(accounts[1].address, {"from": accounts[0]}) == 10

    basic_token.approve(storage.address, 10, {"from": accounts[1]})
    # try to spend too much tokens
    with brownie.reverts("Not allowed operation"):
        basic_token.transferFrom(
            accounts[1], storage.address, 20, {"from": accounts[1]}
        )


def test_erc20_payment_method(storage, storage_data, basic_token):
    """Test of approve & transferFrom method in ERC20 token as a payment method for storing the data"""
    init_value = len(storage_data) * STORAGE_COST
    assert basic_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 0
    basic_token.transfer(accounts[1].address, init_value, {"from": accounts[0]})

    # allow 3'rd party address (contract) to transfer tokens
    # set not enough token to store whole list of data
    value = init_value // 2
    tx = basic_token.approve(storage.address, value, {"from": accounts[1]})
    # check if proper event emited
    assert tx.events["Approval"]
    assert (
        basic_token.allowed(accounts[1].address, storage.address, {"from": accounts[1]})
        == value
    )

    with brownie.reverts("Not allowed operation"):
        for item in storage_data:
            storage.payForStore(item["name"], item["age"], {"from": accounts[1]})

    # approve and transfer with proper amount of tokens
    basic_token.transfer(accounts[1].address, init_value, {"from": accounts[0]})
    basic_token.approve(storage.address, init_value, {"from": accounts[1]})

    for item in storage_data:
        storage.payForStore(item["name"], item["age"], {"from": accounts[1]})


def test_erc677_payment_method(storage_data):
    """Test of the transferAndCall method to store person data in contract"""
    # deploy contracts
    BytesToUint.deploy({"from": accounts[0]})
    token = BasicErc677.deploy(100, {"from": accounts[0]})
    storage = PeopleStorageErc677.deploy(
        token.address, STORAGE_COST, {"from": accounts[0]}
    )

    token.transfer(accounts[1].address, 50, {"from": accounts[0]})

    for person in storage_data:
        data = bytes([1]) + bytes([person["age"]]) + person["name"].encode("utf-8")
        # single transaction to store data
        tx = token.transferAndCall(
            storage.address, STORAGE_COST, data.hex(), {"from": accounts[1]}
        )
        assert tx.events["Approval"]
        assert tx.events["Transfer"]

    stored_data = storage.getAllPeople({"from": accounts[1]})
    assert len(stored_data) == len(storage_data)
    for i in range(len(storage_data)):
        assert (storage_data[i]["name"], storage_data[i]["age"]) == stored_data[i]

    # Check wrong data format
    data = bytes([0]).hex()
    with brownie.reverts("Wrong data format"):
        token.transferAndCall(
            storage.address, STORAGE_COST, data, {"from": accounts[1]}
        )

    # check wrong flag
    data = bytes([0, 1, 2]).hex()
    with brownie.reverts("Wrong flag"):
        token.transferAndCall(
            storage.address, STORAGE_COST, data, {"from": accounts[1]}
        )

    # check wrong storage cost
    data = bytes([1, 2, 3]).hex()
    with brownie.reverts("Amount differs from storage cost"):
        token.transferAndCall(
            storage.address, STORAGE_COST // 2, data, {"from": accounts[1]}
        )

    # check wrong token address
    with brownie.reverts():
        token.transferAndCall(
            accounts[1].address, STORAGE_COST, data, {"from": accounts[1]}
        )
