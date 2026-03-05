# FV-ANC-3-CL13 init\_if\_needed Without Reinitialization Guard

## Bad


```rust
#[account(
    init_if_needed,
    payer = user,
    space = 8 + UserData::SIZE,
    seeds = [b"user", user.key().as_ref()],
    bump,
)]
pub user_data: Account<'info, UserData>,
// Attacker pre-creates this PDA with malicious initial state;
// subsequent call skips init and uses attacker-controlled data.
```

## Good


```rust
#[account(
    init_if_needed,
    payer = user,
    space = 8 + UserData::SIZE,
    seeds = [b"user", user.key().as_ref()],
    bump,
)]
pub user_data: Account<'info, UserData>,

// In instruction body, reject if already initialized with unexpected state
if user_data.is_initialized {
    require!(user_data.authority == ctx.accounts.user.key(), ErrorCode::Unauthorized);
}
user_data.is_initialized = true;
user_data.authority = ctx.accounts.user.key();
```
