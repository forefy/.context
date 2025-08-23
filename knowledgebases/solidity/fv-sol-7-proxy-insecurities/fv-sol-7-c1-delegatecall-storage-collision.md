# FV-SOL-7-C1 delegatecall Storage Collision

## TLDR

`delegatecall` is a function call that allows a contract to run code from another contract while preserving the original caller's context, including storage, `msg.sender`, and `msg.value`

Since `delegatecall` runs in the storage context of the caller, if the contract calls `delegatecall` on user-supplied input, an attacker can input an address to a malicious contract that can manipulate the storage of the calling contract, potentially overwriting sensitive variables or stealing funds

If the target contract has a different storage layout, it may overwrite or corrupt crucial storage variables in the calling contract.

## Game

In this setup, the `ProxyContract` delegates all calls to `LogicContract` using `delegatecall`.

What could possibly go wrong.

## Sections
### Code
```solidity
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

    // Fallback function that forwards calls to the implementation contract
    fallback() external payable {
        (bool success, ) = implementation.delegatecall(msg.data);
        require(success, "Delegatecall failed");
    }
}
```


### Hint 1
`delegatecall` executes code in the context of the calling contract’s storage, meaning the storage layout must be identical between proxy and implementation.

Consider how `data` and `implementation` might share the same storage slot.


### Hint 2
Using a specific storage slot layout or reserved storage pattern can help avoid storage collisions. Look into how to separate the proxy's storage from the implementation's storage.


### Solution
```solidity
contract ProxyContract {
    // Fix: Use a unique storage slot for the implementation address
    bytes32 private constant implementationSlot = keccak256("proxy.implementation.address");

    constructor(address _implementation) {
        setImplementation(_implementation);
    }

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


