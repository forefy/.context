# FV-SOL-1-C3 Cross Contract

## TLDR

In **cross-contract reentrancy**, an attacker uses two separate contracts: one vulnerable contract and another malicious contract.

The attacker’s contract calls the vulnerable contract repeatedly across functions to manipulate shared state and drain funds.

## Game

Think about how an attacker could exploit this setup if they deploy a separate malicious contract.

Can you identify how `withdraw` might allow another contract to repeatedly manipulate `balances` and drain funds?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract CrossContractReentrancyGame {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "Insufficient balance");
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;
    }
}
```


### Hint 1
Cross-contract reentrancy leverages a separate malicious contract that repeatedly calls into the vulnerable contract.

Look at the external call to `msg.sender` in `withdraw`, and consider what could happen if `msg.sender` is itself a contract with logic to call `withdraw` repeatedly.


### Hint 2
Notice that `balances[msg.sender]` is only updated after the Ether transfer.

Think about how a separate attacker contract could call back into `withdraw` multiple times within a single transaction to exploit this delay.


### Solution
```solidity
function withdraw() public {
    uint256 balance = balances[msg.sender];
    require(balance > 0, "Insufficient balance");
    
    // Fix: Set balance to zero before transferring
    balances[msg.sender] = 0; 
    
    (bool success, ) = msg.sender.call{value: balance}("");
    require(success, "Transfer failed");
}
```


