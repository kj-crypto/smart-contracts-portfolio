import brownie
import pytest
from brownie import Erc721, Sink, Strings, TokenReceiverErc721, accounts

NAME = "nft-token"
SYMBOL = "NT"


@pytest.fixture
def erc721_token():
    # deploy necessary library
    Strings.deploy({"from": accounts[0]})
    return Erc721.deploy(NAME, SYMBOL, {"from": accounts[0]})


def test_basic_metadata(erc721_token):
    assert erc721_token.name({"from": accounts[1]}) == NAME
    assert erc721_token.symbol({"from": accounts[1]}) == SYMBOL


def test_adding_and_banning_minters(erc721_token):
    with brownie.reverts("Sender is not allowed to perform this operation"):
        erc721_token.addMinter(accounts[1].address, {"from": accounts[1]})

    assert not erc721_token.checkIfAllowedToMint(accounts[1].address)

    erc721_token.addMinter(accounts[1].address, {"from": accounts[0]})
    assert erc721_token.checkIfAllowedToMint(accounts[1].address)

    erc721_token.banMinter(accounts[1].address, {"from": accounts[1]})
    assert not erc721_token.checkIfAllowedToMint(accounts[1].address)


def test_nft_minting(erc721_token):
    # add mintable addresses
    erc721_token.addMinter(accounts[1].address, {"from": accounts[0]})
    erc721_token.addMinter(accounts[2].address, {"from": accounts[1]})

    erc721_token.mint(0, "0 nft uri", {"from": accounts[1]})
    erc721_token.mint(1, "1 nft uri", {"from": accounts[1]})
    tx = erc721_token.mint(2, "2 nft uri", {"from": accounts[2]})

    transfer = tx.events["Transfer"]
    assert transfer["_from"] == brownie.ZERO_ADDRESS
    assert transfer["_to"] == accounts[2].address
    assert transfer["_tokenId"] == 2

    with brownie.reverts("Sender is not allowed to perform this operation"):
        erc721_token.mint(2, "2 nft uri", {"from": accounts[3]})

    assert erc721_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 2
    assert erc721_token.balanceOf(accounts[2].address, {"from": accounts[2]}) == 1
    assert erc721_token.balanceOf(accounts[3].address, {"from": accounts[3]}) == 0
    assert erc721_token.tokenURI(0, {"from": accounts[1]}) == "0 nft uri"
    assert erc721_token.tokenURI(1, {"from": accounts[1]}) == "1 nft uri"
    assert erc721_token.tokenURI(2, {"from": accounts[2]}) == "2 nft uri"
    with brownie.reverts("Invalid token ID"):
        erc721_token.tokenURI(3, {"from": accounts[3]})
    assert erc721_token.ownerOf(0, {"from": accounts[0]}) == accounts[1].address
    assert erc721_token.ownerOf(1, {"from": accounts[1]}) == accounts[1].address
    assert erc721_token.ownerOf(2, {"from": accounts[2]}) == accounts[2].address
    with brownie.reverts("Invalid token ID"):
        erc721_token.ownerOf(3, {"from": accounts[3]})
    assert erc721_token.balanceOf(accounts[1].address, {"from": accounts[1]}) == 2
    assert erc721_token.balanceOf(accounts[2].address, {"from": accounts[2]}) == 1
    assert erc721_token.balanceOf(accounts[3].address, {"from": accounts[3]}) == 0
    with brownie.reverts("Wrong owner address"):
        erc721_token.balanceOf(brownie.ZERO_ADDRESS, {"from": accounts[0]})

    with brownie.reverts("URI cannot be empty"):
        erc721_token.mint(3, "", {"from": accounts[1]})

    with brownie.reverts("Token already exists"):
        erc721_token.mint(2, "new uri")

    assert erc721_token.totalSupply({"from": accounts[0]}) == 3


def test_nft_transfer_basic_errors(erc721_token):
    erc721_token.mint(0, "uri-0", {"from": accounts[0]})
    # 1. safeTransferFrom without `_data`
    with brownie.reverts("Invalid token ID"):
        erc721_token.safeTransferFrom(
            accounts[0].address, accounts[1].address, 1, {"from": accounts[0]}
        )

    with brownie.reverts("Sender not allowed or owned"):
        erc721_token.safeTransferFrom(
            accounts[1].address, accounts[1].address, 0, {"from": accounts[1]}
        )

    with brownie.reverts("Source address not an owner"):
        erc721_token.safeTransferFrom(
            accounts[1].address, accounts[1].address, 0, {"from": accounts[0]}
        )

    with brownie.reverts("Wrong destination address"):
        erc721_token.safeTransferFrom(
            accounts[0].address, brownie.ZERO_ADDRESS, 0, {"from": accounts[0]}
        )

    # 2. safeTransferFrom with `_data` bytes
    data = "test data".encode("utf-8").hex()
    with brownie.reverts("Invalid token ID"):
        erc721_token.safeTransferFrom(
            accounts[0].address, accounts[1].address, 1, data, {"from": accounts[0]}
        )

    with brownie.reverts("Sender not allowed or owned"):
        erc721_token.safeTransferFrom(
            accounts[1].address, accounts[1].address, 0, data, {"from": accounts[1]}
        )

    with brownie.reverts("Source address not an owner"):
        erc721_token.safeTransferFrom(
            accounts[1].address, accounts[1].address, 0, data, {"from": accounts[0]}
        )

    with brownie.reverts("Wrong destination address"):
        erc721_token.safeTransferFrom(
            accounts[0].address, brownie.ZERO_ADDRESS, 0, data, {"from": accounts[0]}
        )

    # 3. transferFrom
    with brownie.reverts("Invalid token ID"):
        erc721_token.transferFrom(
            accounts[0].address, accounts[1].address, 1, {"from": accounts[0]}
        )

    with brownie.reverts("Sender not allowed or owned"):
        erc721_token.transferFrom(
            accounts[1].address, accounts[1].address, 0, {"from": accounts[1]}
        )

    with brownie.reverts("Source address not an owner"):
        erc721_token.transferFrom(
            accounts[1].address, accounts[1].address, 0, {"from": accounts[0]}
        )

    with brownie.reverts("Wrong destination address"):
        erc721_token.transferFrom(
            accounts[0].address, brownie.ZERO_ADDRESS, 0, {"from": accounts[0]}
        )


def test_approve(erc721_token):
    erc721_token.mint(0, "uri-0", {"from": accounts[0]})

    # test against not existing token id
    with brownie.reverts("Invalid token ID"):
        erc721_token.getApproved(1, {"from": accounts[0]})

    assert erc721_token.getApproved(0, {"from": accounts[0]}) == brownie.ZERO_ADDRESS

    with brownie.reverts("Invalid token ID"):
        erc721_token.approve(accounts[2], 1, {"from": accounts[1]})

    with brownie.reverts("Not allowed sender"):
        erc721_token.approve(accounts[2], 0, {"from": accounts[1]})

    tx = erc721_token.approve(accounts[2], 0, {"from": accounts[0]})
    approval = tx.events["Approval"]
    assert approval["_owner"] == accounts[0].address
    assert approval["_approved"] == accounts[2].address
    assert approval["_tokenId"] == 0

    assert erc721_token.getApproved(0, {"from": accounts[1]}) == accounts[2].address

    # check set zero address
    erc721_token.approve(brownie.ZERO_ADDRESS, 0, {"from": accounts[0]})
    assert erc721_token.getApproved(0, {"from": accounts[1]}) == brownie.ZERO_ADDRESS


def test_approval_for_all(erc721_token):
    assert (
        erc721_token.isApprovedForAll(
            accounts[1].address, accounts[0].address, {"from": accounts[0]}
        )
        == False  # noqa
    )

    tx = erc721_token.setApprovalForAll(
        accounts[1].address, True, {"from": accounts[0]}
    )
    event = tx.events["ApprovalForAll"]
    assert event["_owner"] == accounts[0].address
    assert event["_operator"] == accounts[1].address
    assert event["_approved"] == True  # noqa

    # set approve by operator
    erc721_token.mint(0, "uri-0", {"from": accounts[0]})
    erc721_token.approve(accounts[2].address, 0, {"from": accounts[1]})

    tx = erc721_token.setApprovalForAll(
        accounts[1].address, False, {"from": accounts[0]}
    )
    event = tx.events["ApprovalForAll"]
    assert event["_approved"] == False  # noqa


def transfer_function_type(type_name, contract):
    functions = {"safe": contract.safeTransferFrom, "unsafe": contract.transferFrom}
    return functions[type_name]


@pytest.mark.parametrize(
    "transfer_type,if_data,destination_account",
    [
        ("safe", False, "eoa"),
        ("safe", False, "receiver"),
        ("safe", True, "eoa"),
        ("safe", True, "receiver"),
        ("unsafe", False, "eoa"),
        ("unsafe", False, "receiver"),
        ("unsafe", False, "sink"),
    ],
    ids=[
        "safeTransferFrom - with no `_data` - to EOA",
        "safeTransferFrom - with no `_data` - to contract",
        "safeTransferFrom - with `_data` - to EOA",
        "safeTransferFrom - with `_data` - to contract",
        "transferFrom - with no `_data` - to EOA",
        "transferFrom - with no `_data` - to contract",
        "transferFrom - with no `_data` - to sink contract",
    ],
)
def test_nft_transfer(erc721_token, transfer_type, if_data, destination_account):
    owner = accounts[0]
    approved_account = accounts[1]
    operator_account = accounts[2]
    destination = (
        accounts[3]
        if destination_account == "eoa"
        else
        # deploy nft sink which does not support receiver interface
        Sink.deploy({"from": owner})
        if destination_account == "sink"
        else
        # deploy proper nft receiver
        TokenReceiverErc721.deploy({"from": owner})
    )
    other_accounts = accounts[4:]

    def transfer(_from, _to, _tokenId, *args):
        fun = transfer_function_type(transfer_type, erc721_token)
        if if_data:
            return fun(
                _from, _to, _tokenId, "random bytes data".encode("utf-8").hex(), *args
            )
        return fun(_from, _to, _tokenId, *args)

    # mint nft token
    erc721_token.mint(0, "uri-0", {"from": owner})
    erc721_token.mint(1, "uri-1", {"from": owner})
    erc721_token.mint(2, "uri-2", {"from": owner})
    erc721_token.mint(3, "uri-3", {"from": owner})
    erc721_token.mint(4, "uri-4", {"from": owner})

    assert erc721_token.balanceOf(owner.address, {"from": owner}) == 5
    assert (
        erc721_token.balanceOf(other_accounts[1].address, {"from": other_accounts[1]})
        == 0
    )

    # 1. test NFT transfer by token owner
    tx = transfer(owner.address, destination.address, 0, {"from": owner})
    event = tx.events["Transfer"]
    assert event["_from"] == owner.address
    assert event["_to"] == destination.address
    assert event["_tokenId"] == 0
    assert erc721_token.ownerOf(0, {"from": owner}) == destination.address
    assert erc721_token.balanceOf(owner.address, {"from": owner}) == 4
    assert erc721_token.balanceOf(destination.address, {"from": destination}) == 1
    assert erc721_token.totalSupply({"from": accounts[0]}) == 5

    # 2a. give approve for transfer single token
    tx = erc721_token.approve(approved_account.address, 1, {"from": owner})
    approval = tx.events["Approval"]
    assert approval["_owner"] == owner.address
    assert approval["_approved"] == approved_account.address
    assert approval["_tokenId"] == 1
    assert (
        erc721_token.getApproved(1, {"from": destination}) == approved_account.address
    )

    with brownie.reverts("Sender not allowed or owned"):
        transfer(owner.address, destination.address, 1, {"from": other_accounts[0]})

    # 2b. test transfer by approved address
    tx = transfer(owner.address, destination.address, 1, {"from": approved_account})
    event = tx.events["Transfer"]
    assert event["_from"] == owner.address
    assert event["_to"] == destination.address
    assert event["_tokenId"] == 1
    assert erc721_token.ownerOf(1, {"from": owner}) == destination.address
    assert erc721_token.balanceOf(owner.address, {"from": owner}) == 3
    assert erc721_token.balanceOf(destination.address, {"from": destination}) == 2
    assert erc721_token.getApproved(1, {"from": destination}) == brownie.ZERO_ADDRESS

    # 3a. set operator to transfer
    with brownie.reverts("Sender not allowed or owned"):
        transfer(owner.address, destination.address, 2, {"from": operator_account})

    tx = erc721_token.setApprovalForAll(operator_account.address, True, {"from": owner})
    approval = tx.events["ApprovalForAll"]
    assert approval["_owner"] == owner.address
    assert approval["_operator"] == operator_account.address
    assert approval["_approved"] == True  # noqa

    # 3b. test transfer by operator address
    tx = transfer(owner.address, destination.address, 2, {"from": operator_account})
    event = tx.events["Transfer"]
    assert event["_from"] == owner.address
    assert event["_to"] == destination.address
    assert event["_tokenId"] == 2
    assert erc721_token.ownerOf(2, {"from": owner}) == destination.address
    assert erc721_token.balanceOf(owner.address, {"from": owner}) == 2
    assert erc721_token.balanceOf(destination.address, {"from": destination}) == 3

    tx = transfer(owner.address, destination.address, 3, {"from": operator_account})
    event = tx.events["Transfer"]
    assert event["_from"] == owner.address
    assert event["_to"] == destination.address
    assert event["_tokenId"] == 3
    assert erc721_token.ownerOf(3, {"from": owner}) == destination.address
    assert erc721_token.balanceOf(owner.address, {"from": owner}) == 1
    assert erc721_token.balanceOf(destination.address, {"from": destination}) == 4

    # 4. set approved address by operator and make transfer
    approved_account = other_accounts[-1]

    with brownie.reverts("Not allowed sender"):
        erc721_token.approve(approved_account.address, 4, {"from": other_accounts[-2]})

    erc721_token.approve(approved_account.address, 4, {"from": operator_account})
    tx = transfer(owner.address, destination.address, 4, {"from": approved_account})
    event = tx.events["Transfer"]
    assert event["_from"] == owner.address
    assert event["_to"] == destination.address
    assert event["_tokenId"] == 4
    assert erc721_token.ownerOf(4, {"from": owner}) == destination.address
    assert erc721_token.balanceOf(owner.address, {"from": owner}) == 0
    assert erc721_token.balanceOf(destination.address, {"from": destination}) == 5
    assert erc721_token.totalSupply({"from": accounts[0]}) == 5


def test_safe_transfer_to_sink_contract(erc721_token):
    owner = accounts[0]
    erc721_token.mint(0, "uri-0", {"from": owner})

    # deploy nft sink which does not support receiver interface
    destination = Sink.deploy({"from": owner})

    with brownie.reverts("Unsupported token receiver"):
        erc721_token.safeTransferFrom(
            owner.address, destination.address, 0, {"from": owner}
        )


def test_token_against_erc165(erc721_token):
    # check ERC165
    assert erc721_token.supportsInterface("0x01ffc9a7", {"from": accounts[0]})

    # check IMetadataErc721
    id = 0x06FDDE03 ^ 0x95D89B41 ^ 0xC87B56DD
    assert erc721_token.supportsInterface(
        "0x" + id.to_bytes(4, "big").hex(), {"from": accounts[0]}
    )

    # check IErc721
    assert erc721_token.supportsInterface("0x80ac58cd", {"from": accounts[0]})
