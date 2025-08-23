# FV-ANC-1-CL2 Division by zero

## Bad


```rust
// Risk of crashing if divisor is zero
let avg = total / count;
```

## Good


```rust
// Explicitly check for zero divisor before division
if count == 0 {
    return Err(ProgramError::InvalidArgument);
}
let avg = total / count;
```
