# FV-SOL-2-C4 Division by Zero

## TLDR

**Division by zero** occurs when a divisor in a calculation unexpectedly equals zero, causing an error.

In Solidity, attempting to divide by zero results in a runtime error, which can halt the transaction and potentially lead to unintended contract behavior.

This error often arises in situations where values are derived from user input, external data, or dynamic calculations that don’t account for zero values.

## Game

Can you think of how this might be exploited if the contract doesn’t handle `totalShares` carefully?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract DivisionByZeroGame {
    uint256 public totalShares;
    mapping(address => uint256) public userContributions;

    function setTotalShares(uint256 shares) public {
        totalShares = shares;
    }

    function calculateSharePercentage(address user) public view returns (uint256) {
        uint256 userContribution = userContributions[user];
        
        // Calculate the user's percentage of total shares
        return (userContribution * 100) / totalShares;
    }
}
```


### Hint 1
Division by zero in Solidity causes the transaction to revert.


### Hint 2
Consider what happens if `totalShares` is zero when `calculateSharePercentage` is called.


### Solution
```solidity
function calculateSharePercentage(address user) public view returns (uint256) {
    uint256 userContribution = userContributions[user];
    
    // Fix: Check to prevent division by zero
    require(totalShares > 0, "Total shares must be greater than zero");

    return (userContribution * 100) / totalShares;
}
```


