# FV-ANC-1-CL3 Arbitrary rounding

## Bad


```rust
// Using arbitrary rounding, which might lead to loss of precision
let rounded = collateral.try_round_u64()?;
```

## Good


```rust
// Using floor rounding for consistent and predictable behavior
let rounded = collateral.try_floor_u64()?;
```
