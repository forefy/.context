# FV-ANC-10-CL3 Unintended closure by close constraint

The `close`constraint in anchor is used to automatically close an account after a transaction finishes. Although useful, it can lead to confusion on account closure and introduce false assumptions of when the close occurs or not.

## Bad


```rust
// No checks for closed accounts in other program functions.
#[account(mut, close = <target>)]
pub order: Account<'info>

// implementation does not expect closure at the end
```

## Good


```rust
[account(mut)]
pub order: Account<'info>
// Handle closure manually in the implementation
```
