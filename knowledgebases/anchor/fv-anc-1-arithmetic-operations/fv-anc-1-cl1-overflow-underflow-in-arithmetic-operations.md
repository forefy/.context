# FV-ANC-1-CL1 Overflow/underflow in arithmetic operations

## Bad

```rust
// Adding two values without handling overflow
let balance = ctx.accounts.user.balance + amount;
```

## Good

```rust
// Using `checked_add` to safely handle overflow
let balance = ctx.accounts.user.balance.checked_add(amount).ok_or(ProgramError::InvalidArgument)?;
```
