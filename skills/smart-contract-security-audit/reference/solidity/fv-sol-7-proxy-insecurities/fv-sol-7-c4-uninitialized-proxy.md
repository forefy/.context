# FV-SOL-7-C4 Uninitialized Proxy

## TLDR

If the initializer function isn’t called during deployment, it may leave critical variables in an unprotected state

Same goes for accidentally allowing initializer functions to be called again in the proxy pattern which can result in re-initializing the contract, doing so gaining ability to modify data.

## Game

This proxy has a constructor to initialize the implementation address, but if the proxy is deployed without properly initializing this address, it could end up with an uninitialized state.

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract Proxy {
    address public implementation;

    // Constructor to set the implementation address
    constructor(address _implementation) {
        implementation = _implementation;
    }

    // Fallback function to forward calls to the implementation contract
    fallback() external payable {
        (bool success, ) = implementation.delegatecall(msg.data);
        require(success, "Delegatecall failed");
    }
}
```


### Hint 1
Consider what could happen if the `implementation` address is not properly set before `delegatecall` is used. How can you ensure that the proxy is correctly initialized?


### Hint 2
Look into adding a guard that checks if `implementation` has a valid address before proceeding with any calls.


### Solution
```solidity
fallback() external payable {
    require(implementation != address(0), "Implementation not initialized"); // Fix: Ensure implementation is set
    (bool success, ) = implementation.delegatecall(msg.data);
    require(success, "Delegatecall failed");
}
```


