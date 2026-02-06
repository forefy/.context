# FV-ANC-3-CL1 Trying to modify an account without checking if it's writeable

## Bad


```rust
// Attempt to modify account without checking if it is writable
let data = &mut ctx.accounts.config.data.borrow_mut();
data[0] = 42;
```

## Good


```rust
// Explicitly verify that the account is writable before modification
if !ctx.accounts.config.is_writable {
    return Err(ProgramError::InvalidAccountData);
}

let data = &mut ctx.accounts.config.data.borrow_mut();
data[0] = 42;
```
