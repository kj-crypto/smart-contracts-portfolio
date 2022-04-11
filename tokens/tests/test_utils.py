import brownie
from brownie import (BytesToUint, Strings, TestBytesToUint,
                     TestCheckIfContractAddress, TestOwership, TestStrings,
                     accounts)


def test_ownership():
    owner = accounts[0]
    hacker = accounts[1]

    # deploy contract
    contract = TestOwership.deploy({"from": owner})

    # owner can perform test function call
    assert contract.test({"from": owner})

    # hacker cannot call test function
    with brownie.reverts("Not the owner"):
        contract.test({"from": hacker})


def test_check_if_contract_address():
    # deploy contract
    contract = TestCheckIfContractAddress.deploy({"from": accounts[0]})
    assert not contract.test(accounts[1].address)
    assert contract.test(contract.address)


def test_bytes_to_uint_conversion():
    # deploy library
    BytesToUint.deploy({"from": accounts[0]})
    # deploy contract
    contract = TestBytesToUint.deploy({"from": accounts[0]})

    array = [15, 23, 57, 255, 0, 125, 199, 222, 111]
    input = bytes(array).hex()

    for index, value in enumerate(array):
        results = contract.test(input, index)
        assert value == results[0] == results[1]

    # test out of range
    with brownie.reverts("Out of range"):
        contract.test(input, len(array) + 1)


def test_strings_library():
    # deploy lib and contract
    Strings.deploy({"from": accounts[0]})
    contract = TestStrings.deploy({"from": accounts[0]})
    strings = ["", "1234", "abcdef", "x", "xyz"]
    for string in strings:
        response = contract.testLen(string, {"from": accounts[0]})
        assert response == len(string)
