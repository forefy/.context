# FV-ANC-4-CL1 Using create\_program\_address

## Bad


```rust
let (pda, _) = Pubkey::create_program_address(&[seed, &[bump]], ctx.program_id);
// No validation to ensure PDA is derived correctly
```

## Good

<pre class="language-rust" data-overflow="wrap" data-line-numbers><code class="lang-rust">// Verify PDA derivation using `find_program_address`
<strong>let (expected_pda, expected_bump) = Pubkey::find_program_address(&#x26;[seed], ctx.program_id);
</strong>if ctx.accounts.pda.key() != expected_pda || bump != expected_bump {
    return Err(ProgramError::InvalidArgument);
}
</code></pre>
