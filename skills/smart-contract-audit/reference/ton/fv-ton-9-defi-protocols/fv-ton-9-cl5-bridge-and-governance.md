# FV-TON-9-CL5 Bridge and Governance

## TLDR

Bridge contracts without message-hash deduplication allow replay of bridge transfers, minting tokens multiple times for a single lock. Governance contracts without vote-weight snapshots and timelocks are vulnerable to flash vote and immediate-execution attacks.

## Detection Heuristics

**Bridge message replay**
- No dictionary of processed message IDs (nonce or `cell_hash` of the original message) - the same bridge transfer can be submitted multiple times and mints tokens on each submission
- `dict_get` / `udict_get` check for the message ID absent from the bridge claim handler
- No rate limit on bridge minting per period

**Bridge supply invariant violation**
- Minted supply on the TON side can exceed the locked supply on the source chain due to decimal conversion errors, replay, or a missing supply cap
- No `total_minted` counter compared against `total_locked` reported by the bridge authority

**Flash governance vote**
- Vote weight derived from current token balance at the time of voting - attacker buys tokens, votes, then sells immediately
- No historical snapshot or checkpoint of token balances for vote weight calculation
- Token transfers allowed while a vote is active, enabling vote-weight transfer between wallets

**Proposal execution without timelock**
- Governance proposals execute immediately after passing a vote threshold with no delay
- No `timelock_delay` between vote passage and execution - users cannot review and exit before changes take effect
- No cancel mechanism during the timelock period for identified malicious proposals

## False Positives

- Bridge uses a committee-signed attestation with multi-sig threshold rather than direct replay protection - verify the committee signing keys are sufficiently decentralized and the threshold is adequate
- Governance uses a snapshot oracle or off-chain vote tallying with on-chain execution gating - confirm the snapshot cannot be manipulated between the snapshot block and the execution
