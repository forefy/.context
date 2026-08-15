# Finding Patterns - Safe Governance Hunt

## Scoring System

Each finding contributes to a `risk_score` (0–100+). Findings are bucketed by severity.

| Severity | Score Weight | Audit Category |
|----------|-------------|----------------|
| Critical | +35 | Immediate risk, likely exploitable path |
| High | +20–25 | Serious misconfiguration, material risk |
| Medium | +10–15 | Weakens security posture |
| Low | +5 | Centralization / best practice gap |
| Info | +0 | Noteworthy but not actionable alone |

Risk score thresholds:
- 0–15: ✅ Clean
- 16–35: 🟡 Low risk
- 36–55: 🟠 Medium risk
- 56–79: 🔴 High risk
- 80+: 🔴 Critical

---

## Finding Patterns

### CONFIG-01: Single-signer threshold
**Severity:** High (+25)
**Signal:** `threshold == 1`
**Condition:** Any single owner can execute without consensus
**Audit language:**
> "The Safe multisig is configured with a 1-of-N threshold, effectively granting any single owner unilateral control over privileged operations. This eliminates the core security guarantee of multisig governance."

---

### CONFIG-02: Low threshold ratio
**Severity:** Medium (+15)
**Signal:** `threshold / len(owners) < 0.4` AND `threshold > 1`
**Condition:** Too few signers relative to owner set
**Audit language:**
> "The threshold-to-owner ratio of {threshold}/{total} is below the recommended minimum of 40%. Compromising only {threshold} key(s) is sufficient to execute any transaction, disproportionate to the size of the signer set."

---

### CONFIG-03: No transaction guard
**Severity:** Medium (+10)
**Signal:** `guard == "0x0000000000000000000000000000000000000000"`
**Condition:** No policy enforcement layer on transactions
**Audit language:**
> "No transaction guard is configured on the Safe. Guards provide an additional enforcement layer that can validate or restrict transactions before execution. Without one, the Safe has no mechanism to enforce governance policies at the contract level."

---

### CONFIG-04: Unknown module enabled
**Severity:** High (+25)
**Signal:** `modules[]` contains address not in known-safe whitelist
**Condition:** Unaudited code with full Safe permissions
**Audit language:**
> "Module {address} is enabled on the Safe. Modules bypass the multisig threshold and can execute arbitrary transactions on behalf of the Safe. This module is not in the known-safe registry - if compromised or malicious, it represents a complete bypass of governance controls."

---

### CONFIG-05: Outdated Safe version
**Severity:** High (+20)
**Signal:** `version < "1.3.0"` (i.e. 1.2.0, 1.1.1, 1.1.0, 1.0.0)
**Condition:** Known vulnerabilities in old Safe versions
**Audit language:**
> "The Safe is running version {version}, which predates security improvements introduced in 1.3.0. Upgrading to a current version is recommended."

---

### CONFIG-06: Non-standard fallback handler
**Severity:** Medium (+10)
**Signal:** `fallbackHandler` not in known standard handlers list AND not zero address
**Condition:** Custom fallback handler may introduce unexpected behavior
**Audit language:**
> "A non-standard fallback handler ({address}) is configured. The fallback handler receives all calls to the Safe that don't match any function selector, including EIP-1271 signature validation. A custom handler could manipulate signature verification or introduce attack surface."

---

### HISTORY-01: Threshold decreased
**Severity:** High (+20)
**Signal:** Executed `changeThreshold` tx where new threshold < previous (infer from nonce ordering)
**Condition:** Governance was weakened
**Audit language:**
> "The threshold was decreased {N} time(s) in transaction history. Threshold reductions weaken the security posture of the multisig. Each decrease should be a documented, governance-approved action - unexplained threshold reductions are a red flag."

---

### HISTORY-02: Owner added
**Severity:** Medium (+10)
**Signal:** Executed `addOwner` or `addOwnerWithThreshold` txs
**Condition:** Signer set was expanded - verify authorization
**Audit language:**
> "{N} owner addition(s) were executed. Each owner addition expands the attack surface. Verify these were authorized governance decisions and that new owners' key management practices are adequate."

---

### HISTORY-03: Owner removed or swapped
**Severity:** Medium (+10)
**Signal:** Executed `removeOwner` or `swapOwner` txs
**Condition:** Signer changes may indicate compromise or internal conflict
**Audit language:**
> "{N} owner removal/swap transaction(s) in history. Verify these were authorized and that no owner was forcibly removed following a compromise event."

---

### HISTORY-04: Untrusted delegatecall
**Severity:** High (+25)
**Signal:** Executed tx with `operation == 1` and `to` not in trusted delegate list
**Condition:** Code execution in Safe's context from non-standard contract
**Trusted delegates:** MultiSend 1.3.0/1.4.0, MultiSendCallOnly 1.3.0/1.4.0
**Audit language:**
> "{N} delegatecall(s) to non-standard contract(s) ({targets}) found in history. Delegatecalls execute code in the Safe's storage context and can modify ownership, drain funds, or alter configuration. Any delegatecall target not in the trusted whitelist requires review."

---

### HISTORY-05: Gas token attack pattern
**Severity:** High (+20)
**Signal:** Executed tx with non-zero `gasToken` AND non-zero-address `refundReceiver`
**Condition:** Custom gas refund routing - potential gas token attack
**Audit language:**
> "Transaction(s) with custom gasToken ({token}) and refundReceiver ({receiver}) detected. This pattern can be used to drain Safe funds via gas refund manipulation. In legitimate usage, both fields should be the zero address."

---

### HISTORY-06: Single executor
**Severity:** Low (+5)
**Signal:** All (or >90%) recent executed txs submitted by same `executor` address, N >= 5
**Condition:** One person controls execution timing even if threshold > 1
**Audit language:**
> "All {N} recent executed transactions were submitted by a single executor ({address}). While the threshold requires multiple signatures, a single party controls execution timing and can delay or front-run transactions. Consider distributing executor responsibilities."

---

### HISTORY-07: Execution failures
**Severity:** Medium (+10)
**Signal:** Txs with `isExecuted == true` AND `isSuccessful == false`, count >= 2
**Condition:** Repeated failed executions may indicate attempted manipulation
**Audit language:**
> "{N} execution failure(s) in history. Failed executions still consume nonce and gas. Repeated failures may indicate misconfigured transactions, attempted exploits, or frontrunning."

---

### HISTORY-08: Pending high-risk tx
**Severity:** Critical (+35) if governance-changing, else High (+20)
**Signal:** Pending (unexecuted) tx with method in: `addOwnerWithThreshold`, `addOwner`, `removeOwner`, `swapOwner`, `changeThreshold`, `enableModule`, `changeMasterCopy`, `setGuard`
**Condition:** Active governance change awaiting execution - time-sensitive
**Audit language:**
> "A pending {method} transaction (nonce {nonce}) has {confirmations}/{required} confirmations and has not yet executed. This represents an active governance change that, if executed, would {impact}. Review urgently."

---

## Compound Findings

Some combinations escalate severity:

| Combo | Escalated Severity |
|-------|--------------------|
| threshold=1 + unknown module | Critical |
| no guard + threshold decreased + owner added | Critical |
| outdated version + unknown module | Critical |
| pending addOwner + threshold=1 | Critical |

---

## Not Findings (avoid false positives)

- `operation=1` to known MultiSend addresses → trusted, expected
- `changeThreshold` that *increased* the threshold → positive governance action
- `addOwner` with threshold increase → adding signer responsibly
- Standard fallback handler → expected, skip
- Empty `modules[]` → good, no finding
- `guard != 0x0` → good, has protection, note the address for review but not a finding
