// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';


contract Dex {
    uint256 public totalLiquidityTokenA;
    uint256 public totalLiquidityTokenB;

    IERC20 tokenA;
    IERC20 tokenB;

    constructor(IERC20 _tokenA, IERC20 _tokenB) {
        tokenA = _tokenA;
        tokenB = _tokenB;
    }

    function initDex(uint256 amountTokenA, uint256 amountTokenB) public {
        require(
            totalLiquidityTokenA * totalLiquidityTokenA == 0 &&
            amountTokenA != 0 && amountTokenB != 0,
            'Cannot init DEX'
        );

        tokenA.transferFrom(msg.sender, address(this), amountTokenA);
        tokenB.transferFrom(msg.sender, address(this), amountTokenB);

        totalLiquidityTokenA = amountTokenA;
        totalLiquidityTokenB = amountTokenB;
    }

    function swap(IERC20 inputToken, uint256 amount) public returns(uint256) {
        /*
        There is a swap based on formula
        x*y = k
        x/y = 1
        where
        k = totalLiquidityTokenA * totalLiquidityTokenA

        For given dx we're looking for dy
        (x + dx)*(y - dy) = k = x*y
        xy + ydx - xdy - dx*dy = xy
        (x + dx)*dy = ydx

        dy = ydx / (x + dx)

        */
        if(inputToken == tokenA) {
            require(amount < totalLiquidityTokenA, 'Too much to swap');
            uint256 dy = totalLiquidityTokenB * amount / (totalLiquidityTokenA + amount);
            totalLiquidityTokenA -= amount;
            totalLiquidityTokenB += dy;
            return dy;
        }
        else if(inputToken == tokenB) {
            require(amount < totalLiquidityTokenB, 'Too much to swap');
            uint256 dy = totalLiquidityTokenA * amount / (totalLiquidityTokenB + amount);
            totalLiquidityTokenB -= amount;
            totalLiquidityTokenA += dy;
            return dy;
        }
        revert('Wrong token');
    }
}
