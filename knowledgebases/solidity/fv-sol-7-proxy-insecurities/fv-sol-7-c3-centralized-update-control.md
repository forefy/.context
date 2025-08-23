# FV-SOL-7-C3 Centralized Update Control

## TLDR

If the upgrade process is too centralized, it creates a single point of failure, and generally considered unethical to the users

## Game

Web3 does not like centralized stuff. What are the risks in this contract?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract CentralizedProxy {
    address public implementation;
    address public admin;

    constructor(address _implementation) {
        implementation = _implementation;
        admin = msg.sender;
    }

    function updateImplementation(address newImplementation) public {
        require(msg.sender == admin, "Only admin can update the implementation");
        implementation = newImplementation;
    }

    // Fallback function that forwards calls to the implementation contract
    fallback() external payable {
        (bool success, ) = implementation.delegatecall(msg.data);
        require(success, "Delegatecall failed");
    }
}
```


### Hint 1
Consider how decentralizing control over updates or requiring multiple approvals could mitigate the risk of a single point of failure.


### Hint 2
Multi-signature wallets or decentralized governance mechanisms are common solutions for critical operations that need more security and transparency.


### Solution
```solidity
contract DecentralizedProxy {
    address public implementation;
    address public admin;

    constructor(address _implementation, address _admin) {
        implementation = _implementation;
        admin = _admin; // Fix: Set multi-signature wallet or governance contract as the admin
    }

    function updateImplementation(address newImplementation) public {
        require(msg.sender == admin, "Only admin (multi-sig) can update the implementation");
        implementation = newImplementation;
    }

    fallback() external payable {
        (bool success, ) = implementation.delegatecall(msg.data);
        require(success, "Delegatecall failed");
    }
}
```


