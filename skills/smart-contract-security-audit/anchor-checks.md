# Anchor (Solana) Specific Audit Checks

## Solana/Anchor Program Tricks

- Check if PDA derivations use all required seeds and verify bump seeds are canonical
- Look for CPI calls that don't validate the target program ID matches expected program
- Verify if account validation checks both owner and discriminator for all account types
- Search for instructions that don't verify signer authority for accounts being modified
- Check if account reallocation properly handles rent exemption calculations
- Look for missing close constraints that leave accounts with non-zero data accessible
- Verify if program-derived addresses validate all derivation parameters

## Security Categories

### Account Constraints & Validation

- Missing or incorrect `#[account]` constraints
- Lack of `has_one`, `init`, `close`, or signer checks
- Mutable accounts without proper authority enforcement
- Trying to modify an account without checking if it's writeable
- Trying to access account data without ownership checks
- Usage of UncheckedAccount without manual ownership check
- Usage of UncheckedAccount without manual signer check
- No is_initialized check when operating on an account
- Missing account constraints
- Using ctx.remaining_accounts without non-zero data check
- No reload after account mutation
- Not validating a set address

### PDA & Seed Safety

- Seed collisions or reused seeds across programs
- Missing `bump` seeds or derivations that can be hijacked
- Missing PDA initialization check
- Forced seed de-bump
- Exposed PDA seeds
- Lack of proper PDA validation for signers

### CPI & Instruction Safety

- Unchecked CPI calls to untrusted programs
- Incorrect handling of cross-program invocations
- Dangerous use of `invoke_signed` without control validation
- Signing arbitrary programs without privilege checks
- Insecure CPIs using unchecked accounts
- Passing owner-checked accounts in CPI
- Reusing instruction parameters leading to exploits
- Missing signer checks in CPIs
- Account confusion with system program

### Deserialization & Instruction Data

- Use of unchecked `AccountInfo` directly
- Manual deserialization from instruction data without checks
- Logic depending on instruction index or ordering

### Error Handling

- Missing error checks after operations
- Improper error propagation
- Lack of meaningful error messages

### Token Operations

- Improper token mint/burn operations
- Missing token account validation
- Incorrect authority checks for token operations

### System Account Validation

- Missing system account checks
- Improper account initialization
- Rent exemption violations

### Type Cosplay

- Account type confusion
- Missing discriminator checks
- Improper account casting

### Closing Accounts

- Closing accounts without zeroing data and setting a closed discriminator
- Operations on accounts marked as closed
- Unintended closure by close constraint

## Knowledge Base References

For detailed vulnerability patterns, see:
- `reference/anchor/fv-anc-1-arithmetic-operations/` - Math overflow/underflow
- `reference/anchor/fv-anc-2-signer-checks/` - Signer validation issues
- `reference/anchor/fv-anc-3-account-ownership-validations/` - Account validation
- `reference/anchor/fv-anc-4-pda-security/` - PDA vulnerabilities
- `reference/anchor/fv-anc-5-cross-program-invocation-cpi/` - CPI security
- `reference/anchor/fv-anc-6-error-handling/` - Error handling patterns
- `reference/anchor/fv-anc-7-token-operations/` - Token security
- `reference/anchor/fv-anc-8-system-account-validation/` - System account checks
- `reference/anchor/fv-anc-9-type-cosplay/` - Type confusion
- `reference/anchor/fv-anc-10-closing-accounts/` - Account closure security
