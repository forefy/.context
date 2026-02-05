# FV-ANC-5-CL2 CPI without signer seeds

Caveat - if it's a user doing the transfer, not a PDA, empty seeds might be ok

## Bad


```rust
// CPI signer seeds missing
invoke_signed(&instruction, &accounts, &[]);
```

## Good


```rust
// Provide signer seeds securely during CPI
let seeds = &[b"vault".as_ref(), &[bump]];
invoke_signed(&instruction, &accounts, &[seeds]);
```
