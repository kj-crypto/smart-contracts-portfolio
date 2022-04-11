// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
Interface of the ERC677 transferAndCall based on https://github.com/ethereum/EIPs/issues/677
*/

interface IErc677Receiver {
    function onTokenTransfer(address from, uint256 amount, bytes calldata data) external;
}

interface IErc677 {
    event Transfer(address _from, address _to, uint256 _amount, bytes _data);
    function transferAndCall(address receiver, uint256 amount, bytes calldata data) external;
}
