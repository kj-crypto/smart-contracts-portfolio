// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './Box.sol';

contract BoxV2 is Box {
    function increment() public {
        value += 1;
        emit ValueChanged(value);
    }
}
