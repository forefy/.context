# FV-SOL-6-C1 Unchecked Call Return

## TLDR

functions like `delegatecall`, `call`, `staticcall`, `send`, and external contract function calls fail but return values go unchecked, leading to unintended state changes, lost funds, or incorrect assumptions about success

## Game

Look for unchecked low level calls

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract UncheckedCallGame {
    address public targetContract;

    constructor(address _targetContract) {
        targetContract = _targetContract;
    }

    function executeExternalCall(bytes memory data) public {
        targetContract.call(data);
    }
}
```


### Hint 1
Low-level calls (`call`) do not automatically revert if they fail. Consider how you might confirm that the `call` succeeded before allowing the function to proceed.


### Hint 2
Use the return values from `call` to check if the external call succeeded and take appropriate action if it didn’t.


### Solution
```solidity
function executeExternalCall(bytes memory data) public {
    (bool success, ) = targetContract.call(data);
    require(success, "External call failed"); // Fix: Check the success of the call
}
```


