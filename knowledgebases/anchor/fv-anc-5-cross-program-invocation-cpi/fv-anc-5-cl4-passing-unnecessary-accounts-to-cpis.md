# FV-ANC-5-CL4 Passing unnecessary accounts to CPIs

## Bad


```rust
let cpi_accounts = vec![
    ctx.accounts.user.to_account_info(),
    ctx.accounts.unrelated_account.to_account_info(),
];
// Unrelated account included without need.
```

## Good


```rust
let cpi_accounts = vec![ctx.accounts.user.to_account_info()];
// Only necessary accounts are included.
```
