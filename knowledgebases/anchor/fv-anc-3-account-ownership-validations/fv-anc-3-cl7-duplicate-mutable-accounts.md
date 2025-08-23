# FV-ANC-3-CL7 Duplicate mutable accounts

## Bad


```rust
#[account(mut)]
pub user_a: Account<'info, User>;
#[account(mut)]
pub user_b: Account<'info, User>; // Could be the same as `user_a`.
```

## Good


```rust
#[account(mut, constraint = user_a.key() != user_b.key())]
pub user_a: Account<'info, User>;
pub user_b: Account<'info, User>; // Ensures `user_a` and `user_b` are distinct.
```
