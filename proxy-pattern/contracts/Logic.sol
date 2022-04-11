// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Logic {
    bool initialized;
    uint256 magicNumber;

    constructor() {
        init();
    }

    function init() public {
        require(!initialized, 'Cannot initialized');
        initialized = true;

        magicNumber = 0x4241;
    }

    function setMagicNumber(uint256 newMagicNumber) public {
        magicNumber = newMagicNumber;
    }

    function getMagicNumber() public view returns (uint256) {
        return magicNumber;
    }
}
