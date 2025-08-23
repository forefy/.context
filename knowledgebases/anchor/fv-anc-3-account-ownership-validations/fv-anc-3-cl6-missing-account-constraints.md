# FV-ANC-3-CL6 Missing account constraints

## Bad


```rust
#[account]
pub vault: Account<'info, Vault>;
pub admin: Signer<'info>; // No dependency enforced.
```

## Good


```rust
#[account(has_one = admin)]
pub vault: Account<'info, Vault>;
pub admin: Signer<'info>; // Validates `admin` dependency.
```
