// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '../generic/IErc165.sol';
import '../Utils.sol';

interface IExample {
    function fun_1() external;
    function fun_2(uint256 arg) external;
}

contract TestErc165ComputedIDs is IExample, IErc165 {
    // check support interface via computation XOR logic every time when method called
    function fun_1() public {}
    function fun_2(uint256 arg) public {}
    function supportsInterface(bytes4 interfaceID) public view returns(bool) {
        if(
            interfaceID == IErc165.supportsInterface.selector ||
            interfaceID == IExample.fun_1.selector ^ IExample.fun_2.selector
        )
            return true;
        return false;
    }
}

contract TestErc165Storage is Erc165 {
    // check support interface via register interface and check if register in storage
    constructor() {
        super.registerInterfaceID(
            IErc165.supportsInterface.selector
        );
        super.registerInterfaceID(
            IExample.fun_1.selector ^ IExample.fun_2.selector
        );
    }
}
