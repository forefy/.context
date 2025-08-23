# FV-SOL-1-C5 Dynamic

## TLDR

In **dynamic reentrancy**, the reentrant attack doesn’t target a specific function directly but instead exploits more complex, user-controlled logic in the contract.

This type of reentrancy often arises when a contract allows external calls that influence its state unpredictably, based on dynamic or user-supplied data.

## Game

What could happen if `msg.sender` sets `target` as a contract they control, with a fallback function that calls `dynamicPayout` again?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract DynamicReentrancyGame {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function dynamicPayout(address target, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool success, ) = target.call{value: amount}("");
        require(success, "Transfer failed");
    }
}
```


### Hint 1
Dynamic reentrancy often exploits user-controlled parameters that determine the target of an external call. Here, `dynamicPayout` allows the user to specify `target`.

Consider what happens if `target` is a contract that re-calls `dynamicPayout`.


### Hint 2
Think about whether `balances[msg.sender]` is updated _before_ the external call. If `dynamicPayout` is reentered, would the balance deduction prevent repeated calls, or is there a way to exploit this order?


### Solution
```solidity
function dynamicPayout(address target, uint256 amount) public {
    require(balances[msg.sender] >= amount, "Insufficient balance");

    // Fix: Set balance to zero before any external call to prevent reentrancy
    balances[msg.sender] -= amount;

    (bool success, ) = target.call{value: amount}("");
    require(success, "Transfer failed");
}
```


