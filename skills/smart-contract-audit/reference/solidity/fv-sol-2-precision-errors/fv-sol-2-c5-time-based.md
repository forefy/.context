# FV-SOL-2-C5 Time-Based

## TLDR

**Time-based vulnerabilities** occur when contracts rely on the blockchain timestamp (`block.timestamp`) for critical logic.

Since timestamps can be manipulated slightly by miners, using them for sensitive functions (like fund release schedules or random number generation) can introduce potential exploits or inconsistencies.

## Game

What happens here if miners manipulate the timestamp or there's a long delay?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract TimeBasedGame {
    uint256 public unlockTime;
    mapping(address => uint256) public balances;

    function deposit(uint256 lockDuration) public payable {
        require(msg.value > 0, "Deposit must be greater than zero");

        // Set unlock time based on lockDuration
        unlockTime = block.timestamp + lockDuration;
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        require(block.timestamp >= unlockTime, "Funds are locked");
        uint256 amount = balances[msg.sender];
        balances[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Withdraw failed");
    }
}

```


### Hint 1
Miners have some control over `block.timestamp` and can adjust it slightly. Consider what happens if a miner sets `block.timestamp` slightly ahead or behind the expected time, affecting `unlockTime`


### Hint 2
When setting time-based constraints, consider adding a buffer or alternative logic to handle small timestamp manipulations.


### Solution
```solidity
function deposit(uint256 lockDuration) public payable {
    require(msg.value > 0, "Deposit must be greater than zero");
    
    // Fix: Set unlock time with an additional buffer
    unlockTime = block.timestamp + lockDuration + 15; // Adding a buffer
    balances[msg.sender] += msg.value;
}
```


