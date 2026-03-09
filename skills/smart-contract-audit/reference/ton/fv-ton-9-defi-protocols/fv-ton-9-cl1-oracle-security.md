# FV-TON-9-CL1 Oracle Security

## TLDR

TON DeFi oracle vulnerabilities mirror EVM patterns: stale prices, missing confidence validation, fake oracle contracts, single-source dependency, and on-chain spot price manipulation are all exploitable in TON lending and derivatives protocols.

## Detection Heuristics

**Stale price acceptance**
- Price consumed from oracle message without `throw_unless(error::stale_price, now - last_update_time <= MAX_STALENESS)` check
- No `last_update_time` field stored alongside the price
- Oracle update messages not carrying a timestamp field

**Missing confidence validation**
- Price oracle (e.g., Pyth on TON) provides a confidence interval but only the midpoint price is used
- No check `throw_unless(error::low_confidence, confidence < MAX_ACCEPTABLE_CONFIDENCE)`
- Calculations use the midpoint price in volatile conditions when the spread makes the value unreliable

**Fake oracle sender**
- Price update handler does not verify `sender_address == stored_oracle_address`
- Oracle address not stored in contract data or not checked before processing the price
- Any contract can call the price update op and submit arbitrary prices

**On-chain spot price as oracle**
- Price derived from live AMM pool reserves (`reserve_a / reserve_b`) rather than a TWAP or external price feed
- Lending collateral value calculated from manipulable DEX spot price - flash loan can inflate/deflate

## False Positives

- Contract only accepts price updates from a hardcoded factory-deployed oracle whose address is derived and verified via StateInit hash
- Confidence check is present but implemented as a comparison with a named constant - verify the constant is restrictive enough for the protocol's risk tolerance
