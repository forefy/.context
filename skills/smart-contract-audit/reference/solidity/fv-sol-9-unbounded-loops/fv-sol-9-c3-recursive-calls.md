# FV-SOL-9-C3 Recursive Calls

## TLDR

Although Solidity does not support native recursion due to lack of stack depth, developers may attempt recursive-like behavior by using repetitive function calls that mimic loops

## Game

Can you spot why this contract might run out of gas and fail spectacularly?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract RecursiveCallsGame {
    mapping(address => uint256) public balances;

    // Deposit Ether
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Withdraw funds recursively
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;

        // Recursive payout
        if (amount > 0) {
            payable(msg.sender).transfer(1); // Transfer 1 wei at a time
            withdraw(amount - 1); // Recursive call
        }
    }
}

```


### Hint 1
Look at how the function calls itself. What happens if the `amount` is large? Will it ever stop, or will something else stop it?


### Hint 2
Consider how Solidity handles recursion and gas. Think about whether this design scales.


### Solution
```solidity
function withdraw(uint256 amount) public {
    require(balances[msg.sender] >= amount, "Insufficient balance");
    balances[msg.sender] -= amount;

    for (uint256 i = 0; i < amount; i++) {
        payable(msg.sender).transfer(1); // Fix: Iteratively transfer funds
    }
}
```


