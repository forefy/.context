# FV-ANC-3-CL5 No is\_initialized check when operating on an account

## Bad


```rust
// Risk of operating on an uninitialized account
let state = &ctx.accounts.state;
```

## Good


```rust
// Explicitly check the `is_initialized` flag before proceeding
if ctx.accounts.state.is_initialized {
    return Err(ProgramError::AccountAlreadyInitialized);
}
ctx.accounts.state.is_initialized = true;
```
