# FV-ANC-8-CL1 Unvalidated sysvar address

## Bad


```rust
// Using sysvar without validating its address
let rent = ctx.accounts.rent;
```

## Good


```rust
// Validate the sysvar address explicitly
if ctx.accounts.rent.key() != sysvar::rent::ID {
    return Err(ProgramError::InvalidArgument);
}
```
