# FV-ANC-5-CL6 Post-CPI Ownership Change

## Bad


```rust
// After a CPI to an attacker-controlled program, the account owner
// may have been changed via `assign`. The caller does not re-verify
// ownership before acting on the account.
invoke(&malicious_cpi_ix, &[ctx.accounts.target.to_account_info()])?;
process_account_data(&ctx.accounts.target)?;  // owner may now be attacker
```

## Good


```rust
invoke(&external_cpi_ix, &[ctx.accounts.target.to_account_info()])?;

// Re-verify the account's owner has not changed after the CPI.
require!(
    ctx.accounts.target.owner == &expected_program_id,
    ErrorCode::UnexpectedOwnerChange
);
process_account_data(&ctx.accounts.target)?;
```
