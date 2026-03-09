# FV-MOV-7-CL1: Oracle Validation

## TLDR

Oracle price acceptance without staleness and confidence checks is a critical finding. Any of four failures - stale price, wide confidence, fake oracle object, or single oracle source - can result in protocol insolvency via under-collateralized borrows or manipulated liquidations.

## Detection Heuristics

- Find all oracle price reads; for each one verify: (1) staleness check: `assert!(clock_ms - oracle.last_update_ms <= MAX_STALE_MS)`, (2) confidence interval check: `assert!(oracle.conf * 100 / oracle.price <= MAX_CONF_PCT)`
- Verify the oracle object ID is validated against a stored, admin-configured value: `assert!(object::id(oracle) == config.oracle_id)` - accepting any object of the oracle type allows fake oracle injection
- Count oracle sources used for any single price feed - a single source with no fallback is a medium finding; a single source for liquidation pricing is high
- For Pyth integration on Sui, verify the Pyth state object ID is the official Pyth deployment address
- Verify staleness and confidence thresholds are stored in a mutable admin config (not hardcoded) and emit events when changed

## False Positives

- Staleness check present with configurable `MAX_STALE_MS`
- Confidence interval check present with configurable threshold
- Oracle object ID validated against stored config
- Multi-oracle aggregation with deviation check
