// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import '@openzeppelin/contracts/token/ERC20/ERC20.sol';


contract LinkToken is ERC20 {

    constructor() ERC20("ChainLink Token", "LINK") {
        _mint(msg.sender, 10**27);
    }

    function decimals() public view override returns (uint8) {
        return 18;
    }

    function transferAndCall(address _to, uint _value, bytes memory _data)
        public
        validRecipient(_to)
        returns (bool)
    {
        approve(_to, _value);
        (bool success,) = _to.call(
            abi.encodePacked(
                bytes4(keccak256("onTokenTransfer(address,uint256,bytes)")),
                msg.sender,
                _value,
                _data
            )
        );
        return success;
    }

  // MODIFIERS

  modifier validRecipient(address _recipient) {
    require(_recipient != address(0) && _recipient != address(this));
    _;
  }

}
