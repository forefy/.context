# FV-ANC-3-CL3 Usage of UncheckedAccount without manual ownership check

## Bad


```rust
#[account]
pub external_account: UncheckedAccount<'info>; // No validation.
```

## Good


```rust
#[account]
pub external_account: UncheckedAccount<'info>;

// When using UncheckedAccount, manually validate the same constraints Anchor enforces automatically.
if external_account.owner != &expected_owner_program_id {
    return Err(ProgramError::IllegalOwner);
}
```
