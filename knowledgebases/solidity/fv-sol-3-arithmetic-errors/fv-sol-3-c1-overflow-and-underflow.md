# FV-SOL-3-C1 Overflow and Underflow

## TLDR

**Overflow and underflow** are common arithmetic errors that occur when values exceed or drop below their storage limits.

In Solidity versions before 0.8.0, these errors could result in unexpected behavior without throwing an error.

However, starting with Solidity 0.8.0, these operations automatically revert on overflow or underflow. Nevertheless, it’s important to understand these errors, especially when working with older contracts or specific arithmetic cases where unchecked math is used for optimization.

## Game

What if a user added an amount to `addToBalance` that exceeds the `uint256` limit?

## Sections
### Code
```solidity
pragma solidity ^0.7.0;

contract OverflowUnderflowGame {
    uint256 public totalSupply = 1000;
    mapping(address => uint256) public balances;

    function addToBalance(uint256 amount) public {
        balances[msg.sender] += amount;
    }

    function subtractFromBalance(uint256 amount) public {
        balances[msg.sender] -= amount;
    }
}
```


### Hint 1
Solidity versions before 0.8.0, adding a large number to `balances[msg.sender]` might cause it to wrap around to zero or another small number, creating an overflow.


### Hint 2
The `SafeMath` library from OpenZeppelin can be used to prevent overflow and underflow in Solidity <0.8.0


### Solution
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

import "@openzeppelin/contracts/math/SafeMath.sol";

contract OverflowUnderflowGame {
    using SafeMath for uint256;

    uint256 public totalSupply = 1000;
    mapping(address => uint256) public balances;

    function addToBalance(uint256 amount) public {
        balances[msg.sender] = balances[msg.sender].add(amount); // Fix: SafeMath prevents overflow
    }

    function subtractFromBalance(uint256 amount) public {
        balances[msg.sender] = balances[msg.sender].sub(amount); // Fix: SafeMath prevents underflow
    }
}

```


