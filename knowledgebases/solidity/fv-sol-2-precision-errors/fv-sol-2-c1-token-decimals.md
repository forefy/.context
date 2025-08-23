# FV-SOL-2-C1 Token Decimals

## TLDR

Precision errors often occur when dealing with tokens that have decimal points, especially when tokens with varying decimal standards (e.g., 6, 8, or 18 decimals) interact within the same system.

A mismatch in decimal handling can lead to incorrect calculations, resulting in inaccurate token transfers or balances.

## Game

The `transferAmount` function assumes the token has 18 decimals, can you identify how this assumption could lead to a significant error in token transfers?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function decimals() external view returns (uint8);
}

contract TokenDecimalsGame {
    IERC20 public token;

    constructor(address _token) {
        token = IERC20(_token);
    }

    function transferAmount(address recipient, uint256 amount) public {
        uint256 tokenAmount = amount * 10**18;
        require(token.transfer(recipient, tokenAmount), "Transfer failed");
    }
}
```


### Hint 1
ERC-20 tokens can have varying decimal places, often indicated by `decimals()`. If the contract assumes a specific decimal (e.g., 18), what might happen if the token has only 6 or 8 decimals?

Consider how `amount * 10**18` would differ depending on the actual decimals of the token


### Hint 2
Precision errors often arise when calculations assume a specific unit. In `transferAmount`, think about how the calculation could go wrong if the token's decimal setting differs from the assumed 18.

How could you dynamically adjust the transfer amount to match the token's decimals?


### Solution
```solidity
function transferAmount(address recipient, uint256 amount) public {
    uint8 decimals = token.decimals(); // Fix: Get the token's actual decimals
    uint256 tokenAmount = amount * 10**decimals;
    require(token.transfer(recipient, tokenAmount), "Transfer failed");
}
```


