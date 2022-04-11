// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Proxy {
    // use constant to replace unique address in compile time
    bytes32 private constant _SLOT_ADDRESS =
    bytes32(uint256(keccak256("eip1967.proxy.implementation")) - 1);

    function setImplementation(address _implementation) public {
        // workaround for using constant variable in inline assembly
        bytes32 _slot_address = _SLOT_ADDRESS;

        assembly {
            sstore(_slot_address, _implementation)
        }
    }

    fallback() external {
         // workaround for using constant variable in inline assembly
        bytes32 _slot_address = _SLOT_ADDRESS;

        assembly {
            // load free memory pointer
            let pointer := mload(0x40)

            // load calldata to memory
            calldatacopy(pointer, 0, calldatasize())

            // make delegate call
            let response := delegatecall(
                // use left gas
                gas(),
                // address of destination contract stored in `implementation` slot
                sload(_slot_address),
                // input call data pointer
                pointer,
                // input call data size
                calldatasize(),
                // output and output size set to `0`
                0,
                0
            )

            let output_size := returndatasize()
            returndatacopy(pointer, 0, output_size)

            switch response
            case 0 {
                // if delegate call failed return response error message
                revert(pointer, output_size)
            }
            default {
                return(pointer, output_size)
            }
        }
    }

}
