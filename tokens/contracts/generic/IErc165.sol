// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
This is implementation of ERC165 interface, based on https://github.com/ethereum/EIPs/blob/master/EIPS/eip-165.md
*/

interface IErc165 {
    function supportsInterface(bytes4 interfaceID) external view returns(bool);
}
