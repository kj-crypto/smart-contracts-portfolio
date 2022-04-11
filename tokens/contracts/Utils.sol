// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './generic/IErc165.sol';

contract Ownable {
    // Only owner contract
    address public immutable owner;
    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(owner == msg.sender, 'Not the owner');
        _;
    }
}

// check if address is a contract or EOA
function checkIfContract(address addr) view returns(bool) {
    uint256 code_len;
    assembly {
        code_len := extcodesize(addr)
    }
    return code_len > 0;
}

library BytesToUint {
    function toUint256(bytes memory data, uint256 position) public pure returns(uint256) {
        /**
        Convert byte on given position in data bytes array to uint256
        */
        require(data.length >= position + 1, 'Out of range');
        uint256 result;

        assembly {
            // first 32 (0x20) bytes of byte array stores array length
            // interesting byte is on 32 + position + 1 address
            let offset := add(position, 0x01)

            // this loads 32 bytes of data array
            result := mload(add(data, offset))

            // interesting byte is on last position so we need to set to zeros all bytes except last one
            result := and(result, 0xff)
        }

        return result;
    }

    function toUint256(bytes1 data) public pure returns(uint256) {
        /**
        Convert bytes1 to uint256
        according to documentation
        "explicit conversions between integers and fixed-size byte arrays are only allowed, if both have the same size"
        so:
        1. Convert bytes1 to uint8
        2. Convert uint8 to uint256
        */
        uint8 result = uint8(data);
        return uint256(result);
    }
}

library Strings {
    function len(string memory str) public pure returns(uint256) {
        uint256 length;
        assembly {
            length := mload(str)
        }
        return length;
    }
}

// Erc165 contract which stores interfaces IDs
contract Erc165 is IErc165 {
    mapping(bytes4 => bool) internal interfaces;

    function registerInterfaceID(bytes4 interfaceID) public {
        interfaces[interfaceID] = true;
    }

    function registerInterfaceID(bytes4[] memory interfacesIDs) public {
        for(uint256 i = 0; i < interfacesIDs.length; i++)
            registerInterfaceID(interfacesIDs[i]);
    }

    function supportsInterface(bytes4 interfaceID) public view returns(bool) {
        return interfaces[interfaceID];
    }
}
