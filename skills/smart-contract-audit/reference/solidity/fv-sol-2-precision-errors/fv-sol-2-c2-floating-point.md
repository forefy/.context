# FV-SOL-2-C2 Floating Point

## TLDR

Floating-point numbers can’t represent every decimal exactly. For example, `0.3` might be stored as `0.30000000000000004` in a system that uses floating-point arithmetic.

When you divide and multiply these imprecise values, the error compounds. For example, `(0.3 / 1000.0) * 1.0` could produce something like `0.00030000000000000004` instead of the expected `0.0003`.

This often occurs when dealing with fractional values or very large numbers, where small rounding errors can accumulate and lead to inaccurate calculations or financial discrepancies.

## Game

What is the result of `userReward`? can you tell?

## Sections
### Code
```solidity


totalHoldings = 1000.0; // Total holdings
userHoldings = 0.3;     // User's fractional holdings
totalReward = 1.0;      // Total reward to be distributed

// Calculate user's reward
userReward = (userHoldings / totalHoldings) * totalReward; 
```


### Hint 1
Floating-point calculations can produce small rounding errors. These errors accumulate over multiple calculations, making them especially problematic in systems with many users or repeated transactions. Consider how `userReward` might differ slightly each time due to these rounding issues


### Hint 2
Financial applications need exact values.

Think about how a **scaling factor** could help you avoid floating-point precision issues, ensuring exact calculations by keeping everything in integer form.


### Solution
```solidity
uint256 totalHoldings = 1000 * 10**18; // Fix: Representing 1000.0 with 18 decimal places
uint256 userHoldings = 3 * 10**17;     // Fix 2: Representing 0.3 with 18 decimal places
uint256 totalReward = 1 * 10**18;      // Fix 3: Representing 1.0 as 10^18 (scaled)

uint256 userReward = (userHoldings * totalReward) / totalHoldings; // Result: 3 * 10^14
// This represents 0.0003 Ether without precision errors.
```


