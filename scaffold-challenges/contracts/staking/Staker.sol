// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './External.sol';

contract Staker {
    // events for staking
    event Stake(address from, uint256 deposit);

    mapping (address => uint256) public balances;
    uint256 public constant threshold = 1 ether;
    uint256 immutable stakingPeriod;

    ExternalContract toPay;

    constructor(uint256 _stakingPeriod, address payable _extrnalContractAddress) {
        require(_stakingPeriod > 1 minutes, "Staking period less then 1 minute");
        stakingPeriod = block.timestamp + _stakingPeriod;
        toPay = ExternalContract(_extrnalContractAddress);
    }

    function stake() public payable {
        require(msg.value > 0, "Accept deposit > 0");
        balances[msg.sender] += msg.value;
        emit Stake(msg.sender, msg.value);
    }

    modifier matureStake() {
        require(block.timestamp >= stakingPeriod, "Stake is immature");
        _;
    }

    function execute() public matureStake {
          require(address(this).balance >= threshold, "Balance under the threshold");
          payable(address(toPay)).transfer(address(this).balance);
    }

    function timeLeft() public view returns(uint256) {
        return stakingPeriod - block.timestamp;
    }

    function withdraw() public matureStake {
        payable(msg.sender).transfer(balances[msg.sender]);
        balances[msg.sender] = 0;
    }

    receive() external payable {
        stake();
    }
}
