# FV-SOL-10 Oracle Manipulation Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**55. Wrong Price Feed for Derivative or Wrapped Asset**

**D:** Protocol uses ETH/USD feed to price stETH collateral, or BTC/USD feed for WBTC. During normal conditions the error is small, but during depeg events the mispricing enables undercollateralized borrows or incorrect liquidations.

**FP:** Dedicated feed for the actual derivative asset (e.g., stETH/USD, WBTC/BTC). Deviation check against secondary oracle. Protocol documentation explicitly accepts depeg risk.

---

**69. Chainlink Staleness / No Validity Checks**

**D:** `latestRoundData()` called but missing checks: `answer > 0`, `updatedAt > block.timestamp - MAX_STALENESS`, `answeredInRound >= roundId`, fallback on failure.

**FP:** All four checks present. Circuit breaker or fallback oracle on failure.

---

**86. Flash Loan-Assisted Price Manipulation**

**D:** Function reads price from on-chain source (AMM reserves, vault `totalAssets()`) manipulable atomically via flash loan + swap in same tx.

**FP:** TWAP with >= 30min window. Multi-block cooldown between price reads. Separate-block enforcement.

---

**93. Chainlink Feed Deprecation / Wrong Decimal Assumption**

**D:** (a) Chainlink aggregator address hardcoded/immutable with no update path — deprecated feed returns stale/zero price. (b) Assumes `feed.decimals() == 8` without runtime check — some feeds return 18 decimals, causing 10^10 scaling error.

**FP:** Feed address updatable via governance. `feed.decimals()` called and used for normalization. Secondary oracle deviation check.

---

**124. Spot Price Oracle from AMM**

**D:** Price from AMM reserves: `reserve0 / reserve1`, `getAmountsOut()`, `getReserves()`. Flash-loan exploitable atomically.

**FP:** TWAP >= 30 min window. Chainlink/Pyth as primary source.

---

**137. Multi-Block TWAP Oracle Manipulation**

**D:** TWAP observation window < 30 minutes. Post-Merge validators controlling consecutive blocks can hold manipulated AMM state across blocks, shifting TWAP cheaply.

**FP:** TWAP window >= 30 min. Chainlink/Pyth as price source. Max-deviation circuit breaker against secondary source.

---

**141. Missing Oracle Price Bounds (Flash Crash / Extreme Value)**

**D:** Oracle returns a technically valid but extreme price (e.g., ETH at $0.01 during a flash crash). No min/max sanity bound or deviation check against historical/secondary price. Protocol executes liquidations or swaps at wildly incorrect prices.

**FP:** Circuit breaker: `require(price >= MIN_PRICE && price <= MAX_PRICE)`. Deviation check against secondary oracle source. Heartbeat + price-change-rate limiting.

---

**145. L2 Sequencer Uptime Not Checked**

**D:** Contract on L2 (Arbitrum/Optimism/Base) uses Chainlink feeds without querying L2 Sequencer Uptime Feed. Stale data during downtime triggers wrong liquidations.

**FP:** Sequencer uptime feed queried (`answer == 0` = up), with grace period after restart.

---
