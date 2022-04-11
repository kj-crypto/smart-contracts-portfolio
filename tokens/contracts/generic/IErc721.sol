// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// NFT interfaces

interface IMetadataErc721 {
    function name() external view returns(string memory);
    function symbol() external view returns(string memory);
    function tokenURI(uint256 _tokenId) external view returns(string memory);
}

interface IErc721 {
    event Transfer(address _from, address _to, uint256 _tokenId);
    event Approval(address _owner, address _approved, uint256 _tokenId);
    event ApprovalForAll(address _owner, address _operator, bool _approved);

    function balanceOf(address _owner) external view returns(uint256);
    function ownerOf(uint256 _tokenId) external view returns(address);
    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes memory _data) external;
    function safeTransferFrom(address _from, address _to, uint256 _tokenId) external;
    function transferFrom(address _from, address _to, uint256 _tokenId) external;
    function approve(address _approved, uint256 _tokenId) external;
    function getApproved(uint256 _tokenId) external view returns(address);
    function setApprovalForAll(address _operator, bool _approved) external;
    function isApprovedForAll(address _owner, address _operator) external view returns(bool);
}

interface IErc721TokenReceiver {
   function onERC721Received(address _operator, address _from, uint256 _tokenId, bytes memory _data) external returns(bytes4);
}
