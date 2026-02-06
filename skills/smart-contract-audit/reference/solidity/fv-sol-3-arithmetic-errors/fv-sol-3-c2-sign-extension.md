# FV-SOL-3-C2 Sign Extension

## TLDR

Sign extension issues can occur when smaller integer types are converted to larger signed integers, potentially causing unintended sign changes in the process

An `int8` value of `-1` might be interpreted incorrectly if expanded to an `int256`, as sign extension might lead to an unexpected value

## Game

A signed integer is mishandled, can you spot the issue?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract SignExtensionGame {
    int8 public score;

    function setScore(int8 newScore) public {
        score = newScore;
    }

    // This function rewards or penalizes the user based on score
    function applyBonus() public view returns (int256) {
        int256 reward = int256(score) * 1000;
        return reward;
    }
}
```


### Hint 1
Sign extension errors happen when a smaller signed integer is cast to a larger signed integer without handling the sign properly


### Hint 2
When extending `int8` to `int256`, the sign bit can extend to fill the additional bits, leading to unintended results.


### Solution
```solidity
function applyBonus() public view returns (int256) {
    int256 reward = int256(int8(score & 0xFF)) * 1000; // Fix: Masking to prevent sign extension
    return reward;
}
```


