# FV-ANC-12-CL1 Stale Oracle Price Accepted Without Freshness Check

## TLDR

Pyth and Switchboard price feeds publish a `publish_time` timestamp with each price update. If a program reads the price without comparing this timestamp against `Clock.unix_timestamp`, it may act on prices that are seconds, minutes, or hours old, allowing exploitation during oracle outages, network congestion, or feed manipulation periods where the on-chain price diverges from the real market price.

## Detection Heuristics

**No Publish Time Validation**
- `price_account.try_get_price_no_older_than(clock, max_age_seconds)` not used; raw `price_account.get_price_unchecked()` or direct deserialization used instead
- `PriceFeed.publish_time` or `AggregatorAccountData.latest_confirmed_round.round_open_slot` not compared against current `Clock.unix_timestamp` or `Clock.slot`
- Max age threshold missing or set to an unreasonably large value (e.g., 3600 seconds for a protocol that needs sub-minute freshness)

**Pyth-Specific Patterns**
- `Price::get_price_no_older_than` call missing the clock argument; stale prices accepted silently
- `Price.status` field not checked for `PriceStatus::Trading` before use
- Oracle account not verified against a hardcoded expected address; any account with matching layout accepted

**Switchboard-Specific Patterns**
- `AggregatorAccountData.latest_confirmed_round.round_open_slot` not checked against current slot with a staleness window
- `staleness_threshold` in Switchboard feed config not validated against protocol requirements at initialization

## False Positives

- Protocol calls `try_get_price_no_older_than` with an appropriately tight max age for the operation's sensitivity
- Oracle update frequency is guaranteed by the feed operator to be faster than the protocol's staleness tolerance, and the program enforces this at the instruction level
