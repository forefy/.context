# FV-ANC-2-CL2 No is\_signer check

## Bad


```rust
// Signer validation missing entirely
if authority.key != expected_authority_key {
    return Err(ProgramError::MissingRequiredSignature);
}
```

## Good


```rust
// Explicitly ensure the signer has signed
if !ctx.accounts.authority.is_signer {
    return Err(ProgramError::MissingRequiredSignature);
}
```
