# FV-SOL-5-C1 Boundary Misalignment

## TLDR

Occurs when code fails to respect predefined boundaries or intervals (e.g., epochs, time windows, thresholds)

## Game

Examine how `setRewardTier` assigns reward tiers based on the `score` value. Can you identify any boundary misalignments in the conditions that might cause scores on the boundary to be assigned incorrectly?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract BoundaryMisalignmentGame {
    uint256 public rewardTier;

    // Function to assign a reward tier based on score
    function setRewardTier(uint256 score) public {
        if (score < 50) {
            rewardTier = 1;
        } else if (score <= 100) {
            rewardTier = 2;
        } else if (score < 150) {
            rewardTier = 3;
        } else {
            rewardTier = 4;
        }
    }
}
```


### Hint 1
Pay attention to how each boundary is defined and consider what happens at the cutoff points, especially around `100` and `150`.


### Hint 2
Think about how overlapping or missing ranges could lead to certain scores being assigned to the wrong tier or skipped entirely.


### Solution
```solidity
function setRewardTier(uint256 score) public {
    if (score < 50) {
        rewardTier = 1;
    } else if (score >= 50 && score < 100) { // Fix: Adjust range to avoid overlap
        rewardTier = 2;
    } else if (score >= 100 && score < 150) { // Fix: Define range explicitly
        rewardTier = 3;
    } else {
        rewardTier = 4;
    }
}
```


