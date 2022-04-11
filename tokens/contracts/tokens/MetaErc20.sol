// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '../generic/MetadataErc20.sol';
import './BasicErc20.sol';

contract MetaErc20 is BasicErc20, MetadataErc20 {
    // Erc20 token with Metadata
    constructor(uint256 totalSupply, string memory name, string memory symbol, uint8 decimals)
    BasicErc20(totalSupply) MetadataErc20(name, symbol, decimals) {}
}
