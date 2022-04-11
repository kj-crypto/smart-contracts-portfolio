// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './Logic.sol';

contract LogicV2 is Logic {

    // new functionality
    function halving() public view returns(uint256) {
        return magicNumber / 2;
    }

    function raiseError(string memory message) public pure {
        revert(message);
    }
}
