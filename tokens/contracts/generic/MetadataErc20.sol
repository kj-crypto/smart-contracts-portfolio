// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
Metadata of the ERC20 token standard
*/

abstract contract MetadataErc20 {
    string public name;
    string public symbol;
    uint8 public decimals;

    constructor(string memory _name, string memory _symbol, uint8 _decimals) {
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
    }
}
