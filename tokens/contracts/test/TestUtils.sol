// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
Tests of utils
*/

import '../Utils.sol';

contract TestOwership is Ownable {
    function test() public view onlyOwner()
    returns(bool) {
        return true;
    }
}

contract TestCheckIfContractAddress {
    function test(address _address) public view returns(bool) {
        return checkIfContract(_address);
    }
}

contract TestBytesToUint {
    using BytesToUint for bytes;
    using BytesToUint for bytes1;

    function test(bytes memory data, uint256 position)
    public pure returns(uint256, uint256) {
        return (
            data.toUint256(position),
            data[position].toUint256()
        );
    }
}

contract TestStrings {
    using Strings for string;

    function testLen(string memory str) public pure returns(uint256) {
        return str.len();
    }
}
