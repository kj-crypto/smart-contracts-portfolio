// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '../generic/IErc20.sol';

contract BasicErc20 is IErc20 {
    // This is a basic implementation on ERC20 token supporting only basic ERC20 token functionality

    uint256 internal _totalSupply;
    mapping(address => uint256) internal balances;
    mapping(address => mapping(address => uint256)) public allowed;

    constructor(uint256 __totalSupply) {
        require(__totalSupply > 0, 'Supply has to be greater than 0');
        _totalSupply = __totalSupply;
        balances[msg.sender] = __totalSupply;
    }

    function totalSupply() public view returns(uint256) {
        return _totalSupply;
    }

    function balanceOf(address _owner) external view returns(uint256) {
        return balances[_owner];
    }

    function _makeTransfer(address _from, address _to, uint256 _value) internal {
        balances[_to] += _value;
        balances[_from] -= _value;
    }

    modifier enoughBalance(uint256 _value) {
        require(balances[msg.sender] >= _value, 'Not enough tokens');
        _;
    }
    function transfer(address _to, uint256 _value) public enoughBalance(_value) virtual {
        _makeTransfer(msg.sender, _to, _value);
        emit Transfer(msg.sender, _to, _value);
    }

    function approve(address _spender, uint256 _value) public enoughBalance(_value) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
    }

    function transferFrom(address _from, address _to, uint256 _value) public {
        require(allowed[_from][msg.sender] >= _value, 'Not allowed operation');
        allowed[_from][msg.sender] -= _value;
        _makeTransfer(_from, _to, _value);
        emit Transfer(_from, _to, _value);
    }
}
