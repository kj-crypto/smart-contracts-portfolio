// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '../generic/IBurnable.sol';
import '../generic/IMintable.sol';
import { Ownable } from '../Utils.sol';

import './MetaErc20.sol';

contract Mintable is MetaErc20, Ownable, IMintable, IBurnable {
    /**  Erc20 token which total supply can be change via mint or burn the tokens  */
    // Burned event is emitted when token are burned
    event Burned(address account, uint256 amount);
    constructor(uint256 totalSupply, string memory name, string memory symbol, uint8 decimals)
    MetaErc20(totalSupply, name, symbol, decimals) {}

    // only owner can mint new tokens
    function mint(uint256 amount) public onlyOwner() {
        balances[msg.sender] += amount;
        _totalSupply += amount;
    }

    function burn(uint256 amount) public {
        require(balances[msg.sender] >= amount, 'Cannot burn');
        balances[msg.sender] -= amount;
        _totalSupply -= amount;
        emit Burned(msg.sender, amount);
    }
}
