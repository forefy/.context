# FV-SOL-8-C2 Front-Running

## TLDR

Exploiting the price calculation mechanism to cause an unusually high slippage rate

## Game

This contract allows users to execute token swaps on a DEX. This transactions are visible in the mempool. Umm.. what else?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IDEX {
    function swap(address tokenIn, address tokenOut, uint256 amountIn) external returns (uint256);
    function getPrice(address tokenIn, address tokenOut) external view returns (uint256);
}

contract FrontRunningGame {
    IDEX public dex;
    address public tokenOut;

    constructor(address _dex, address _tokenOut) {
        dex = IDEX(_dex);
        tokenOut = _tokenOut;
    }

    // Function to perform a swap without protection against front-running
    function executeSwap(address tokenIn, uint256 amountIn, uint256 minAmountOut) public {
        uint256 amountOut = dex.swap(tokenIn, tokenOut, amountIn);
        require(amountOut >= minAmountOut, "Slippage too high");
    }
}
```


### Hint 1
Consider how you might prevent front-runners from knowing the exact price or transaction parameters until execution. Is there a way to obfuscate the trade details?


### Hint 2
Using a two-step commit-reveal scheme can help protect users by preventing attackers from viewing the trade parameters in the mempool.


### Solution
```solidity
contract FrontRunningGame {
    IDEX public dex;
    address public tokenOut;

    struct Trade {
        uint256 amountIn;
        uint256 minAmountOut;
    }

    mapping(address => bytes32) public tradeCommitments;

    constructor(address _dex, address _tokenOut) {
        dex = IDEX(_dex);
        tokenOut = _tokenOut;
    }

    // Fix step 1: User commits to a trade by submitting a hash
    function commitTrade(bytes32 tradeHash) public {
        tradeCommitments[msg.sender] = tradeHash;
    }

    // Fix step 2: User reveals trade details, which are checked against the committed hash
    function revealTrade(address tokenIn, uint256 amountIn, uint256 minAmountOut) public {
        // Fix step 3: Verify that the revealed parameters match the committed hash
        require(tradeCommitments[msg.sender] == keccak256(abi.encodePacked(tokenIn, amountIn, minAmountOut)), "Invalid commitment");

        uint256 amountOut = dex.swap(tokenIn, tokenOut, amountIn);
        require(amountOut >= minAmountOut, "Slippage too high");

        // Clear commitment after successful trade
        delete tradeCommitments[msg.sender];
    }
}
```


