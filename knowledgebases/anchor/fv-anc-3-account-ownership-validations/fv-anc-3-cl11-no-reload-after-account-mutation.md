# FV-ANC-3-CL11 No reload after account mutation

## Bad


```rust
let mut account_data = ctx.accounts.user_account.load_mut()?;
account_data.value = new_value;
// Further operations assume `account_data` is up-to-date without reloading.
```

## Good


```rust
{
    let mut account_data = ctx.accounts.user_account.load_mut()?;
    account_data.value = new_value;
}
// Reload the account to ensure fresh data.
let account_data = ctx.accounts.user_account.load()?;
```
