# FV-MOV-7-CL3: Liquidation Safety

## TLDR

Four liquidation failure modes: (1) liquidation bonus does not cover gas cost for dust positions, creating unliquidatable bad debt; (2) self-liquidation is profitable, allowing users to extract the bonus; (3) bad debt not socialized, leaving a permanent accounting hole; (4) interest continues accruing during protocol pause, causing unexpected liquidations on unpause.

## Detection Heuristics

- Calculate the minimum liquidation bonus for the smallest viable position - if the bonus is less than a typical Sui transaction fee, the position cannot be profitably liquidated by any external actor
- Check whether self-liquidation is blocked (`assert!(liquidator != borrower)`) and whether the math makes self-liquidation unprofitable (bonus < penalty)
- Look for the bad debt handling mechanism: when collateral value falls below debt value, where does the residual go? No mechanism means it accumulates as a protocol deficit
- Check whether interest accrual is paused alongside `config.paused` - search for `accrue_interest` calls and verify they check the pause flag
- For partial liquidations, verify the remaining position size after liquidation is above the minimum position threshold - leaving a dust position creates a permanent unliquidatable residue

## False Positives

- Minimum position size enforced on all operations ensures positions are always liquidatable
- Self-liquidation explicitly prohibited or made unprofitable by design
- Insurance fund absorbs bad debt with socialization mechanism for overflow
- Interest accrual paused in the same function as protocol operations
