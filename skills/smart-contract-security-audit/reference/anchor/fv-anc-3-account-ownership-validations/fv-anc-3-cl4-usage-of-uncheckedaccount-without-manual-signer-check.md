# FV-ANC-3-CL4 Usage of UncheckedAccount without manual signer check

## Bad


```rust
#[account]
pub signer_account: UncheckedAccount<'info>; // Missing `is_signer` check.
```

## Good


```rust
#[account]
pub signer_account: UncheckedAccount<'info>;

// Check if signer
if !signer_account.is_signer {
    return Err(ProgramError::MissingRequiredSignature);
}
```
