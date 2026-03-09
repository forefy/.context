# FV-ANC-12-CL2 Oracle Confidence Interval and Status Flags Ignored

## TLDR

Pyth price feeds publish a confidence interval alongside each price representing the uncertainty in the reported value. Ignoring this interval allows the protocol to act on prices with high uncertainty, which can be exploited during volatile markets. Additionally, Pyth's `status` field signals whether the feed is actively trading or in an error/halted state; using a price with a non-Trading status can result in grossly incorrect valuations.

## Detection Heuristics

**Confidence Interval Not Checked**
- `price.conf` field read but not validated against a maximum acceptable ratio (e.g., `conf / price.price > MAX_CONF_RATIO`)
- Protocol uses `price.price` directly without any confidence-based rejection or uncertainty adjustment
- No configurable `max_confidence_bps` parameter in the protocol's oracle config struct

**Status Field Ignored**
- `price.status` not compared against `PriceStatus::Trading` before using the price value
- Program proceeds when `price.status == PriceStatus::Unknown` or `PriceStatus::Halted`, using potentially zeroed or stale price data
- Pyth `PriceFeed` deserialized but `status` field access skipped in the price validation helper

**Circuit Breaker Absent**
- No maximum price deviation check (e.g., new price must not exceed 2x previous price) that would reject oracle values during extreme market events or feed manipulation
- No `min_price` or `max_price` bounds on accepted oracle values, allowing a compromised oracle to report near-zero or astronomically high prices without rejection

## False Positives

- Protocol applies a configurable confidence ratio check and a status check before every price use, returning a specific error code on violation
- Market conditions and oracle type make confidence intervals consistently tight; protocol documentation acknowledges and accepts the confidence model
