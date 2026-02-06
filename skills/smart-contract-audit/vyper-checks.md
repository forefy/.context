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

For detailed vulnerability patterns, see:
- `reference/vyper/fv-vyp-1-reentrancy/` - Reentrancy attack patterns
- `reference/vyper/fv-vyp-2-integer-overflow/` - Overflow/underflow issues
- `reference/vyper/fv-vyp-3-access-control/` - Access control vulnerabilities
- `reference/vyper/fv-vyp-4-external-calls/` - External call safety
- `reference/vyper/fv-vyp-5-timestamp-dependencies/` - Timestamp manipulation
- `reference/vyper/fv-vyp-6-weak-randomness/` - Random number generation
- `reference/vyper/fv-vyp-7-front-running/` - MEV and front-running
- `reference/vyper/fv-vyp-8-division-precision/` - Fixed-point math issues
- `reference/vyper/fv-vyp-9-denial-of-service/` - DoS vulnerabilities
- `reference/vyper/fv-vyp-10-upgradeability/` - Upgrade pattern security
