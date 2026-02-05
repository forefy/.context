# FV-SOL-6-C5 Partial Execution with No Rollback

## TLDR

When a function call fails mid-function, the contract may continue execution without rolling back previous changes, leading to partial, unintended state changes.

## Game

Imagine a contract that performs a series of critical operations, one of which involves an external call to another contract. What is missing here?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IExternalContract {
    function doAction() external returns (bool);
}

contract PartialExecutionGame {
    IExternalContract public externalContract;
    uint256 public balance;

    constructor(address _externalContract) {
        externalContract = IExternalContract(_externalContract);
    }

    // Function that performs a sequence of operations, including an unchecked external call
    function executeSequence(uint256 amount) public {
        balance += amount; // Step 1: Increase balance
        bool success = externalContract.doAction(); // Step 2: External call
        if (!success) {
            balance -= amount; // Attempt to revert manually, but this is partial
        }
    }
}
```


### Hint 1
Consider what would happen if `doAction` fails.

Is the `balance` effectively rolled back, and does the contract return to a fully consistent state?


### Hint 2
A more reliable approach might involve enforcing that all steps succeed or none at all, using a mechanism to revert the entire transaction on failure.


### Solution
```solidity
function executeSequence(uint256 amount) public {
    balance += amount; // Step 1: Increase balance
    bool success = externalContract.doAction(); 
    require(success, "External action failed"); // Fix: Revert the entire transaction on failure
}
```


