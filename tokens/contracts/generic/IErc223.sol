// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
This is implementation of ERC223 token standard based on https://github.com/ethereum/EIPs/issues/223
*/

import '../generic/IErc20.sol';

interface ITokenFallback {
    function tokenFallback(address _from, uint256 _amount, bytes calldata _data) external;
}

interface IErc223 is IErc20 {
    event Transfer(address indexed _from, address indexed _to, uint256 _value, bytes _data);
    function transfer(address _to, uint _value, bytes calldata _data) external;
}
