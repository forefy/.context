# FV-SOL-6-C2 Unchecked Transfer Return

## TLDR

Failing to check the return value of calls to `transferFrom` or `transfer` functions on ERC20 tokens can lead to unexpected behavior.

For certain tokens, these functions may return `false` instead of reverting when there are insufficient tokens or if the transfer is unsuccessful. If the return value is ignored, the transaction might continue even if the transfer failed.

## Game

What in this token transfer contract can be risky?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

interface IToken {
    function transfer(address recipient, uint256 amount) external returns (bool);
}

contract UncheckedExternalCallGame {
    IToken public token;

    constructor(address _token) {
        token = IToken(_token);
    }

    function transferTokens(address recipient, uint256 amount) public {
        token.transfer(recipient, amount); 
}
```


### Hint 1
External calls can fail for various reasons, such as insufficient funds or other contract restrictions. Consider how you might verify that the `transfer` function succeeded.


### Hint 2
Think about using the return value of the `transfer` function to check if the external call was successful and handle the situation accordingly if it wasn’t.


### Solution
```solidity
function transferTokens(address recipient, uint256 amount) public {
    bool success = token.transfer(recipient, amount);
    require(success, "Token transfer failed"); // Fix: Check the return value
}
```


