// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';
import '@openzeppelin/contracts/access/Ownable.sol';


contract FundMe is Ownable {
    mapping (address => uint256) public balances;
    address[] public funders;

    AggregatorV3Interface internal priceFeed;

    uint256 public constant minPriceInUSD = 50;

    constructor(address priceFeedAddress) {
        priceFeed = AggregatorV3Interface(priceFeedAddress);
    }

    function fund() public payable {
        // getPrice() / 10**decimals * msg.value / 10**18
        uint256 decimals = priceFeed.decimals();
        require(getPrice() * msg.value / 10 ** (18 + decimals) > minPriceInUSD, 'Not enough funds');

        if(balances[msg.sender] == 0) {
            funders.push(msg.sender);
        }
        balances[msg.sender] += msg.value;
    }

    function getPrice() public returns(uint256) {
        (   uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        return uint256(price);
    }

    function withdraw() public onlyOwner {
        payable(msg.sender).transfer(address(this).balance);

        for(uint256 i; i < funders.length; i++) {
            balances[funders[i]] = 0;
        }
        funders = new address[](0);
    }

    function getBalance() public view returns(uint256) {
        uint256 balance;
        for(uint256 i; i < funders.length; i++) {
            balance += balances[funders[i]];
        }
        return balance;
    }

    function getAllFunders() public view returns(address[] memory) {
        return funders;
    }
}
