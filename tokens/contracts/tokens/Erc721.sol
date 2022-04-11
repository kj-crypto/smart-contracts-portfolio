// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '../generic/IErc721.sol';
import {Strings, checkIfContract, Erc165} from '../Utils.sol';
import '../generic/IErc165.sol';

contract MetadataErc721 is IMetadataErc721 {
    using Strings for string;

    string private _name;
    string private _symbol;
    mapping (uint256 => string) internal tokenURIs;

    constructor(string memory __name, string memory __symbol) {
        _name = __name;
        _symbol = __symbol;
    }

    function name() public view returns(string memory) {
        return _name;
    }

    function symbol() public view returns(string memory) {
        return _symbol;
    }

    function tokenURI(uint256 _tokenId) public view returns(string memory) {
        string memory uri = tokenURIs[_tokenId];
        require(uri.len() > 0, 'Invalid token ID');
        return uri;
    }
}

abstract contract MintableErc721 {
    mapping (address => bool) private _addressesAllowedToMint;

    constructor() {
        _addressesAllowedToMint[msg.sender] = true;
    }

    modifier allowedSender() {
        require(_addressesAllowedToMint[msg.sender], 'Sender is not allowed to perform this operation');
        _;
    }

    function addMinter(address minter_address) public allowedSender() {
        _addressesAllowedToMint[minter_address] = true;
    }

    function banMinter(address minter_address) public allowedSender() {
        _addressesAllowedToMint[minter_address] = false;
    }

    function checkIfAllowedToMint(address _address) public view returns(bool) {
        return _addressesAllowedToMint[_address];
    }

    function mint(uint256 tokenId, string memory tokenURI) public virtual;
}

contract Erc721 is
IErc721,
MintableErc721,
MetadataErc721,
Erc165
{
    using Strings for string;

    // todo move to enumerable interface
    uint256 public totalSupply;

    mapping (address => uint256) balances;

    // mapping of tokenId into owner address
    mapping (uint256 => address) owners;

    // approvals for single token
    mapping (uint256 => address) private _tokenApprovals;

    // approvals for external contract/EOA, called `operators`, to manipulate all tokens belonging to particular owner
    mapping (address => mapping (address => bool)) private _operatorApprovals;

    constructor(string memory _name, string memory _symbol) MetadataErc721(_name, _symbol) {
        super.registerInterfaceID(IErc165.supportsInterface.selector);
        super.registerInterfaceID(
            IMetadataErc721.name.selector ^
            IMetadataErc721.symbol.selector ^
            IMetadataErc721.tokenURI.selector
        );
        super.registerInterfaceID(
            IErc721.balanceOf.selector ^
            IErc721.ownerOf.selector ^

            // overload function cannot use selector
            bytes4(keccak256('safeTransferFrom(address,address,uint256,bytes)')) ^
            bytes4(keccak256('safeTransferFrom(address,address,uint256)')) ^

            IErc721.transferFrom.selector ^
            IErc721.approve.selector ^
            IErc721.getApproved.selector ^
            IErc721.setApprovalForAll.selector ^
            IErc721.isApprovedForAll.selector
        );
    }

    function mint(uint256 _tokenId, string memory _tokenURI) public allowedSender() override(MintableErc721) {
        require(_tokenURI.len() > 0, 'URI cannot be empty');
        require(tokenURIs[_tokenId].len() == 0, 'Token already exists');

        tokenURIs[_tokenId] = _tokenURI;
        owners[_tokenId] = msg.sender;
        balances[msg.sender]++;
        emit Transfer(address(0), msg.sender, _tokenId);

        totalSupply++;
    }

    function balanceOf(address _owner) public view returns(uint256) {
        require(_owner != address(0), 'Wrong owner address');
        return balances[_owner];
    }

    function ownerOf(uint256 _tokenId) public view returns(address) {
        address _owner = owners[_tokenId];
        require(_owner != address(0), 'Invalid token ID');
        return _owner;
    }

    function _checksBeforeTransfer(address _from, address _to, uint256 _tokenId) private view {
        // check token ID
        address _owner = ownerOf(_tokenId);

        // check ownership of message sender
        require(
            _owner == msg.sender ||
            _tokenApprovals[_tokenId] == msg.sender ||
            _operatorApprovals[_owner][msg.sender],
            'Sender not allowed or owned'
        );

        require(_owner == _from,'Source address not an owner');
        require(_to != address(0), 'Wrong destination address');
    }

    function _transfer(address _from, address _to, uint256 _tokenId) private {
        owners[_tokenId] = _to;
        balances[_from]--;
        balances[_to]++;

        emit Transfer(_from, _to, _tokenId);

        // clear token approvals mapping
        _tokenApprovals[_tokenId] = address(0);
    }

    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes memory _data) public {
        _checksBeforeTransfer(_from, _to, _tokenId);

        if(checkIfContract(_to)) {
            IErc721TokenReceiver receiver = IErc721TokenReceiver(_to);
            try receiver.onERC721Received(
                msg.sender,
                owners[_tokenId],
                _tokenId,
                _data
            ) returns(bytes4 result) {
                require(result == IErc721TokenReceiver.onERC721Received.selector, 'Unsupported token receiver');
            }
            catch {
                revert('Unsupported token receiver');
            }
        }

        _transfer(_from, _to, _tokenId);
    }

    function safeTransferFrom(address _from, address _to, uint256 _tokenId) public {
        safeTransferFrom(_from, _to, _tokenId, '');
    }

    function transferFrom(address _from, address _to, uint256 _tokenId) public {
        /**
        External caller of this function take responsibility of checking
        if `_to` address can handle NFT token,
        otherwise it can be permanently locked
        */
        _checksBeforeTransfer(_from, _to, _tokenId);
        _transfer(_from, _to, _tokenId);
    }

    function approve(address _approved, uint256 _tokenId) public {
        address _owner = ownerOf(_tokenId);
        require(_owner == msg.sender || _operatorApprovals[_owner][msg.sender], 'Not allowed sender');
        _tokenApprovals[_tokenId] = _approved;
        emit Approval(_owner, _approved, _tokenId);
    }

    function getApproved(uint256 _tokenId) public view returns(address) {
        // check if tokenId has ownership, if not then isn't valid one
        ownerOf(_tokenId);
        return _tokenApprovals[_tokenId];
    }

    function setApprovalForAll(address _operator, bool _approved) public {
        require(_operator != address(0), 'Wrong operator address');
        _operatorApprovals[msg.sender][_operator] = _approved;
        emit ApprovalForAll(msg.sender, _operator, _approved);
    }

    function isApprovedForAll(address _owner, address _operator) public view returns(bool) {
        return _operatorApprovals[_owner][_operator];
    }
}
