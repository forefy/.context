# FV-ANC-10-CL2 Operations on accounts marked as closed

## Bad


```rust
// No checks for closed accounts in other program functions.
let data = ctx.accounts.account.try_borrow_data()?;
```

## Good


```rust
let data = ctx.accounts.account.try_borrow_data()?;
let discriminator: [u8; 8] = data[..8].try_into()?;
if discriminator == *b"CLOSEDAC" {
    return Err(ProgramError::InvalidAccountData); // Prevent usage of closed account.
}
```
