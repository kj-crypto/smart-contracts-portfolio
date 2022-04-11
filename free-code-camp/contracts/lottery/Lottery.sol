// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol';
import '@chainlink/contracts/src/v0.8/VRFConsumerBase.sol';
import '@openzeppelin/contracts/access/Ownable.sol';


contract Lottery is Ownable, VRFConsumerBase {
    enum LotteryStates {
        STOP,
        RUNNING,
        WINNER_FINDING
    }

    LotteryStates public currentState = LotteryStates.STOP;

    mapping(address => bool) public isPlayer;
    address payable[] public players;
    uint256 public entryFeeInUSD = 20;
    address public lastWinner;

    AggregatorV3Interface public priceFeed;

    uint256 public fee;
    bytes32 public keyHash;
    event RequestedRandomness(bytes32 requestId);

    constructor (
        address _priceFeedPrice,
        address _vrfCoordinator,
        address _linkToken,
        uint256 _fee,
        bytes32 _keyHash
    ) VRFConsumerBase(_vrfCoordinator, _linkToken)
    {
        priceFeed = AggregatorV3Interface(_priceFeedPrice);
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(currentState == LotteryStates.RUNNING, 'Cannot enter not running lottery');
        uint256 decimals = priceFeed.decimals();
        require(getEntranceFee() * msg.value / 10**(18 + decimals) > entryFeeInUSD, 'Not enough funds to enter lottery');

        if(!isPlayer[msg.sender]) {
            isPlayer[msg.sender] = true;
            players.push(payable(msg.sender));
        }
    }

    function getEntranceFee() public view returns(uint256) {
        (,int256 price,,,) = priceFeed.latestRoundData();
        return uint256(price);
    }

    function startLottery() public onlyOwner {
        require(currentState == LotteryStates.STOP, 'Cannot start lottery');
        currentState = LotteryStates.RUNNING;
    }

    function endLottery() public onlyOwner {
        require(currentState == LotteryStates.RUNNING, 'Cannot end lottery');
        currentState = LotteryStates.WINNER_FINDING;
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    function _clearLotteryStates() private {
        for(uint256 i = 0; i < players.length; i++)
            isPlayer[players[i]] = false;
        players = new address payable[](0);
        currentState = LotteryStates.STOP;
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness) internal override {
        require(currentState == LotteryStates.WINNER_FINDING, 'Wrong lottery state');
        require(randomness > 0, 'Random number not found');
        uint256 index = randomness % players.length;
        players[index].transfer(address(this).balance);
        lastWinner = players[index];
        _clearLotteryStates();
    }
}
