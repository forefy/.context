# FV-MOV-7: DeFi Protocols

This category covers the domain-specific vulnerability patterns for lending, AMM/DEX, staking, bridge, and governance protocols on Sui. The protocol checklists from `sui-protocol-agent.md` are the primary reference for each type.

## Cases

- [fv-mov-7-cl1-oracle-validation.md](fv-mov-7-cl1-oracle-validation.md) - Oracle staleness, confidence interval, fake oracle, single-source risk
- [fv-mov-7-cl2-staking-rewards.md](fv-mov-7-cl2-staking-rewards.md) - Accumulator ordering, flash stake, precision loss, reward dilution
- [fv-mov-7-cl3-liquidation.md](fv-mov-7-cl3-liquidation.md) - Incentive gaps, self-liquidation, bad debt, interest during pause
- [fv-mov-7-cl4-bridge-governance.md](fv-mov-7-cl4-bridge-governance.md) - Message replay, flash vote, governance timelock, ZK nullifier

## Key Vectors

V91, V92, V93, V94, V95, V96, V97, V99, V100, V101, V102, V103, V104, V105, V106, V110, V111, V115, V117, V119, V133, V143
