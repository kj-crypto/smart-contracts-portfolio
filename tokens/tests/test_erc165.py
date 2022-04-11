from brownie import TestErc165ComputedIDs, TestErc165Storage, accounts


def run_interface_id_test(contract):
    def if_support(id):
        return contract.supportsInterface(id, {"from": accounts[1]})

    # check if false for id 0xff_ff_ff_ff
    assert not if_support("0x" + 4 * "ff")

    # check id for ERC165 interface, which is '0x01ffc9a7'
    assert if_support("0x01ffc9a7")

    # check custom support interface
    id = 0x628BA97E ^ 0xC6D63590
    assert if_support("0x" + id.to_bytes(4, "big").hex())

    # check another id
    assert id != id // 2 != 0xFF_FF_FF_FF
    assert not if_support("0x" + (id // 2).to_bytes(4, "big").hex())


def test_erc165_computed_ids():
    contract = TestErc165ComputedIDs.deploy({"from": accounts[0]})
    run_interface_id_test(contract)


def test_erc165_stored_ids():
    contract = TestErc165Storage.deploy({"from": accounts[0]})
    run_interface_id_test(contract)
