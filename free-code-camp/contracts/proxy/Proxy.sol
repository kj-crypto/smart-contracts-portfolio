// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/proxy/transparent/ProxyAdmin.sol';
import '@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol';


contract CustomProxyAdmin is ProxyAdmin {}

contract CustomProxy is TransparentUpgradeableProxy {
    constructor(
        address _logic,
        address admin_,
        bytes memory _data
    ) payable
    TransparentUpgradeableProxy(
        _logic,
        admin_,
        _data
    ) {}
}
