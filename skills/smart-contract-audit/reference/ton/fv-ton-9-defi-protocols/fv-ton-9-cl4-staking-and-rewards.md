# FV-TON-9-CL4 Staking and Rewards

## TLDR

Flash stake/unstake reward capture, precision loss in accumulators, and reward rate manipulation via direct token transfers are the primary vulnerabilities in TON staking contracts.

## Detection Heuristics

**Flash stake reward capture**
- No minimum staking duration or warmup period - user stakes just before a reward distribution snapshot, claims full rewards, and unstakes immediately
- Reward weight based on point-in-time balance rather than time-weighted balance

**Precision loss in reward accumulator**
- `reward_per_token += reward_amount / total_staked` with no scaling multiplier - when `reward_amount < total_staked`, the increment rounds to zero and small stakers accumulate nothing
- Absence of a scaling factor (e.g., multiply numerator by `1_000_000_000` before dividing)
- Reward accumulator updated after a balance change rather than before - the balance update affects the reward calculation for the current period

**Direct transfer manipulation**
- Reward rate calculated from the reward token's balance in the contract - direct token transfer inflates the balance and dilutes the reward rate for existing stakers
- No internal `reward_balance` tracker separate from the raw contract token balance

**Cooldown griefing**
- Cooldown period for unstaking can be reset by dust deposits from an attacker, locking the user's stake indefinitely
- No per-user cooldown enforcement - a single contract-level cooldown allows all users to be affected

## False Positives

- Time-weighted average balance used for reward calculation - verify the TWAB implementation snapshots before the reward period closes
- Reward rate is a fixed emission per block/time rather than derived from balance, making direct transfers irrelevant to the rate
