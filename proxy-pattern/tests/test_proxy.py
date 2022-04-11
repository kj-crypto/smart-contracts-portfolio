import brownie
from brownie import Contract, Logic, LogicV2, Proxy, accounts


def test():
    logic = Logic.deploy({"from": accounts[0]})
    proxy = Proxy.deploy({"from": accounts[0]})
    logic_proxy = Contract.from_abi("LogicProxy", proxy.address, Logic.abi)

    # test logic state variable
    assert logic.getMagicNumber() == 0x4241

    proxy.setImplementation(logic.address, {"from": accounts[0]})

    # test logic_proxy constructor states init
    assert logic_proxy.getMagicNumber() == 0x0

    # init logic contract states through proxy
    logic_proxy.init({"from": accounts[0]})
    assert logic_proxy.getMagicNumber() == 0x4241

    # update contract
    logic_v2 = LogicV2.deploy({"from": accounts[0]})
    logic_v2_proxy = Contract.from_abi("LogicV2Proxy", proxy.address, logic_v2.abi)
    proxy.setImplementation(logic_v2.address, {"from": accounts[0]})

    # check old state
    assert logic_v2_proxy.getMagicNumber() == 0x4241

    # update state
    logic_v2_proxy.setMagicNumber(0x1234, {"from": accounts[0]})
    assert logic_v2_proxy.getMagicNumber() == 0x1234

    # test new functionality
    assert logic_v2_proxy.halving() == 0x1234 // 2

    # test error revert
    error_message = "temp error message"
    with brownie.reverts(error_message):
        logic_v2_proxy.raiseError(error_message)
