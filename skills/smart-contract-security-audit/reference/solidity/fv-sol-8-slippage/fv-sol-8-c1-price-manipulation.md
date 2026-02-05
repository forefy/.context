# FV-SOL-8-C1 Price Manipulation

## TLDR

Exploiting the price calculation mechanism to cause an unusually high slippage rate

## Game

They did not thing about guarding against slippage here.

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IDEX {
    function swap(address tokenIn, address tokenOut, uint256 amountIn) external returns (uint256);
    function getPrice(address tokenIn, address tokenOut) external view returns (uint256);
}

contract PriceManipulationGame {
    IDEX public dex;
    address public tokenOut;

    constructor(address _dex, address _tokenOut) {
        dex = IDEX(_dex);
        tokenOut = _tokenOut;
    }

    // Function to execute a swap based on the DEX's current price without additional protection
    function executeSwap(address tokenIn, uint256 amountIn) public {
        uint256 currentPrice = dex.getPrice(tokenIn, tokenOut);
        uint256 amountOut = dex.swap(tokenIn, tokenOut, amountIn);
        
        // No more safeguards after this point
    }
}
```


### Hint 1
Using only a single price source like `getPrice` can expose the contract to manipulation. Think about how you might incorporate additional checks or sources of truth for price validation.


### Hint 2
Consider implementing time-weighted average prices (TWAP) or using a decentralized oracle service to secure prices against manipulation.


### Solution
```solidity
interface IOracle {
    function getLatestPrice(address tokenIn, address tokenOut) external view returns (uint256);
}

contract PriceManipulationGame {
    IDEX public dex;
    IOracle public priceOracle;
    address public tokenOut;

    constructor(address _dex, address _tokenOut, address _oracle) {
        dex = IDEX(_dex);
        tokenOut = _tokenOut;
        priceOracle = IOracle(_oracle);
    }

    function executeSwap(address tokenIn, uint256 amountIn, uint256 maxSlippagePercent) public {
        uint256 dexPrice = dex.getPrice(tokenIn, tokenOut);
        uint256 oraclePrice = priceOracle.getLatestPrice(tokenIn, tokenOut);
        
        // Fix: Check if DEX price deviates too much from the oracle price
        require(
            dexPrice >= oraclePrice * (100 - maxSlippagePercent) / 100 &&
            dexPrice <= oraclePrice * (100 + maxSlippagePercent) / 100,
            "Price manipulation detected"
        );
        
        uint256 amountOut = dex.swap(tokenIn, tokenOut, amountIn);
        require(amountOut > 0, "Swap failed");
    }
}
```


