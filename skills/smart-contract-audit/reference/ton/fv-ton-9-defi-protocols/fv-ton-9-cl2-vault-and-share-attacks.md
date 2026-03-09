# FV-TON-9-CL2 Vault and Share Price Attacks

## TLDR

Empty vaults are vulnerable to first-depositor inflation: a 1-unit deposit followed by a direct token transfer to the vault inflates the share price so the next depositor receives 0 shares (rounded down), losing their entire deposit to the attacker.

## Detection Heuristics

**No virtual shares or minimum deposit**
- Share calculation: `shares = deposit * total_supply / total_tokens` - when `total_supply = 1` and `total_tokens = attacker_donation + 1`, a victim deposit of `total_tokens - 1` yields 0 shares
- No virtual offset added to both numerator and denominator (virtual shares pattern)
- No minimum first deposit enforced to make the attack economically unattractive

**Share price from raw balance**
- `total_tokens` sourced from `my_balance` or the raw Jetton balance of the vault contract rather than from a tracked `total_deposited` variable
- Direct token transfers to the vault address (not through the deposit op) alter the share price

**Rounding direction exploitable**
- Both deposit (shares minted) and withdrawal (tokens returned) round in the user's favor - round-trip profit possible through repeated deposit/withdraw cycles
- Fee calculations that round DOWN consistently allow systematic underpayment

## False Positives

- Dead shares mechanism: a small amount of shares is minted to a burn address on vault creation, making the attack require a proportionally larger donation than any realistic attack budget
- Virtual shares: `shares = (deposit + VIRTUAL_OFFSET) * (total_supply + VIRTUAL_OFFSET) / (total_tokens + VIRTUAL_OFFSET)` - verify the offset is applied symmetrically and is large enough relative to expected minimum deposits
