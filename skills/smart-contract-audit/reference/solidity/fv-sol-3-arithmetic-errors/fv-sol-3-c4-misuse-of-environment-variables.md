# FV-SOL-3-C4 Misuse of Environment Variables

## TLDR

Environmental variables like `block.timestamp` are sometimes used in arithmetic, which can lead to unintended outcomes if assumptions about their values change

## Game

In this contract, `startGame` uses `block.timestamp` to enforce a 1-day delay between game starts.\
What do you think?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract TimestampGame {
    uint256 public lastPlayed;

    // Function to start a time-based game
    function startGame() public {
        require(block.timestamp >= lastPlayed + 1 days, "Game can only be started once a day");
        lastPlayed = block.timestamp;
    }
}
```


### Hint 1
How does the fairness of the game look like?


### Hint 2
Miners can adjust `block.timestamp` within a small range.

Consider what could happen if a miner slightly shifts the timestamp forward or backward in their favor, enabling them to bypass the intended delay.


### Solution
```solidity
uint256 public lastPlayedBlock;
function startGame() public {
    // Fix: Block numbers progress consistently, with each block representing approximately 13 seconds on Ethereum. By requiring a specific number of blocks to pass (6500 for roughly 24 hours), the contract can achieve a day-long delay without relying on block.timestamp
    require(block.number >= lastPlayedBlock + 6500, "Game can only be started once every ~1 day");
    lastPlayedBlock = block.number;
}
```


