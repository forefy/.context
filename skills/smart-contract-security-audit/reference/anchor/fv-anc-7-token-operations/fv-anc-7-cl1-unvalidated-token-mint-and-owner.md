# FV-ANC-7-CL1 Unvalidated token mint & owner

## Bad


```rust
// Proceeding without verifying token mint or owner
let token = ctx.accounts.token_account;
```

## Good


```rust
// Validate both the mint and owner of the token account
if ctx.accounts.token_account.mint != expected_mint || ctx.accounts.token_account.owner != expected_owner {
    return Err(ProgramError::InvalidAccountData);
}
```
