# FV-SOL-8 Slippage and MEV Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**86. Flash Loan-Assisted Price Manipulation**

**D:** Function reads price from on-chain source (AMM reserves, vault `totalAssets()`) manipulable atomically via flash loan + swap in same tx.

**FP:** TWAP with >= 30min window. Multi-block cooldown between price reads. Separate-block enforcement.

---

**95. Missing or Expired Deadline on Swaps**

**D:** `deadline = block.timestamp` (always valid), `deadline = type(uint256).max`, or no deadline. Tx holdable in mempool indefinitely.

**FP:** Deadline is calldata parameter validated as `require(deadline >= block.timestamp)`, not derived from `block.timestamp` internally.

---

**125. Missing Slippage Protection (Sandwich Attack)**

**D:** Swap/deposit/withdrawal with `minAmountOut = 0`, or `minAmountOut` computed on-chain from current pool state.

**FP:** `minAmountOut` set off-chain by user and validated on-chain.

---

**154. Slippage Enforced at Intermediate Step, Not Final Output**

**D:** Multi-hop swap checks `minAmountOut` on the first hop or an intermediate step, but the amount actually received by the user at the end of the pipeline has no independent slippage bound. Second/third hops can be sandwiched freely.

**FP:** `minAmountOut` validated against the user's final received balance (delta check). Single-hop swap. User specifies per-hop minimums.

---

**164. Oracle Price Update Front-Running**

**D:** On-chain oracle update tx visible in mempool. Attacker front-runs a favorable price update by opening a position at the stale price, then profits when the update lands. Pattern: Pyth/Chainlink push-model where update tx is submitted to public mempool.

**FP:** Protocol uses pull-based oracle (user submits price update atomically with their action). Private mempool (Flashbots Protect) for oracle updates. Price-update-and-action in single tx.

---
