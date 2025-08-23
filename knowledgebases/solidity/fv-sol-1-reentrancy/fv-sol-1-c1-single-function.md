# FV-SOL-1-C1 Single Function

## TLDR

Attacker calls a vulnerable function repeatedly within itself, exploiting incomplete state updates to drain funds

## Game

Try to find what's wrong with the `withdraw` function, how would you turn this code secure?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract ReentrancyGame {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        require(balances[msg.sender] > 0, "Insufficient balance");

        (bool success, ) = msg.sender.call{value: balances[msg.sender]}("");
        require(success, "Transfer failed");

        balances[msg.sender] = 0;
    }
}
```


### Hint 1
When reviewing smart contract code, always check if any **state changes** (e.g., updating balances or other internal values) happen _after_ an external call, especially when using `.call`

Notice the order of operations in `withdraw` - does the balance update happen before or after the funds are sent?


### Hint 2
When `msg.sender` is a smart contract, it can have a `receive` or `fallback` function that gets triggered automatically when it receives Ether.

If this function calls `withdraw` again (before the balance is updated), it can re-enter the vulnerable function.


### Solution
```solidity
function withdraw() public {
    uint256 amount = balances[msg.sender];
    require(amount > 0, "Insufficient balance");

    // Fix: set balance to zero before transferring
    balances[msg.sender] = 0;

    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```


