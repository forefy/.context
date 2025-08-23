# FV-SOL-8-C3 Insufficient Liquidity

## TLDR

If a DEX doesn’t have enough liquidity in the token pair, the price impact will be disproportionately high, leading to significant slippage or failed transactions.

## Game

If the DEX’s liquidity is low, the swap might incur heavy slippage, or worse, revert due to insufficient output tokens. What to do??

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IDEX {
    function swap(address tokenIn, address tokenOut, uint256 amountIn) external returns (uint256);
    function getAvailableLiquidity(address tokenOut) external view returns (uint256);
}

contract InsufficientLiquidityGame {
    IDEX public dex;
    address public tokenOut;

    constructor(address _dex, address _tokenOut) {
        dex = IDEX(_dex);
        tokenOut = _tokenOut;
    }

    function executeSwap(address tokenIn, uint256 amountIn) public {
        uint256 amountOut = dex.swap(tokenIn, tokenOut, amountIn);
        require(amountOut > 0, "Swap failed");
    }
}

```


### Hint 1
Before performing a swap, consider how you might verify that the DEX has enough liquidity for the requested token.


### Hint 2
Checking the DEX’s available liquidity for `tokenOut` can help you ensure that the swap is feasible and reduce the risk of slippage or failure.


### Solution
```solidity
function executeSwap(address tokenIn, uint256 amountIn, uint256 minLiquidity) public {
    uint256 availableLiquidity = dex.getAvailableLiquidity(tokenOut);
    require(availableLiquidity >= minLiquidity, "Insufficient liquidity"); // Fix: Check liquidity before swapping

    uint256 amountOut = dex.swap(tokenIn, tokenOut, amountIn);
    require(amountOut > 0, "Swap failed");
}
```


