# FV-ANC-2-CL1 Unvalidated signers

## Bad


```rust
// No validation to check if `authority` signed the transaction
pub authority: AccountInfo<'info>,
```

## Good


```rust
// Ensures `authority` is a valid signer
pub authority: Signer<'info>,
```
