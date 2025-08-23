# FV-ANC-3-CL2 Trying to access account data without ownership checks

## Bad


```rust
// Accessing account data without validating its ownership
let config_data = &ctx.accounts.config.data.borrow();
```

## Good


```rust
// Validate that the account is owned by the current program
if ctx.accounts.config.owner != ctx.program_id {
    return Err(ProgramError::IllegalOwner);
}

let config_data = &ctx.accounts.config.data.borrow();
```
