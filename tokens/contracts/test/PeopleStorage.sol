// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
Simple storage of people, containg their name and age
Requirements name cannot be longer than 255 chars
*/

import '../generic/IErc20.sol';
import '../generic/IErc677.sol';
import {BytesToUint} from '../Utils.sol';

struct Person {
    string name;
    uint256 age;
}

contract PeopleStorage {
    // default getter does not return whole array, but sinlge item
    Person[] public people;
    IErc20 token;
    uint256 public immutable storageCost;

    constructor(IErc20 _token, uint256 _storageCost) {
        token = _token;
        storageCost = _storageCost;
    }

    function getAllPeople() public view returns(Person[] memory) {
        return people;
    }

    function freeStore(string memory name, uint256 age) public {
        people.push(
            Person(
                name,
                age
            )
        );
    }

    function payForStore(string memory name, uint256 age) public {
        token.transferFrom(msg.sender, address(this), storageCost);
        people.push(Person(name, age));
    }
}

contract PeopleStorageErc677 is PeopleStorage, IErc677Receiver {
    using BytesToUint for bytes1;

    constructor(IErc20 _token, uint256 _storageCost)
    PeopleStorage(_token, _storageCost) {}

    function onTokenTransfer(address from, uint256 amount, bytes calldata data) public {
        /**
        Structure of data is following
        1-byte of flag, 0 - will raise error, 1 - will pass
        1-byte of the person age, age from 1 - 255
        n-byte of the person name
        */

        require(data.length >= 3, 'Wrong data format');
        require(amount == storageCost, 'Amount differs from storage cost');

        // check flag
        uint256 flag = data[0].toUint256();
        require(flag == 1, 'Wrong flag');

        // get age
        uint256 age = data[1].toUint256();

        // get name
        // use explict type conversion from array slice to bytes because
        // the string(data[2:]) raises internal compilation error
        string memory name = string(bytes(data[2:]));

        token.transferFrom(from, address(this), amount);
        people.push(Person(name, age));
    }
}
