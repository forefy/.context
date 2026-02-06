# FV-SOL-1-C2 Cross Function

## TLDR

Attacker uses multiple functions within the same contract that share state

## Game

Cross-function reentrancy occurs when an attacker can exploit reentrant calls across multiple functions, rather than a single function, how can you see this affecting the nature of the vulnerability?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract CrossFunctionReentrancyGame {
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

    function play() public {
        require(balances[msg.sender] >= 1 ether, "Must have at least 1 ether to play");
        balances[msg.sender] -= 1 ether;
    }
}
```


### Hint 1
Cross-function reentrancy occurs when multiple functions use the same state variable inconsistently.\
\
Look at how `withdraw` and `play` interact with `balances` and consider what might happen if an attacker calls `play` within a reentrant `withdraw` call.


### Hint 2
Think about what happens if `msg.sender` is a contract that calls `withdraw` first and then repeatedly reenters `play`.\
\
Would `balances[msg.sender]` behave as expected, or could it be manipulated across the two functions?


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


