# FV-ANC-7-CL3 Token-2022 Incompatibility

## Bad


```rust
// anchor_spl::token::transfer is hardcoded to the legacy Token program ID.
// Calling it with a Token-2022 mint silently fails or panics at runtime.
use anchor_spl::token::{self, Transfer};

let cpi_ctx = CpiContext::new(
    ctx.accounts.token_program.to_account_info(),
    Transfer {
        from: ctx.accounts.from.to_account_info(),
        to: ctx.accounts.to.to_account_info(),
        authority: ctx.accounts.authority.to_account_info(),
    },
);
token::transfer(cpi_ctx, amount)?;
```

## Good


```rust
// Use the token_interface module which handles both Token and Token-2022.
use anchor_spl::token_interface::{self, TransferChecked};

let cpi_ctx = CpiContext::new(
    ctx.accounts.token_program.to_account_info(),
    TransferChecked {
        from: ctx.accounts.from.to_account_info(),
        mint: ctx.accounts.mint.to_account_info(),
        to: ctx.accounts.to.to_account_info(),
        authority: ctx.accounts.authority.to_account_info(),
    },
);
token_interface::transfer_checked(cpi_ctx, amount, decimals)?;
```
