import os

import brownie
from brownie import (DappToken, MockV3Aggregator, TokenFarm, Wei, accounts,
                     network)
from utils import publish


def deploy_aggregator(price, decimals):
    if network.show_active() == "development":
        return MockV3Aggregator.deploy(decimals, price, {"from": accounts[0]}).address
    raise NotImplementedError("Unknown network")


def deploy_farm(reward_token_address, aggregator_address):
    if network.show_active() == "development":
        contract = TokenFarm.deploy(
            reward_token_address, aggregator_address, {"from": accounts[5]}
        )
        if os.environ.get("BLOCKSCOUT_PUBLISH", "").lower() == "true":
            publish(
                TokenFarm, contract.address, reward_token_address, aggregator_address
            )
        return contract
    raise NotImplementedError("Unknown network")


def test_token_farm():
    # deploy ERC20 tokens
    token_a = DappToken.deploy("TokenA", "A", 1000, {"from": accounts[0]})
    token_b = DappToken.deploy("TokenB", "B", 1500, {"from": accounts[1]})
    token_c = DappToken.deploy("TokenC", "C", 2000, {"from": accounts[2]})
    reward_token = DappToken.deploy("RewardToken", "RT", 10_000, {"from": accounts[0]})

    farm = deploy_farm(reward_token.address, deploy_aggregator(Wei("5 ether"), 0))

    # add allowed tokens with their price feeds
    with brownie.reverts("Ownable: caller is not the owner"):
        farm.addAllowedToken(
            token_a.address,
            deploy_aggregator(Wei("10 ether"), 5),
            {"from": accounts[0]},
        )

    farm.addAllowedToken(
        token_a.address, deploy_aggregator(Wei("0.1 ether"), 0), {"from": accounts[5]}
    )
    farm.addAllowedToken(
        token_b.address, deploy_aggregator(Wei("0.2 ether"), 0), {"from": accounts[5]}
    )
    farm.addAllowedToken(
        token_c.address, deploy_aggregator(Wei("0.04 ether"), 0), {"from": accounts[5]}
    )

    assert farm.tokenIsAllowed(token_a.address)
    assert farm.tokenIsAllowed(token_b.address)
    assert farm.tokenIsAllowed(token_c.address)

    # check stake errors
    with brownie.reverts("Cannot stake 0 tokens"):
        farm.stakeToken(accounts[0].address, 0, {"from": accounts[0]})

    with brownie.reverts("Not allowed token"):
        farm.stakeToken(accounts[0].address, 10, {"from": accounts[0]})

    # make staker possesing all allowed tokens
    full_staker = accounts[-1]
    token_a.transfer(full_staker.address, 100, {"from": accounts[0]})
    token_b.transfer(full_staker.address, 200, {"from": accounts[1]})
    token_c.transfer(full_staker.address, 500, {"from": accounts[2]})
    token_a.approve(farm.address, 100, {"from": full_staker})
    token_b.approve(farm.address, 200, {"from": full_staker})
    token_c.approve(farm.address, 500, {"from": full_staker})
    farm.stakeToken(token_a.address, 100, {"from": full_staker})
    farm.stakeToken(token_b.address, 200, {"from": full_staker})
    farm.stakeToken(token_c.address, 500, {"from": full_staker})
    assert farm.stakingBalances(full_staker.address, token_a.address) == 100
    assert farm.stakingBalances(full_staker.address, token_b.address) == 200
    assert farm.stakingBalances(full_staker.address, token_c.address) == 500

    # transfer reward token to farm contract
    assert reward_token.balanceOf(farm.address) == 0
    reward_token.transfer(farm.address, 5_000, {"from": accounts[0]})
    assert reward_token.balanceOf(farm.address) == 5_000

    # unstake token_a and token_c from full_staker
    # as a reward full_staker will receive reward_token
    assert reward_token.balanceOf(full_staker.address) == 0

    # token_a in ETH is 100 * 0.1 ETH = 10 ETH
    assert (
        Wei(farm.getReward(token_a.address, {"from": full_staker}).return_value).to(
            "ether"
        )
        == 10
    )

    # token_c in ETH is 500 * 0.04 ETH = 20 ETH
    assert (
        Wei(farm.getReward(token_c.address, {"from": full_staker}).return_value).to(
            "ether"
        )
        == 20
    )

    farm.unstake(token_a, {"from": full_staker})
    farm.unstake(token_c, {"from": full_staker})
    # after unstake there is ( 10 ETH + 20 ETH ) / 5 ETH = 6 RT(RewardToken)
    assert reward_token.balanceOf(full_staker) == 6
    # check balances in farm contract
    assert (
        farm.stakingBalances(full_staker.address, token_a.address)
        == farm.stakingBalances(full_staker.address, token_c.address)
        == 0
    )
    assert farm.stakingBalances(full_staker.address, token_b.address) == 200

    # test unstake error
    with brownie.reverts("Cannot unstake"):
        farm.unstake(token_a, {"from": full_staker})
