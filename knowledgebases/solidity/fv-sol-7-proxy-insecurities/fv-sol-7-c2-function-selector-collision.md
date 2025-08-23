# FV-SOL-7-C2 Function Selector Collision

## TLDR

When two functions in the implementation contract have the same function selector, unintended functions can be called, leading to incorrect behavior or security loopholes

## Game

This proxy implements a function with a selector that could potentially collide with implementation contract functions.

## Sections
### Code
```solidity

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LogicContract {
    uint256 public data;

    function setData(uint256 _data) public {
        data = _data;
    }
}

contract ProxyContract {
    address public implementation;

    constructor(address _implementation) {
        implementation = _implementation;
    }

    function setImplementation(address _implementation) public {
        implementation = _implementation;
    }

    // Fallback function that forwards calls to the implementation contract
    fallback() external payable {
        (bool success, ) = implementation.delegatecall(msg.data);
        require(success, "Delegatecall failed");
    }
}
```


### Hint 1
The function selector is determined by the first four bytes of the hashed function signature.&#x20;

Think about what happens if a call intended for `LogicContract` accidentally matches a function in `ProxyContract`.


### Hint 2
Using a specific interface structure can help avoid accidental selector collisions between proxy and implementation.

Look into ways to segregate function selectors in proxy and implementation contracts.


### Solution
```solidity
contract ProxyContract {
    bytes32 private constant implementationSlot = keccak256("proxy.implementation.address");

    constructor(address _implementation) {
        setImplementation(_implementation);
    }
    
    // Fix: setImplementation is now internal to block collisions
    function setImplementation(address _implementation) internal {
        assembly {
            sstore(implementationSlot, _implementation)
        }
    }

    function getImplementation() public view returns (address impl) {
        assembly {
            impl := sload(implementationSlot)
        }
    }

    // Fallback function that forwards calls to the implementation contract
    fallback() external payable {
        address impl = getImplementation();
        require(impl != address(0), "Implementation not set");

        (bool success, ) = impl.delegatecall(msg.data);
        require(success, "Delegatecall failed");
    }
}
```


