# FV-SOL-10-C4 Time Lags

## TLDR

Delaying block production or influencing the timing of price updates can lead to incorrect price feeds that attackers use to profit

## Game

You’ve come across a contract that relies on an oracle to provide time-sensitive price data. It assumes the oracle always provides up-to-date information.

But what if the oracle provides stale or outdated prices? Can you trust its time logs?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IPriceOracle {
    function getPrice() external view returns (uint256);
    function getLastUpdatedTime() external view returns (uint256);
}

contract TimeLogsGame {
    IPriceOracle public oracle;
    uint256 public totalValue;

    constructor(address _oracle, uint256 _initialValue) {
        oracle = IPriceOracle(_oracle);
        totalValue = _initialValue;
    }

    // Update total value based on oracle price
    function updateValue() public {
        uint256 price = oracle.getPrice();
        uint256 lastUpdated = oracle.getLastUpdatedTime();

        require(price > 0, "Invalid price");
        require(lastUpdated > 0, "Invalid timestamp");
        totalValue = totalValue * price / 1e18; // Adjust value based on price
    }
}
```


### Hint 1
What happens if the oracle’s `lastUpdated` timestamp is far in the past? How could this affect the validity of the `price`?


### Hint 2
Consider enforcing stricter rules around the freshness of oracle data to ensure calculations are based on recent information.


### Solution
```solidity
uint256 public constant MAX_DELAY = 1 hours; // Fix: Define maximum allowed delay

function updateValue() public {
    uint256 price = oracle.getPrice();
    uint256 lastUpdated = oracle.getLastUpdatedTime();

    require(price > 0, "Invalid price");
    require(lastUpdated > 0, "Invalid timestamp");
    require(block.timestamp - lastUpdated <= MAX_DELAY, "Price data too old"); // Fix: Enforce freshness

    totalValue = totalValue * price / 1e18;
}
```


