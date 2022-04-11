// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./Token.sol";

contract Vendor is Ownable {

    event BuyTokens(address buyer, uint256 amountOfETH, uint256 amountOfTokens);

    Token public token;
    uint256 public constant tokensPerEth = 100;
    constructor(address tokenAddress) {
        token = Token(tokenAddress);
    }

    function buyTokens() public payable {
        uint256 amount = tokensPerEth * msg.value / 1e18;
        token.transfer(msg.sender, amount);
        emit BuyTokens(msg.sender, msg.value / 1e18, amount);
    }

    function withdraw() public onlyOwner() {
        token.transfer(
            msg.sender,
            token.balanceOf(address(this))
        );
    }

    function sellTokens(uint256 amount) public {
        token.transferFrom(
            msg.sender,
            address(this),
            amount
        );
    }

  // ToDo: create a withdraw() function that lets the owner withdraw ETH

  // ToDo: create a sellTokens() function:

}