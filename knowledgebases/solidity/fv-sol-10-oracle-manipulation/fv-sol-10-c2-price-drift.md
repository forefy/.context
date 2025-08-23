# FV-SOL-10-C2 Price Drift

## TLDR

Due to improper state updates, the `oraclePrice` "drifts" back to its initial value rather than incrementally increasing

## Game

The system assumes the oracle price remains accurate, but what if the price drifts slowly over time? Can you spot how this could lead to long-term exploitation?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IPriceOracle {
    function getPrice() external view returns (uint256);
}

contract PriceDriftGame {
    IPriceOracle public oracle;
    uint256 public totalValue;

    constructor(address _oracle, uint256 _initialValue) {
        oracle = IPriceOracle(_oracle);
        totalValue = _initialValue;
    }

    // Update value based on oracle price
    function updateValue() public {
        uint256 price = oracle.getPrice();
        require(price > 0, "Invalid price");
        totalValue = totalValue * price / 1e18; // Adjust value based on price
    }
}

```


### Hint 1
Imagine the oracle’s price slowly drifts away from reality over time. How might this impact the `totalValue` calculation?


### Hint 2
Can you cross-verify the price with another source or use a mechanism to ensure the price remains reliable?


### Solution
```solidity
uint256 public lastValidPrice;

function updateValue() public {
    uint256 price = oracle.getPrice();
    require(price > 0, "Invalid price");

    // Fix: Validate against last valid price to detect drift
    require(
        price <= lastValidPrice * 105 / 100 && price >= lastValidPrice * 95 / 100,
        "Detected price drift"
    );

    totalValue = totalValue * price / 1e18;
    lastValidPrice = price; // Fix: Update last valid price
}
```


