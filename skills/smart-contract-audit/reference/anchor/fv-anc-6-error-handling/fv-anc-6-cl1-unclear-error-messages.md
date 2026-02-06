# FV-ANC-6-CL1 Unclear error messages

## Bad


```rust
// Generic and unclear error messages
return Err(ProgramError::InvalidInstructionData);
```

## Good


```rust
// Clear and descriptive custom error codes
#[error_code]
pub enum CustomError {
    #[msg("Invalid configuration.")]
    InvalidConfig,
}

return Err(CustomError::InvalidConfig.into());
```
