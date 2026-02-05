# FV-ANC-3-CL9 Using ctx.remaining\_accounts without manual discriminator check

## Bad


```rust
let extra_account = &ctx.remaining_accounts[0];
// No check for account type discriminator.
```

## Good


```rust
let extra_account = &ctx.remaining_accounts[0];
let data = extra_account.try_borrow_data()?;
if &data[..8] != MyAccountType::DISCRIMINATOR {
    return Err(ProgramError::InvalidAccountData);
}
```
