# Vyper-Specific Audit Checks

## Security Categories

### Access Control & Upgradeability

- Unauthorized access to sensitive functions
- Insecure constructor/init logic
- Upgradeability pattern misuse (e.g. unprotected upgradeTo)

### Fund Management

- Reentrancy vulnerabilities
- Incorrect accounting or balance tracking
- Incorrect token transfers or approvals
- Unchecked external call returns

### Vyper-Specific Issues

- Integer overflow/underflow (pre-0.3.4 versions)
- Timestamp dependencies and block manipulation
- Weak randomness sources
- Front-running vulnerabilities in MEV-sensitive logic
- Division precision errors specific to Vyper's fixed-point arithmetic

### Contract Logic Integrity

- Incorrect state transitions
- Lack of input validation leading to invariant violation
- Division precision errors
- Denial of service through unbounded operations

## Knowledge Base References

For detailed vulnerability patterns, read the relevant README then drill into case files:
- `cat $SKILL_DIR/reference/vyper/fv-vyp-1-reentrancy/README.md` - Reentrancy attack patterns
- `cat $SKILL_DIR/reference/vyper/fv-vyp-2-integer-overflow/README.md` - Overflow/underflow issues
- `cat $SKILL_DIR/reference/vyper/fv-vyp-3-access-control/README.md` - Access control vulnerabilities
- `cat $SKILL_DIR/reference/vyper/fv-vyp-4-external-calls/README.md` - External call safety
- `cat $SKILL_DIR/reference/vyper/fv-vyp-5-timestamp-dependencies/README.md` - Timestamp manipulation
- `cat $SKILL_DIR/reference/vyper/fv-vyp-6-weak-randomness/README.md` - Random number generation
- `cat $SKILL_DIR/reference/vyper/fv-vyp-7-front-running/README.md` - MEV and front-running
- `cat $SKILL_DIR/reference/vyper/fv-vyp-8-division-precision/README.md` - Fixed-point math issues
- `cat $SKILL_DIR/reference/vyper/fv-vyp-9-denial-of-service/README.md` - DoS vulnerabilities
- `cat $SKILL_DIR/reference/vyper/fv-vyp-10-upgradeability/README.md` - Upgrade pattern security
