//SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/access/Ownable.sol";


contract Multisig is Ownable {

    mapping(address => bool) public isWalletSigner;
    address[] public walletSigners;
    uint256 public N;
    uint256 public M;
    address[] public approved;

    constructor(uint256 _N, uint256 _M) {
        require(_N > 0 && _M > 0 && _M >= _N, 'Wrong N of M');
        N = _N;
        M = _M;
    }

    receive() external payable {}

    function addSigner(address signer) public onlyOwner {
        if(!isWalletSigner[signer]) {
            isWalletSigner[signer] = true;
            walletSigners.push(signer);
        }
    }

    function approve() public {
        approved.push(msg.sender);
    }

    function _checkNofM() private returns(bool) {
        if(walletSigners.length != M)
            return false;

        if(approved.length < N)
            return false;

        uint256 counter = 0;
        for(uint256 i = 0; i < approved.length; i++) {
            if(counter == N) {
                return true;
            }
            if(isWalletSigner[approved[i]]) {
                counter++;
            }
        }
        if(counter == N) {
            return true;
        }
        return false;
    }

    function transferEth(address payable to, uint256 amount) public {
        require(address(this).balance >= amount, 'Not enough funds');
        require(_checkNofM(), 'Wrong N of M signers');
        to.transfer(amount);
        approved = new address[](0);
    }
}
