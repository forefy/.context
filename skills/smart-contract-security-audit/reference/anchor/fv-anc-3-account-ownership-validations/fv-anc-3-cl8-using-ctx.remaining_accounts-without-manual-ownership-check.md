# FV-ANC-3-CL8 Using ctx.remaining\_accounts without manual ownership check

## Bad


```rust
let extra_account = &ctx.remaining_accounts[0];
// No ownership validation performed.
```

## Good


```rust
let extra_account = &ctx.remaining_accounts[0];
if extra_account.owner != &expected_program_id {
    return Err(ProgramError::IllegalOwner);
}
```
