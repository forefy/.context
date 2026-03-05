# FV-ANC-5-CL5 SOL Balance Drain via CPI

## Bad


```rust
// Caller signs an account and hands it to an external program via CPI.
// No check on lamport balance before or after — the callee can spend
// lamports from the signing account without the caller's awareness.
invoke(
    &external_program_instruction,
    &[ctx.accounts.vault.to_account_info()],
)?;
```

## Good


```rust
let vault_before = ctx.accounts.vault.lamports();

invoke(
    &external_program_instruction,
    &[ctx.accounts.vault.to_account_info()],
)?;

let vault_after = ctx.accounts.vault.lamports();
require!(vault_after >= vault_before, ErrorCode::UnexpectedLamportDrain);
```
