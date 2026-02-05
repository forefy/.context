# FV-ANC-3-CL10 Using ctx.remaining\_accounts without non-zero data check

## Bad


```rust
let extra_account = &ctx.remaining_accounts[0];
// No check for account liveness.
```

## Good


```rust
let extra_account = &ctx.remaining_accounts[0];
let data = extra_account.try_borrow_data()?;
if data.iter().all(|&byte| byte == 0) {
    return Err(ProgramError::UninitializedAccount);
}
```
