# FV-ANC-10-CL1 Closing accounts without zeroing data & setting a closed discriminator

## Bad


```rust
let lamports = ctx.accounts.account.lamports();
**ctx.accounts.destination.lamports.borrow_mut() = lamports;
**ctx.accounts.account.lamports.borrow_mut() = 0;
// Leaves account data intact, allowing potential misuse.
```

## Good


```rust
let lamports = ctx.accounts.account.lamports();
**ctx.accounts.destination.lamports.borrow_mut() = lamports;
**ctx.accounts.account.lamports.borrow_mut() = 0;

let mut data = ctx.accounts.account.try_borrow_mut_data()?;
for byte in data.iter_mut() {
    *byte = 0; // Zero out data.
}
let closed_discriminator: [u8; 8] = *b"CLOSEDAC";
data[..8].copy_from_slice(&closed_discriminator); // Add closed discriminator.
```
