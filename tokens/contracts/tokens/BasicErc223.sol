// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './BasicErc20.sol';
import '../generic/IErc223.sol';
import {checkIfContract} from '../Utils.sol';


contract BasicErc223 is IErc223, BasicErc20 {
    // Extension of Basic ERC20 token by ERC223 standard
    constructor(uint256 __totalSupply) BasicErc20(__totalSupply) {}

    function _transferToContract(ITokenFallback receiver, uint256 _value, bytes memory _data) private {
        require(balances[msg.sender] >= _value, 'Not enough token');
        try receiver.tokenFallback(msg.sender, _value, _data) {
            _makeTransfer(msg.sender, address(receiver), _value);
            emit Transfer(msg.sender, address(receiver), _value, _data);
        }
        catch {
            revert("Contract does not support tokenFallback interface");
        }
    }

    function transfer(address _to, uint256 _value) public override(BasicErc20, IErc20) {
        if(!checkIfContract(_to)) {
            super.transfer(_to, _value);
            return;
        }
        _transferToContract(ITokenFallback(_to), _value, "");

    }

    function transfer(address _to, uint256 _value, bytes calldata _data) public {
        if(checkIfContract(_to)) {
            _transferToContract(ITokenFallback(_to), _value, _data);
        }
        else if(_data.length == 0) {
            transfer(_to, _value);
        }
        else
            revert("Cannot transfer _data field to EOA");
    }
}
