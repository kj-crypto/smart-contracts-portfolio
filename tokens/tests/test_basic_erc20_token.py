import brownie
from brownie import accounts
from conftest import TOTAL_SUPPLY


def test_basic_token_simple_transfer(basic_token):
    # check initial balances
    account = accounts[1]
    assert basic_token.balanceOf(account.address, {"from": account}) == 0
    assert (
        basic_token.balanceOf(accounts[0].address, {"from": accounts[0]})
        == TOTAL_SUPPLY
    )

    # transfer some token
    token_amount = 4
    tx = basic_token.transfer(account.address, token_amount, {"from": accounts[0]})

    # check if transfer emitted event
    transfer_event = tx.events["Transfer"]
    assert transfer_event["_from"] == accounts[0].address
    assert transfer_event["_to"] == account.address
    assert transfer_event["_value"] == token_amount

    # check balances after transfer
    assert basic_token.balanceOf(account.address, {"from": account}) == token_amount
    assert (
        basic_token.balanceOf(accounts[0].address, {"from": accounts[0]})
        == TOTAL_SUPPLY - token_amount
    )


def test_approve_basic_token_transfer(basic_token):
    middle_account = accounts[1]
    destination_account = accounts[2]

    # check initial balances are 0s
    assert basic_token.balanceOf(middle_account.address, {"from": middle_account}) == 0
    assert (
        basic_token.balanceOf(
            destination_account.address, {"from": destination_account}
        )
        == 0
    )

    allowed_token_to_spend = 6
    # allow middle_account to spend token
    tx = basic_token.approve(
        middle_account.address, allowed_token_to_spend, {"from": accounts[0]}
    )

    # check if event emitted
    approval_event = tx.events["Approval"]
    assert approval_event["_owner"] == accounts[0].address
    assert approval_event["_spender"] == middle_account.address
    assert approval_event["_value"] == allowed_token_to_spend

    # check allowed mapping
    assert (
        basic_token.allowed(accounts[0].address, middle_account)
        == allowed_token_to_spend
    )

    # transfer from token holder to destination_account by middle_account
    tx = basic_token.transferFrom(
        accounts[0].address,
        destination_account.address,
        2,
        {"from": middle_account.address},
    )

    # check transfer event
    transfer_event = tx.events["Transfer"]
    assert transfer_event["_from"] == accounts[0].address
    assert transfer_event["_to"] == destination_account.address
    assert transfer_event["_value"] == 2

    # check balances after transfer
    assert (
        basic_token.balanceOf(
            destination_account.address, {"from": destination_account}
        )
        == 2
    )
    assert (
        basic_token.balanceOf(accounts[0].address, {"from": accounts[0]})
        == TOTAL_SUPPLY - 2
    )
    assert (
        basic_token.allowed(accounts[0], middle_account.address)
        == allowed_token_to_spend - 2
    )

    # not allowed address try to spend token
    with brownie.reverts("Not allowed operation"):
        basic_token.transferFrom(
            accounts[0].address,
            destination_account.address,
            2,
            {"from": accounts[-1].address},
        )

    # try spend too much tokens
    with brownie.reverts("Not allowed operation"):
        basic_token.transferFrom(
            accounts[0].address,
            destination_account.address,
            10 * allowed_token_to_spend,
            {"from": middle_account.address},
        )
