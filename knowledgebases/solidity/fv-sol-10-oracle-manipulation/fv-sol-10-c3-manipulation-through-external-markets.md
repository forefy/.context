# FV-SOL-10-C3 Manipulation Through External Markets

## TLDR

Manipulating prices in less liquid markets to impact the oracle's reported price, as some oracles aggregate prices from external exchanges

## Game

You’ve stumbled upon a contract using an on-chain oracle that directly fetches prices from a decentralized exchange (DEX).

But what if someone manipulates the DEX price for a brief window? Can the system withstand sudden external price shifts?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IPriceOracle {
    function getPrice(address token) external view returns (uint256);
}

contract MarketManipulationGame {
    IPriceOracle public oracle;
    address public token;
    uint256 public collateral;

    constructor(address _oracle, address _token, uint256 _initialCollateral) {
        oracle = IPriceOracle(_oracle);
        token = _token;
        collateral = _initialCollateral;
    }

    // Function to adjust collateral value based on oracle price
    function adjustCollateral() public {
        uint256 price = oracle.getPrice(token);
        require(price > 0, "Invalid price");
        collateral = collateral * price / 1e18; // Adjust collateral based on price
    }
}
```


### Hint 1
If the price from the DEX oracle can be temporarily manipulated, what impact could this have on `collateral`?


### Hint 2
Consider mechanisms to validate the price data or to smooth out sudden price changes over time.


### Solution
```solidity
uint256 public lastValidPrice;

function adjustCollateral() public {
    uint256 price = oracle.getPrice(token);
    require(price > 0, "Invalid price");

    // Fix: Cross-check with last valid price to ensure no sudden manipulation
    require(
        price <= lastValidPrice * 105 / 100 && price >= lastValidPrice * 95 / 100,
        "Price deviation too large"
    );

    collateral = collateral * price / 1e18;
    lastValidPrice = price; // Fix: Update last valid price
}
```


