# FV-SOL-6-C4 False Positive Success Assumption

## TLDR

The contract assumes a function call succeeded without verifying, potentially leading to state inconsistencies or incorrect balance assumptions if the call actually failed.

## Game

What's wrong with the assumptions made by this contracts author?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IExternalContract {
    function doSomething() external returns (bool);
}

contract FalsePositiveGame {
    IExternalContract public externalContract;

    constructor(address _externalContract) {
        externalContract = IExternalContract(_externalContract);
    }

    // Function that assumes success without verifying
    function executeAction() public {
        bool success = externalContract.doSomething();
        if (!success) {
            // Assume the action succeeded
        }
        // Continue execution assuming the external call succeeded
    }
}
```


### Hint 1
Consider what would happen if `doSomething` returns `false`. How does `executeAction` handle this outcome?

Does it account for failure explicitly, or does it continue regardless?


### Hint 2
Think about how you might use the `require` or `revert` statements to enforce stricter handling of failure cases.


### Solution
```solidity
function executeAction() public {
    bool success = externalContract.doSomething();
    require(success, "External action failed"); // Fix: Explicitly require success
}
```


