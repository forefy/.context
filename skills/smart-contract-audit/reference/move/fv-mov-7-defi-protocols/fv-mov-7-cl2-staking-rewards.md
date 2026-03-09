# FV-MOV-7-CL2: Staking Reward Accumulator Ordering

## TLDR

A reward accumulator (`reward_per_token`) must be updated before any balance change. Updating it after a stake/unstake causes the new balance to earn historical rewards (retroactive accrual) or the withdrawing user to lose owed rewards. This is a Critical finding pattern confirmed in two Thala Labs audits.

## Detection Heuristics

- In every stake and unstake function, verify `update_rewards(account)` or accumulator update is the first statement, before any balance modification
- Safe pattern: (1) update global accumulator `reward_per_token`, (2) settle pending rewards for account, (3) modify balance, (4) checkpoint new accumulator value on account
- Staking contracts should prevent flash stake/unstake reward capture via a minimum lock period or time-weighted reward accumulation
- Check whether direct coin transfers to the reward pool change the reward rate - the reward rate must be based on an internal `total_staked` counter, not on actual token balance in the contract
- For multi-token reward systems, verify each reward token has an independent accumulator

## False Positives

- Accumulator updated as the first operation in every balance-modifying function
- Minimum staking duration prevents flash stake/unstake in same epoch
- Time-weighted rewards mean short-duration stakes earn negligible rewards
- Reward rate based on `total_staked` state variable, not raw contract balance
