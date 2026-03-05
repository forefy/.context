# FV-SOL-9 DoS and Unbounded Operations Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**22. Blacklistable or Pausable Token in Critical Payment Path**

**D:** Push-model transfer `token.transfer(recipient, amount)` with USDC/USDT or other blacklistable token. Blacklisted recipient reverts entire function, DOSing withdrawals/liquidations/fees.

**FP:** Pull-over-push pattern (recipients withdraw own funds). Skip-on-failure `try/catch` on fee distribution. Token whitelist excludes blacklistable tokens.

---

**25. DoS via Unbounded Loop**

**D:** Loop over user-growable unbounded array: `for (uint i = 0; i < users.length; i++)`. Eventually hits block gas limit.

**FP:** Array length capped at insertion: `require(arr.length < MAX)`. Loop iterates fixed small constant.

---

**77. Griefing via Dust Deposits Resetting Timelocks or Cooldowns**

**D:** Timelock/cooldown resets on any deposit with no minimum: `lastActionTime[user] = block.timestamp` inside `deposit(uint256 amount)` without `require(amount >= MIN)`. Attacker calls `deposit(1)` to reset victim's lock indefinitely.

**FP:** Minimum deposit enforced unconditionally. Cooldown resets only for depositing user. Lock assessed independently of deposit amounts per-user.

---

**82. Block Stuffing / Gas Griefing on Subcalls**

**D:** Time-sensitive function blockable by filling blocks. For relayer gas-forwarding griefing (63/64 rule), see Vector 30.

**FP:** Function not time-sensitive or window long enough that block stuffing is economically infeasible.

---

**110. DoS via Push Payment to Rejecting Contract**

**D:** ETH distribution in a single loop via `recipient.call{value:}("")`. Any reverting recipient blocks entire loop.

**FP:** Pull-over-push pattern. Loop uses `try/catch` and continues on failure.

---

**129. Front-Running Zero Balance Check with Dust Transfer**

**D:** `require(token.balanceOf(address(this)) == 0)` gates a state transition. Dust transfer makes balance non-zero, DoS-ing the function at negligible cost.

**FP:** Threshold check (`<= DUST_THRESHOLD`) instead of `== 0`. Access-controlled function. Internal accounting ignores direct transfers.

---

**146. Insufficient Gas Forwarding / 63/64 Rule**

**D:** External call without minimum gas budget: `target.call(data)` with no gas check. 63/64 rule leaves subcall with insufficient gas. In relayer patterns, subcall silently fails but outer tx marks request as "processed."

**FP:** `require(gasleft() >= minGas)` before subcall. Return value + returndata both checked. EIP-2771 with verified gas parameter.

---
