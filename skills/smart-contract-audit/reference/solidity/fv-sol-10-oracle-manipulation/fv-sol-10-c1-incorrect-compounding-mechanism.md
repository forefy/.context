# FV-SOL-10-C1 Incorrect Compounding Mechanism

## TLDR

The oracle fails to compound APR (Annual Percentage Rate) correctly over time, resulting in values that do not accurately reflect the cumulative growth intended

## Game

What happens if the oracle reports incorrect values at the wrong moments?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IPriceOracle {
    function getPrice() external view returns (uint256);
}

contract CompoundingMechanismGame {
    IPriceOracle public oracle;
    uint256 public totalValue;
    uint256 public interestRate = 5; // 5% annual interest

    constructor(address _oracle, uint256 _initialValue) {
        oracle = IPriceOracle(_oracle);
        totalValue = _initialValue;
    }

    // Compound the value based on oracle price
    function compound() public {
        uint256 price = oracle.getPrice();
        uint256 interest = (totalValue * interestRate * price) / (100 * 1e18); // Compounding logic
        totalValue += interest;
    }
}
```


### Hint 1
If an attacker can manipulate the oracle, how might they inflate or deflate the calculated `interest` in the `compound` function?


### Hint 2
Consider how to validate the oracle’s data to prevent reliance on potentially manipulated values.


### Solution
```solidity
uint256 public lastPrice;

function compound() public {
    uint256 currentPrice = oracle.getPrice();
    require(currentPrice > 0, "Invalid price"); // Fix: Check for valid oracle data
    require(
        currentPrice <= lastPrice * 2 && currentPrice >= lastPrice / 2,
        "Unrealistic price change" // Fix: Sanity check for sudden changes
    );

    uint256 interest = (totalValue * interestRate * currentPrice) / (100 * 1e18);
    totalValue += interest;
    lastPrice = currentPrice; // Fix: Update lastPrice for future checks
}
```


