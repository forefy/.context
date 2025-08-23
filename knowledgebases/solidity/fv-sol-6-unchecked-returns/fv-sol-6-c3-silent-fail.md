# FV-SOL-6-C3 Silent Fail

## TLDR

A function call fails without detection, and continues executing as if it succeeded, which can create an invalid or inconsistent state.

## Game

Silent fails are scary and can be unpredictable. can you find what can cause a silent fail here?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IExternalContract {
    function performAction() external returns (bool);
}

contract SilentFailGame {
    IExternalContract public externalContract;

    constructor(address _externalContract) {
        externalContract = IExternalContract(_externalContract);
    }

    function callExternalAction() public {
        externalContract.performAction();
    }
}
```


### Hint 1
Consider the return type of `performAction` and whether ignoring it might cause issues. How can you confirm that the function actually succeeded?


### Hint 2
Adding a check on the return value can help ensure that you handle failures explicitly rather than assuming success.


### Solution
```solidity
function callExternalAction() public {
    bool success = externalContract.performAction();
    require(success, "External action failed"); // Fix: Check return value to catch failure
}
```


