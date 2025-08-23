# FV-SOL-5 Logic Errors

## TLDR

Logic errors arise from mistakes in the program’s control flow or conditional statements.

These errors usually occur when the code’s behavior deviates from its intended purpose, not because of a flaw in the underlying arithmetic but due to a conceptual mistake in implementing rules or boundaries.

## Code


```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableMarket {
    uint256 constant BLOCK_EPOCH = 100000;
    mapping(uint256 => uint256) public cantoPerBlock; // Reward rates by epoch
    struct MarketInfo {
        uint256 lastRewardBlock;
        uint256 accCantoPerShare;
    }
    mapping(address => MarketInfo) public marketInfo;

    constructor() {
        cantoPerBlock[0] = 100;       // Reward for epoch 0-99999
        cantoPerBlock[BLOCK_EPOCH] = 0; // No reward for epoch 100000+
    }

    function update_market(address _market) public {
        MarketInfo storage market = marketInfo[_market];
        if (block.number > market.lastRewardBlock) {
            uint256 i = market.lastRewardBlock;
            while (i < block.number) {
                uint256 epoch = (i / BLOCK_EPOCH) * BLOCK_EPOCH;
                // Incorrect: should be `epoch + BLOCK_EPOCH`
                // Adding BLOCK_EPOCH to i only creates a fixed offset from i. It moves i forward by 100,000 blocks from whatever its current position is. However, this new position could land anywhere within an epoch and will not necessarily align with the start of the next epoch boundary
                uint256 nextEpoch = i + BLOCK_EPOCH; 
                uint256 blockDelta = min(nextEpoch, block.number) - i;

                // Incorrect reward calculation across epochs
                market.accCantoPerShare += blockDelta * cantoPerBlock[epoch];
                i += blockDelta;
            }
            market.lastRewardBlock = block.number;
        }
    }

    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}
```

## Classifications

#### [fv-sol-5-c1-boundary-misalignment.md](fv-sol-5-c1-boundary-misalignment.md "mention")

#### [fv-sol-5-c2-incorrect-conditionals.md](fv-sol-5-c2-incorrect-conditionals.md "mention")

#### [fv-sol-5-c3-improper-state-transitions.md](fv-sol-5-c3-improper-state-transitions.md "mention")

#### [fv-sol-5-c4-misordered-calculations.md](fv-sol-5-c4-misordered-calculations.md "mention")

#### [fv-sol-5-c5-event-misreporting.md](fv-sol-5-c5-event-misreporting.md "mention")

## Mitigation Patterns

### State Machine Design (FV-SOL-5-M1)

The State Machine Design mitigation pattern is a robust approach for managing complex workflows or processes with defined states

### Fail-Safe Defaults (FV-SOL-5-M2)

Use safe defaults in case of unexpected conditions or edge cases

### Unit Testing on Edge Cases (FV-SOL-5-M3)

Implement exhaustive tests for each function, focusing on boundary values, extreme inputs, and edge cases

## Actual Occurrences

* [https://solodit.cyfrin.io/issues/h-02-eth-gets-locked-in-the-groupcoinfactory-contract-pashov-audit-group-none-groupcoin-markdown](https://solodit.cyfrin.io/issues/h-02-update_market-nextepoch-calculation-incorrect-code4rena-canto-canto-git)
