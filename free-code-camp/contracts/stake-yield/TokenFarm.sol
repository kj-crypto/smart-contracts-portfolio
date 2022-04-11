// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';


contract TokenFarm is Ownable {

    mapping(address => bool) public allowedTokens;
    // array need for iterating
    address[] public tokens;

    // token => priceFeed contract address
    mapping(address => address) public tokenPriceFeeds;

    // reward token address when unstake
    address public rewardToken;

    // staker => token => amount
    mapping(address => mapping(address => uint256)) public stakingBalances;

    constructor(address _rewardToken, address _rewardTokenPriceFeed) {
        rewardToken = _rewardToken;
        tokenPriceFeeds[rewardToken] = _rewardTokenPriceFeed;
    }

    function stakeToken(address _token, uint256 _amount) public {
        require(_amount > 0, "Cannot stake 0 tokens");
        require(tokenIsAllowed(_token), "Not allowed token");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        stakingBalances[msg.sender][_token] += _amount;
    }

    function addAllowedToken(address _token, address _priceFeed) public onlyOwner {
        if(!allowedTokens[_token]) {
            allowedTokens[_token] = true;
            tokens.push(_token);
            tokenPriceFeeds[_token] = _priceFeed;
        }
    }

    function tokenIsAllowed(address _token) public returns(bool) {
        return allowedTokens[_token];
    }

    function unstake(address token) public {
        uint256 balance = stakingBalances[msg.sender][token];
        require(balance > 0, 'Cannot unstake');
        uint256 reward = getReward(token);
        (uint256 price, uint256 decimals) = getTokenPrice(rewardToken);
        uint256 rewardTokenAmount = reward * 10 ** decimals / price;
        IERC20(rewardToken).transfer(msg.sender, rewardTokenAmount);
        stakingBalances[msg.sender][token] = 0;
    }

    function getReward(address token) public returns(uint256) {
        uint256 reward = 0;
        uint256 stakedAmount = stakingBalances[msg.sender][token];
        if(stakedAmount > 0) {
            (uint256 price, uint256 decimals) = getTokenPrice(token);
            reward = stakedAmount * price / 10 ** decimals;
        }
        return reward;
    }

    function getTokenPrice(address token) public returns(uint256, uint256) {
        (, int price,,,) = AggregatorV3Interface(tokenPriceFeeds[token]).latestRoundData();

        return (uint256(price), uint256(AggregatorV3Interface(tokenPriceFeeds[token]).decimals()));
    }
}
