# FV-SOL-5-C2 Incorrect Conditionals

## TLDR

Results from incorrect conditions in `if` statements, loops, or switches, causing unintended branching in code execution

e.g. a function meant to handle reward calculation might incorrectly check for `block.number >= lastRewardBlock` instead of `block.number > lastRewardBlock`, causing rewards to be skipped or duplicated

## Game

Can you identify how this contract might cause certain balances to yield unexpected rewards?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract IncorrectConditionalsGame {
    uint256 public reward;

    // Function to calculate rewards based on balance
    function calculateReward(uint256 balance) public {
        if (balance > 100) {
            reward = 10;
        } else if (balance > 500) {
            reward = 50;
        } else {
            reward = 0;
        }
    }
}
```


### Hint 1
Consider the order in which each condition is evaluated. Are any conditions unreachable or incorrectly prioritized?


### Hint 2
Pay attention to the range of balances and whether each condition logically captures the correct range for each reward tier.


### Solution
```solidity
function calculateReward(uint256 balance) public {
    if (balance > 500) { // Fix: Check for higher balance first
        reward = 50;
    } else if (balance > 100) {
        reward = 10;
    } else {
        reward = 0;
    }
}
```


