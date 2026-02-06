# FV-SOL-5-C5 Event Misreporting

## TLDR

Failing to emit an event during a critical update like reward distribution, making it hard to track transactions or actions on-chain

## Game

The wrong balance might be logged.

Can you identify how this misreporting could happen?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract EventMisreportingGame {
    uint256 public totalDeposits;
    mapping(address => uint256) public balances;

    event DepositMade(address indexed user, uint256 amount, uint256 totalDeposits);

    // Function to allow users to deposit and log the event
    function deposit() public payable {
        balances[msg.sender] += msg.value;
        totalDeposits += msg.value;
        
        emit DepositMade(msg.sender, balances[msg.sender], totalDeposits);
    }
}
```


### Hint 1
Look carefully at the values emitted in the `DepositMade` event.

Consider whether the event is showing the current deposit amount or the user’s total balance.


### Hint 2
Think about how you could adjust the parameters of `emit DepositMade` to reflect the accurate data intended for each transaction.


### Solution
```solidity
function deposit() public payable {
    balances[msg.sender] += msg.value;
    totalDeposits += msg.value;
    
    // Fix: Emit the actual deposit amount (msg.value) rather than the total balance
    emit DepositMade(msg.sender, msg.value, totalDeposits);
}
```


