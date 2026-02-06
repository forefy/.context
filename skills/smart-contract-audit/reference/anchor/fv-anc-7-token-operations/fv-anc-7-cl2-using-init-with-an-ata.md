# FV-ANC-7-CL2 Using init with an ATA

## Bad


```rust
// init expects ATA to be uninitilized, but any ATA (like one that is already initiated) can be provided, cauisng a DoS
#[account(
    init,
    payer = initializer,
    associated_token::mint = mint,
    associated_token::authority = authorityacc,
    associated_token::token_program = token_program,
)]
pub payment_ta: Box<InterfaceAccount<'info, TokenAccount>>
```

## Good


```rust
// init_if_needed won't cause a DoS in the same case
#[account(
    init_if_needed,
    payer = initializer,
    associated_token::mint = mint,
    associated_token::authority = authorityacc,
    associated_token::token_program = token_program,
)]
pub payment_ta: Box<InterfaceAccount<'info, TokenAccount>>
```
