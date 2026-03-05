# FV-SOL-2 Precision Errors Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**4 Token Decimal Mismatch in Cross-Token Arithmetic**

**D:** Cross-token math uses hardcoded `1e18` or assumes identical decimals. Pattern: collateral/LTV/rate calculations combining token amounts without per-token `decimals()` normalization.

**FP:** Amounts normalized to canonical precision (WAD/RAY) using each token's `decimals()`. Explicit `10 ** (18 - decimals())` scaling. Protocol only supports tokens with identical verified decimals.

---

**26 Precision Loss - Division Before Multiplication**

**D:** `(a / b) * c` — truncation before multiplication amplifies error. E.g., `fee = (amount / 10000) * bps`. Correct: `(a * c) / b`.

**FP:** `a` provably divisible by `b` (enforced by `require(a % b == 0)` or mathematical construction).

---

**35 Batch Distribution Dust Residual**

**D:** Loop distributes funds proportionally: `share = total * weight[i] / totalWeight`. Cumulative rounding causes `sum(shares) < total`, leaving dust locked in contract. Pattern: N recipients each computed independently without remainder handling.

**FP:** Last recipient gets `total - sumOfPrevious`. Dust swept to treasury. `mulDiv` with accumulator tracking. Protocol accepts bounded dust loss by design.

---

**56 ERC4626 Preview Rounding Direction Violation**

**D:** `previewDeposit` returns more shares than `deposit` mints, or `previewMint` charges fewer assets than `mint`. Custom `_convertToShares`/`_convertToAssets` with wrong `Math.mulDiv` rounding direction.

**FP:** OZ ERC4626 base without overriding conversion functions. Custom impl explicitly uses `Floor` for share issuance, `Ceil` for share burning.

---

**66 ERC4626 Deposit/Withdraw Share-Count Asymmetry**

**D:** `_convertToShares` uses `Rounding.Floor` for both deposit and withdraw paths. `withdraw(a)` burns fewer shares than `deposit(a)` minted, manufacturing free shares. Single rounding helper called on both paths without distinct rounding args.

**FP:** `deposit` uses `Floor`, `withdraw` uses `Ceil` (vault-favorable both directions). OZ ERC4626 without custom conversion overrides.

---

**67 ERC4626 Mint/Redeem Asset-Cost Asymmetry**

**D:** `redeem(s)` returns more assets than `mint(s)` costs — cycling yields net profit. Root cause: `_convertToAssets` rounds up in `redeem` and down in `mint` (opposite of EIP-4626 spec). Pattern: `previewRedeem` uses `Rounding.Ceil`, `previewMint` uses `Rounding.Floor`.

**FP:** `redeem` uses `Math.Rounding.Floor`, `mint` uses `Math.Rounding.Ceil`. OZ ERC4626 without custom conversion overrides.

---

**120 Rounding in Favor of the User**

**D:** `shares = assets / pricePerShare` rounds down for deposit but up for redeem. Division without explicit rounding direction. First-depositor donation amplifies the error.

**FP:** `Math.mulDiv` with explicit `Rounding.Up` where vault-favorable. OZ ERC4626 `_decimalsOffset()`. Dead shares at init.

---
