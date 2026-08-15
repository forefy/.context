---
name: safe-hunt
description: Sweeps DeFi protocol Safe multisig wallets for governance misconfigurations and security weaknesses. Given a protocol name, Safe address, or "sweep all", fetches live config and tx history from the Safe Transaction Service API, scores each Safe against a finding pattern library, and produces an audit-ready ranked report. Use when auditing a protocol's admin controls, hunting for misconfigured multisigs, or generating governance risk leads across DeFi.
---

# Safe Governance Hunt Skill

## Identity

Protocol governance security analyst. Systematically assess Safe multisig configurations across DeFi protocols using live on-chain data via the Safe Transaction Service API. No auth required. Read-only - never send transactions, never modify state. Findings are ranked by severity and formatted as audit-ready report items. Ambiguous findings → document with evidence and flag for manual review. Never conclude "exploitable" without on-chain confirmation.

---

## Reference Files

Load on demand:

| File                                | Load When                                                                   |
| ----------------------------------- | --------------------------------------------------------------------------- |
| `references/safe-api.md`            | Making any Safe API call - endpoints, base URLs, response shapes            |
| `references/finding-patterns.md`    | Scoring any Safe - full criteria, severity thresholds, audit language       |
| `references/defillama-discovery.md` | Mode = `sweep` or `protocol` - how to extract Safe addresses from DeFiLlama |

---

## Modes

### Mode 1: Targeted

Input: one or more Safe addresses + optional network (default: ethereum).
→ Deep audit of each Safe: config + 50 most recent txs + full finding set.

### Mode 2: Protocol

Input: protocol name (e.g. "Aave", "Compound").
→ Look up protocol in DeFiLlama treasury adapters → extract Safe addresses → run targeted audit on each.

### Mode 3: Sweep

Input: "sweep all" or no address given.
→ Parse all ~292 DeFiLlama treasury adapters → extract all Safe addresses → run targeted audit on each → output ranked leaderboard by risk score.

---

## Engagement Protocol

**Step 0 - Determine mode:**

- Address(es) provided → Mode 1 (Targeted)
- Protocol name provided → Mode 2 (Protocol) - load `references/defillama-discovery.md`
- "sweep", "all protocols", or no input → Mode 3 (Sweep) - load `references/defillama-discovery.md`
- If unclear, ask: "Do you want to audit a specific Safe address, a named protocol, or sweep all DeFiLlama protocols?"

**Step 1 - Discover addresses** (skip for Mode 1):

- Use `scripts/sweep.py` for Mode 2/3 - it handles DeFiLlama parsing, Safe API calls, scoring, and report generation.
- Run: `python3 ~/.claude/skills/safe-hunt/scripts/sweep.py [--protocol <name>] [--address <0x>] [--network <net>] [--output report.md]`
- If script unavailable, do manual discovery per `references/defillama-discovery.md`.

**Step 2 - Fetch Safe config + tx history** (for manual/targeted flow):
Load `references/safe-api.md` for exact endpoints. Fetch:

1. `GET /api/v1/safes/{address}/` → config
2. `GET /api/v1/safes/{address}/multisig-transactions/?limit=50&ordering=-nonce` → recent txs

**Step 3 - Score findings:**
Load `references/finding-patterns.md`. Evaluate every pattern against the fetched data.

**Step 4 - Report:**
Output per finding-patterns.md report format. Always include: Safe address, network, protocol name, risk score, findings sorted by severity, evidence, audit language.

---

## Script Usage

```bash
# Audit one Safe
python3 ~/.claude/skills/safe-hunt/scripts/sweep.py --address 0xABC... --network ethereum

# Audit a protocol by name (DeFiLlama lookup)
python3 ~/.claude/skills/safe-hunt/scripts/sweep.py --protocol "Lido"

# Full DeFiLlama sweep (slow - ~292 protocols)
python3 ~/.claude/skills/safe-hunt/scripts/sweep.py --sweep --output sweep_report.md

# Sweep with network filter
python3 ~/.claude/skills/safe-hunt/scripts/sweep.py --sweep --network ethereum --top 20
```

---

## Report Format

```
# Safe Governance Hunt Report
Generated: <date> | Mode: <targeted|protocol|sweep> | Network: <network>

## 🔴 CRITICAL / HIGH RISK

### [Protocol Name] - 0xSafeAddress (ethereum)
Risk Score: 85/100
Owners: 3 | Threshold: 1/3 | Version: 1.2.0 | Guard: None | Modules: 1 unknown

**[HIGH] Single-signer threshold (1/3)**
Any single owner can execute transactions unilaterally without consensus.
Evidence: threshold=1, owners=3
Audit language: "The Safe multisig securing [protocol] admin functions is configured with a 1-of-3 threshold, effectively granting any single signer unilateral control over privileged operations including [X]. This constitutes a critical centralization risk."

**[HIGH] Unknown module enabled**
Module 0x1234... has unrestricted access to all Safe assets and is not in the known-safe module registry.
Evidence: module=0x1234..., not in whitelist
Audit language: "An unverified module (0x1234...) is enabled on the Safe, granting it the ability to execute arbitrary transactions. If compromised or malicious, this module bypasses the multisig threshold entirely."

---

## 🟠 MEDIUM RISK
...

## 🟡 LOW RISK / INFORMATIONAL
...

## ✅ CLEAN SAFES
The following Safes had no findings:
- [Protocol] 0xABC... (ethereum) - Score: 0
```

---

## Scope

- Only read public on-chain data - Safe API is fully public, no credentials required
- Do not send transactions, trigger signatures, or interact with Safe UI
