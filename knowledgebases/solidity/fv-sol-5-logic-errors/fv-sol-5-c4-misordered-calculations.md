# FV-SOL-5-C4 Misordered Calculations

## TLDR

Errors from improper indexing or referencing in mappings, often due to incorrect key choices or updates

## Game

Review the calculation order in `calculateReward`

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract LogicMisorderGame {
    uint256 public finalReward;
    uint256 public constant BONUS = 50;
    uint256 public constant TAX_PERCENT = 10;

    // Function to calculate the final reward based on balance with bonus and tax applied
    function calculateReward(uint256 balance) public {
        uint256 doubledBalance = balance * 2;
        uint256 rewardWithBonus = doubledBalance + BONUS;
        finalReward = rewardWithBonus - (rewardWithBonus * TAX_PERCENT / 100);
    }
}
```


### Hint 1
Think about whether the bonus should be taxed or only the user’s balance. Should the bonus be added before or after applying the tax?


### Hint 2
Consider how adding the bonus after applying the tax might better align with the intended logic of rewarding the user’s balance.


### Solution
```solidity
function calculateReward(uint256 balance) public {
    uint256 doubledBalance = balance * 2;
    uint256 taxedBalance = doubledBalance - (doubledBalance * TAX_PERCENT / 100); // Fix: Apply tax first
    finalReward = taxedBalance + BONUS; // Add bonus after tax
}
```


