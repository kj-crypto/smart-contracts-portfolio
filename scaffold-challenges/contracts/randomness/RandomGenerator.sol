// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// based on commit-reveal pattern in
// https://github.com/scaffold-eth/scaffold-eth-examples/tree/commit-reveal-with-frontend
// and
// https://gitcoin.co/blog/commit-reveal-scheme-on-ethereum/

contract RandomNumberGenerator {

    struct Commit {
        bytes32 data;
        uint64 block_number;
        bool revealed;
    }

    mapping (address => Commit) public commits;

    uint8 public constant max = 200;

    function getHash(bytes32 data) public view returns(bytes32) {
        return keccak256(abi.encodePacked(address(this), data));
    }

    function commit(bytes32 data, uint64 block_number) public {
        require(block_number >= block.number, 'Too small block number');
        commits[msg.sender] = Commit(data, block_number, false);
    }

    function generate() public returns(uint256) {
        require(!commits[msg.sender].revealed, 'Data already revealed');
        commits[msg.sender].revealed = true;

        bytes32 blockHash = blockhash(commits[msg.sender].block_number);
        return uint256(keccak256(abi.encodePacked(blockHash, commits[msg.sender].data))) % max;
    }
}