// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '../generic/IErc20.sol';
import {ITokenFallback} from '../generic/IErc223.sol';
import {Erc165} from '../Utils.sol';
import {IErc721TokenReceiver} from '../generic/IErc721.sol';
import '../generic/IErc165.sol';

contract TokenReceiver {
    // method which allows for withdraw tokens transferred to contract
    function withdraw(IErc20 token, address _to) public {
        token.transfer(_to, token.balanceOf(address(this)));
    }
}

contract TokenReceiverErc223 is ITokenFallback {
    function tokenFallback(address _from, uint256 _amount, bytes memory _data) public {

    }
}

contract TokenReceiverErc721 is Erc165, IErc721TokenReceiver {
    constructor() {
        super.registerInterfaceID(IErc165.supportsInterface.selector);
        super.registerInterfaceID(IErc721TokenReceiver.onERC721Received.selector);
    }

    function onERC721Received(address _operator, address _from, uint256 _tokenId, bytes memory _data) public pure returns(bytes4) {
        return IErc721TokenReceiver.onERC721Received.selector;
    }

}
