from brownie import MetaErc20, accounts


def deploy(total_amount, name, symbol, decimals):
    return MetaErc20.deploy(total_amount, name, symbol, decimals, {"from": accounts[0]})


def test_deploy():
    total_amount = 10
    name = "Test name"
    symbol = "TN"
    decimals = 0
    contract = deploy(total_amount, name, symbol, decimals)

    # tests set up metadata over contract constructor
    assert contract.name() == name
    assert contract.symbol() == symbol
    assert contract.decimals() == decimals
    assert contract.totalSupply() == total_amount


def test_decimals_representation():
    owner = accounts[0].address
    decimals = 5
    total_amount = 25
    contract = deploy(total_amount, "Name", "N", decimals)
    assert contract.balanceOf(owner) / 10**decimals == 0.00025

    # test 0 decimals
    decimals = 0
    contract = deploy(total_amount, "Name", "N", decimals)
    assert contract.balanceOf(owner) / 10**decimals == 25
