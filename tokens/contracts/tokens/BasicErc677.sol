// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './BasicErc20.sol';
import '../generic/IErc677.sol';


contract BasicErc677 is BasicErc20, IErc677 {
    constructor(uint256 totalSupply) BasicErc20(totalSupply) {}

    bytes public eCode;
    function transferAndCall(address receiver, uint256 amount, bytes calldata data) public {
        IErc677Receiver token = IErc677Receiver(receiver);
        approve(receiver, amount);
        token.onTokenTransfer(msg.sender, amount, data);
    }
}
