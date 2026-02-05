# FV-ANC-5-CL1 Lack of validation of external program before CPI

## Bad


```rust
// Assumes external program is correct without validation
let cpi_program = ctx.accounts.external_program.to_account_info();
```

## Good


```rust
// Explicitly verify the target program ID before CPI
if ctx.accounts.external_program.key() != &spl_token::ID {
    return Err(ProgramError::IncorrectProgramId);
}

let cpi_program = ctx.accounts.external_program.to_account_info();
```
