# FV-ANC-3-CL14 realloc Without zero\_init

## Bad


```rust
#[account(
    mut,
    realloc = 8 + DataStore::new_size(new_count),
    realloc::payer = user,
    realloc::zero_init = false,  // stale bytes from previous allocation remain
)]
pub data_store: Account<'info, DataStore>,
```

## Good


```rust
#[account(
    mut,
    realloc = 8 + DataStore::new_size(new_count),
    realloc::payer = user,
    realloc::zero_init = true,   // zeroes any newly exposed bytes
)]
pub data_store: Account<'info, DataStore>,
```
