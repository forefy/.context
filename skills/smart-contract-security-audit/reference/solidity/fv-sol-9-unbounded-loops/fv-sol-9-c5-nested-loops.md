# FV-SOL-9-C5 Nested Loops

## TLDR

Nested loops are particularly costly because the gas cost grows exponentially with each layer of nesting. This is especially problematic when the loop conditions are based on user data or dynamic array lengths

## Game

Can the contract handle large datasets, or will it crumble under its own weight?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract NestedLoopsGame {
    mapping(address => uint256[]) public userRewards;

    // Function to calculate and sum up rewards across tiers
    function calculateTotalRewards(address[] memory users) public view returns (uint256) {
        uint256 totalRewards = 0;

        for (uint256 i = 0; i < users.length; i++) {
            uint256[] memory rewards = userRewards[users[i]];

            for (uint256 j = 0; j < rewards.length; j++) {
                totalRewards += rewards[j];
            }
        }

        return totalRewards;
    }
}
```


### Hint 1
Consider how the combination of `users` and their reward arrays affects the gas cost. What happens as the dataset grows larger?


### Hint 2
Think about ways to process or precompute data to avoid iterating through everything in real-time.


### Solution
```solidity
contract NestedLoopsGame {
    mapping(address => uint256[]) public userRewards;
    mapping(address => uint256) public precomputedTotals; // Fix: Store precomputed totals

    function addReward(address user, uint256 reward) public {
        userRewards[user].push(reward);
        precomputedTotals[user] += reward; // Fix: Update total during addition
    }
    
    function calculateTotalRewards(address[] memory users) public view returns (uint256) {
        uint256 totalRewards = 0;

        for (uint256 i = 0; i < users.length; i++) {
            totalRewards += precomputedTotals[users[i]]; // Fix: Use precomputed totals
        }

        return totalRewards;
    }
}
```


