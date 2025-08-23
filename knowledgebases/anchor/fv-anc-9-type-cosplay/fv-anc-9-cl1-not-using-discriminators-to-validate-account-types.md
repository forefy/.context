# FV-ANC-9-CL1 Not using discriminators to validate account types

## Bad


```rust
let account = User::try_from_slice(&ctx.accounts.account.data.borrow())?;
// No check to ensure `account` is actually a `User` type.
```

## Good


```rust
let discriminator = &ctx.accounts.account.data.borrow()[..8];
if discriminator != User::DISCRIMINATOR {
    return Err(ProgramError::InvalidAccountData);
}
let account = User::try_from_slice(&ctx.accounts.account.data.borrow())?;
```
