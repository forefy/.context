# FV-SOL-8-C4 Unexpected Gas Increase

## TLDR

Occurs when dynamic transaction fees or gas fees increase unexpectedly, eating into the user's transaction value and causing unintended slippage.

## Game

During the transaction, the user expects a predictable gas cost. Would you say he can calm down and go eat a sandwich?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IDEX {
    function swap(address tokenIn, address tokenOut, uint256 amountIn) external returns (uint256);
}

contract GasIncreaseGame {
    IDEX public dex;
    address public tokenOut;

    constructor(address _dex, address _tokenOut) {
        dex = IDEX(_dex);
        tokenOut = _tokenOut;
    }
    
    function executeSwap(address tokenIn, uint256 amountIn) public {
        dex.swap(tokenIn, tokenOut, amountIn);
    }
}
```


### Hint 1
Consider how you might limit the transaction’s gas cost or mitigate the impact of gas-heavy external calls.


### Hint 2
Timeouts or gas limit checks might help you detect and prevent excessive gas consumption during the transaction.


### Solution
```solidity
function executeSwap(address tokenIn, uint256 amountIn) public {
    uint256 gasLimit = gasleft() / 2; // Fix: Use only a portion of the remaining gas for the external call

    (bool success, bytes memory returnData) = address(dex).call{gas: gasLimit}(
        abi.encodeWithSelector(dex.swap.selector, tokenIn, tokenOut, amountIn)
    );

    require(success, "Swap failed or exceeded gas limit");

    // Decode and validate the result
    uint256 amountOut = abi.decode(returnData, (uint256));
    require(amountOut > 0, "Invalid swap output");
}
```


