# FV-ANC-5-CL3 Not unsetting signer status before a CPI

## Bad


```rust
let cpi_accounts = vec![ctx.accounts.user.to_account_info()];
// User's `is_signer` status is propagated to the callee program without restriction.
invoke_signed(
    &instruction,
    &cpi_accounts,
    &[&seeds],
)?;
```

## Good


```rust
let mut cpi_accounts = vec![ctx.accounts.user.to_account_info()];
// Explicitly unset the `is_signer` status, to protect against malicious signer authority misuse by the external program
cpi_accounts[0].is_signer = false;

invoke_signed(
    &instruction,
    &cpi_accounts,
    &[&seeds],
)?;
```
