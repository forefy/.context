# FV-ANC-4-CL3 PDA Sharing / Single Global Vault

## Bad


```rust
// One vault PDA holds funds for all users.
// Seeds contain no per-user component.
let (vault, bump) = Pubkey::find_program_address(&[b"vault"], ctx.program_id);
// Exploiting any user's position can drain the shared vault.
```

## Good


```rust
// Derive a separate vault PDA per user (or per position).
let (vault, bump) = Pubkey::find_program_address(
    &[b"vault", ctx.accounts.user.key().as_ref()],
    ctx.program_id,
);
// Compromise of one user's position cannot affect others.
```
