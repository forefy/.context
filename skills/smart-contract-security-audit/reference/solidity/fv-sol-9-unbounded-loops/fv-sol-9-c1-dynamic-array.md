# FV-SOL-9-C1 Dynamic Array

## TLDR

This issue arises when a loop iterates over a dynamic array (an array whose size can grow over time) without bounds or a reasonable upper limit

## Game

Hoping that the array size can't grow too large..?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract DynamicArrayGame {
    uint256[] public numbers;

    function addNumber(uint256 number) public {
        numbers.push(number);
    }

    function sumNumbers() public view returns (uint256) {
        uint256 sum = 0;
        for (uint256 i = 0; i < numbers.length; i++) {
            sum += numbers[i];
        }
        return sum;
    }
}
```


### Hint 1
Consider how the size of `numbers` affects the gas cost of `sumNumbers`. Is there a way to limit the size of the array or break the operation into smaller steps?


### Hint 2
Precomputing or caching results can help avoid iterating through large arrays during transactions.


### Solution
```solidity
contract DynamicArrayGame {
    uint256[] public numbers;
    uint256 public cachedSum;

    function addNumber(uint256 number) public {
        numbers.push(number);
        cachedSum += number; // Fix: Update cached sum during each addition
    }

    function sumNumbers() public view returns (uint256) {
        return cachedSum; // Fix: Use cached sum instead of looping
    }
}
```


