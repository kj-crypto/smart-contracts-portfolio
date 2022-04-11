import os

from brownie import (Box, BoxV2, Contract, CustomProxy, CustomProxyAdmin,
                     accounts, network)
from utils import publish


def deploy_proxy(box_address, proxy_admin_address):
    if network.show_active() == "development":
        proxy = CustomProxy.deploy(
            box_address,
            proxy_admin_address,
            # no initializer
            b"",
            {"from": accounts[0]},
        )
        if os.environ.get("BLOCKSCOUT_PUBLISH", "").lower() == "true":
            publish(CustomProxy, proxy.address, box_address, proxy_admin_address, b"")
        return proxy
    raise NotImplementedError("Unknown network")


def test_proxy():
    box = Box.deploy({"from": accounts[0]})
    proxy_admin = CustomProxyAdmin.deploy({"from": accounts[0]})
    proxy = deploy_proxy(box.address, proxy_admin.address)

    proxy_box = Contract.from_abi("ProxyBox", proxy.address, Box.abi)
    proxy_box.store(5, {"from": accounts[0]})
    assert proxy_box.retreive() == 5

    # upgrade contract
    box_v2 = BoxV2.deploy({"from": accounts[0]})
    proxy_admin.upgrade(proxy.address, box_v2.address, {"from": accounts[0]})
    proxy_box_v2 = Contract.from_abi("ProxyBoxV2", proxy.address, BoxV2.abi)
    assert proxy_box_v2.retreive() == 5

    # test new function in BoxV2
    proxy_box_v2.increment({"from": accounts[0]})
    assert proxy_box_v2.retreive() == 6
