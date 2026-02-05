# FV-ANC-3-CL12 Not validating a set address

## Bad


```rust
pub fn handler(ctx: Context<MyContext>) -> Result<()> {
    ctx.accounts.x = new_address; // No validation
    Ok(())
}
```

## Good


```rust
pub fn handler(ctx: Context<MyContext>) -> Result<()> {
    // prevent system program address
    // prevent pda or program address
    // verify address exists and can receive tokens
    // only then dot he update
    ctx.accounts.x = new_address;
    Ok(())
}
```
