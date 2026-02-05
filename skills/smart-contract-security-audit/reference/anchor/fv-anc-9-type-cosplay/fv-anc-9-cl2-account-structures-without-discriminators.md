# FV-ANC-9-CL2 Account structures without discriminators

## Bad


```rust
#[account]
pub struct User {
    pub authority: Pubkey,
}
```

## Good


```rust
#[account]
pub struct User {
    pub discriminator: [u8; 8], // Unique discriminator for type validation
    pub authority: Pubkey,
}

impl User {
    pub const DISCRIMINATOR: [u8; 8] = *b"USERDATA";
}
```
