# FV-ANC-4-CL2 PDA Seed Concatenation Collision

## Bad


```rust
// Seeds are concatenated without length-prefixing or separators.
// ["AB", "C"] and ["A", "BC"] produce identical raw seed bytes
// and therefore the same PDA.
let pda = Pubkey::find_program_address(
    &[prefix.as_bytes(), suffix.as_bytes()],
    program_id,
);
```

## Good


```rust
// Use a fixed-length or hashed representation so seeds are unambiguous.
let pda = Pubkey::find_program_address(
    &[
        &(prefix.len() as u32).to_le_bytes(),
        prefix.as_bytes(),
        suffix.as_bytes(),
    ],
    program_id,
);
// Or use distinct constant separators between variable-length fields.
```
