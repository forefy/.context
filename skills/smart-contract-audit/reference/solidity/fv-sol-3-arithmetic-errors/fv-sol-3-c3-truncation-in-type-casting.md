# FV-SOL-3-C3 Truncation in Type Casting

## TLDR

When casting from a larger integer type to a smaller one, data can be truncated, resulting in a different value than intended

For example, assigning a `uint256` value to a `uint8` variable without validating that it fits

## Game

Someone did a crazy downcast on this code.

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract TruncationGame {
    uint256 public totalPoints;

    // Function to add points based on a reward calculation
    function addPoints(uint256 reward) public {
        // Assume reward is calculated externally and cast to uint16
        uint16 truncatedReward = uint16(reward);
        totalPoints += truncatedReward;
    }
}

```


### Hint 1
What value will `truncatedReward` actually hold?


### Hint 2
Consider what happens if `reward` is a large number, such as `70000`, and is then cast to `uint16`


### Solution
```solidity
function addPoints(uint256 reward) public {
    require(reward <= type(uint16).max, "Reward exceeds uint16 range"); // Fix: Safe to cast after check
    uint16 truncatedReward = uint16(reward); 
    totalPoints += truncatedReward;
}

```


