# FV-SOL-6-C6 False Contract Existence Assumption

## TLDR

If a contract does not verify that an external address is a valid contract, it may perform operations under the incorrect assumption that the contract exists, risking failed calls.

## Game

What assumptions can be false?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IExternalContract {
    function performAction() external;
}

contract ExistenceAssumptionGame {
    address public externalContractAddress;

    constructor(address _externalContractAddress) {
        externalContractAddress = _externalContractAddress;
    }

    // Function that assumes the address is a valid contract and calls a function on it
    function executeAction() public {
        IExternalContract(externalContractAddress).performAction();
    }
}
```


### Hint 1
Consider how you might confirm that an address actually points to a contract before attempting to call a function on it.

Solidity provides certain tools to help verify contract existence.


### Hint 2
Checking if code exists at `externalContractAddress` can help determine if the address points to a contract or an EOA.


### Solution
```solidity
function executeAction() public {
    require(isContract(externalContractAddress), "Address is not a contract"); // Fix: Check if address is a contract
    IExternalContract(externalContractAddress).performAction();
}

// New function
function isContract(address addr) internal view returns (bool) {
    uint256 size;
    assembly { size := extcodesize(addr) }
    return size > 0;
}
```


