# FV-MOV-7-CL4: Bridge and Governance Security

## TLDR

Bridge message replay (missing nonce), governance flash vote (using current instead of snapshot balance), and ZK proof replay (missing nullifier) are the primary critical/high findings in this category. Each allows an attacker to repeat or manipulate a privileged action.

## Detection Heuristics

- For bridges: verify every processed message hash is stored and checked: `assert!(!table::contains(&processed, message_hash))` before processing, then `table::add` after
- Verify source chain and sender are validated on every inbound bridge message - accepting messages from any sender is a critical finding
- For governance: verify vote weight is read from a historical snapshot (past epoch balance), not current token balance - current-balance voting enables flash vote attacks via PTB
- Verify a timelock between proposal passage and execution - immediate execution of passed proposals is a critical finding
- For ZK proofs: verify a nullifier is computed from the proof and stored: `assert!(!table::contains(&nullifiers, proof.nullifier))` before accepting, then stored after acceptance

## False Positives

- Bridge message hash stored and checked on every execution
- Governance vote weight from past epoch snapshot via checkpointed balance
- Timelock between passage and execution with documented delay
- ZK nullifier table maintained and checked on every proof verification
