#!/usr/bin/env python3
"""
Safe Governance Hunt - sweep.py
Discovers and audits Safe multisig configurations across DeFi protocols.

Usage:
  python3 sweep.py --address 0xABC... [--network ethereum]
  python3 sweep.py --protocol "Lido"
  python3 sweep.py --sweep [--network ethereum] [--top 20] [--output report.md]
"""

import asyncio
import aiohttp
import argparse
import json
import re
import ssl
import sys
import certifi
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def checksum_address(addr: str) -> str:
    """Compute EIP-55 checksummed address."""
    try:
        from web3 import Web3
        return Web3.to_checksum_address(addr)
    except Exception:
        pass
    # Fallback: pycryptodome keccak256
    from Crypto.Hash import keccak as _keccak
    addr_clean = addr.lower().replace("0x", "")
    k = _keccak.new(digest_bits=256)
    k.update(addr_clean.encode())
    h = k.hexdigest()
    return "0x" + "".join(c.upper() if int(h[i], 16) >= 8 else c for i, c in enumerate(addr_clean))

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

SAFE_API_BASES = {
    "ethereum":  "https://api.safe.global/tx-service/eth/api/v1",
    "polygon":   "https://api.safe.global/tx-service/pol/api/v1",
    "arbitrum":  "https://api.safe.global/tx-service/arb1/api/v1",
    "optimism":  "https://api.safe.global/tx-service/oeth/api/v1",
    "base":      "https://api.safe.global/tx-service/base/api/v1",
    "gnosis":    "https://api.safe.global/tx-service/gno/api/v1",
    "avalanche": "https://api.safe.global/tx-service/avax/api/v1",
    "bnb":       "https://api.safe.global/tx-service/bnb/api/v1",
    "sepolia":   "https://api.safe.global/tx-service/sep/api/v1",
}

DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"
DEFILLAMA_ADAPTER_BASE = "https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/treasury/"

TRUSTED_DELEGATES = {
    "0x40a2accbd92bca938b02010e17a5b8929b49130d",  # MultiSend 1.3.0
    "0xa238cbeb142c10ef7ad8442c6d1f9e89e07e7761",  # MultiSend 1.4.0
    "0x998739bfdaadde7c933b942a68053933098f9eda",  # MultiSendCallOnly 1.3.0
    "0x9641d764fc13c8b624c04430c7356c1c7c8102e2",  # MultiSendCallOnly 1.4.0
}

STANDARD_FALLBACK_HANDLERS = {
    "0xf48f2b2d2a534e402487b3ee7c18c33aec0fe5e4",  # CompatibilityFallbackHandler 1.3.0
    "0xfd0732dc9e303f09fcef3a7388ad10a83459ec99",  # CompatibilityFallbackHandler 1.4.0
}

ZERO_ADDR = "0x0000000000000000000000000000000000000000"
ETH_ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

GOVERNANCE_METHODS = {
    "addOwner", "addOwnerWithThreshold", "removeOwner", "swapOwner",
    "changeThreshold", "enableModule", "disableModule",
    "changeMasterCopy", "setGuard", "setFallbackHandler", "setup",
}

# ──────────────────────────────────────────────
# Data models
# ──────────────────────────────────────────────

@dataclass
class Finding:
    severity: str       # critical, high, medium, low, info
    code: str           # e.g. CONFIG-01
    title: str
    detail: str
    audit_language: str
    evidence: dict = field(default_factory=dict)
    score: int = 0

@dataclass
class SafeResult:
    address: str
    network: str
    protocol: str
    safe_info: Optional[dict] = None
    findings: list = field(default_factory=list)
    risk_score: int = 0
    error: Optional[str] = None

    @property
    def risk_label(self):
        s = self.risk_score
        if s >= 80: return "🔴 CRITICAL"
        if s >= 56: return "🔴 HIGH"
        if s >= 36: return "🟠 MEDIUM"
        if s >= 16: return "🟡 LOW"
        return "✅ CLEAN"

# ──────────────────────────────────────────────
# Safe API
# ──────────────────────────────────────────────

async def fetch_safe_info(session: aiohttp.ClientSession, address: str, network: str) -> Optional[dict]:
    base = SAFE_API_BASES.get(network)
    if not base:
        return None
    address = checksum_address(address)
    url = f"{base}/safes/{address}/"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status == 404:
                return None
            if r.status == 429:
                await asyncio.sleep(5)
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r2:
                    if r2.status != 200:
                        return None
                    return await r2.json()
            if r.status != 200:
                return None
            return await r.json()
    except Exception:
        return None


async def fetch_transactions(session: aiohttp.ClientSession, address: str, network: str, limit: int = 50) -> list:
    base = SAFE_API_BASES.get(network)
    if not base:
        return []
    address = checksum_address(address)
    url = f"{base}/safes/{address}/multisig-transactions/?limit={limit}&ordering=-nonce"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as r:
            if r.status != 200:
                return []
            data = await r.json()
            return data.get("results", [])
    except Exception:
        return []

# ──────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────

def analyze_safe(safe_info: dict, txs: list, address: str, network: str, protocol: str) -> SafeResult:
    result = SafeResult(address=address, network=network, protocol=protocol, safe_info=safe_info)

    threshold = safe_info.get("threshold", 0)
    owners = safe_info.get("owners", [])
    guard = (safe_info.get("guard") or ZERO_ADDR).lower()
    modules = safe_info.get("modules") or []
    version = safe_info.get("version") or "unknown"
    fallback = (safe_info.get("fallbackHandler") or ZERO_ADDR).lower()
    owner_count = len(owners)

    executed = [t for t in txs if t.get("isExecuted")]
    pending  = [t for t in txs if not t.get("isExecuted")]

    # ── CONFIG-01: Single-signer threshold ────────────────────────────────
    if threshold == 1:
        result.findings.append(Finding(
            severity="high", code="CONFIG-01",
            title=f"Single-signer threshold (1/{owner_count})",
            detail=f"Threshold is 1/{owner_count} - any single owner can execute transactions unilaterally.",
            audit_language=(
                f"The Safe multisig is configured with a 1-of-{owner_count} threshold, effectively granting "
                f"any single owner unilateral control over privileged operations. This eliminates the core "
                f"security guarantee of multisig governance."
            ),
            evidence={"threshold": threshold, "owners": owner_count},
            score=25,
        ))

    # ── CONFIG-02: Low threshold ratio ────────────────────────────────────
    elif owner_count > 0 and threshold > 1 and (threshold / owner_count) < 0.4:
        ratio = round(threshold / owner_count, 2)
        result.findings.append(Finding(
            severity="medium", code="CONFIG-02",
            title=f"Low threshold ratio ({threshold}/{owner_count} = {ratio})",
            detail=f"Only {threshold} of {owner_count} owners required - ratio {ratio} is below 0.40.",
            audit_language=(
                f"The threshold-to-owner ratio of {threshold}/{owner_count} ({ratio}) is below the recommended "
                f"minimum of 40%. Compromising only {threshold} key(s) is sufficient to execute any transaction."
            ),
            evidence={"threshold": threshold, "owners": owner_count, "ratio": ratio},
            score=15,
        ))

    # ── CONFIG-03: No guard ────────────────────────────────────────────────
    if guard == ZERO_ADDR:
        result.findings.append(Finding(
            severity="medium", code="CONFIG-03",
            title="No transaction guard configured",
            detail="guard == 0x0 - no policy enforcement layer on transaction execution.",
            audit_language=(
                "No transaction guard is configured on the Safe. Guards provide an additional enforcement "
                "layer that can validate or restrict transactions before execution. Without one, the Safe "
                "has no mechanism to enforce governance policies at the contract level."
            ),
            evidence={"guard": safe_info.get("guard")},
            score=10,
        ))

    # ── CONFIG-04: Unknown modules ─────────────────────────────────────────
    for module in modules:
        result.findings.append(Finding(
            severity="high", code="CONFIG-04",
            title=f"Unknown module enabled: {module[:10]}...",
            detail=f"Module {module} has unrestricted Safe access and is not in the known-safe whitelist.",
            audit_language=(
                f"Module {module} is enabled on the Safe. Modules bypass the multisig threshold and can "
                f"execute arbitrary transactions on behalf of the Safe. This module is not in the known-safe "
                f"registry - if compromised or malicious, it represents a complete bypass of governance controls."
            ),
            evidence={"module": module},
            score=25,
        ))

    # ── CONFIG-05: Outdated version ────────────────────────────────────────
    if version not in ("unknown",) and version < "1.3.0":
        result.findings.append(Finding(
            severity="high", code="CONFIG-05",
            title=f"Outdated Safe version ({version})",
            detail=f"Version {version} predates security improvements in Safe 1.3.0.",
            audit_language=(
                f"The Safe is running version {version}, which predates security improvements introduced "
                f"in 1.3.0. Upgrading to a current version is recommended."
            ),
            evidence={"version": version, "masterCopy": safe_info.get("masterCopy")},
            score=20,
        ))

    # ── CONFIG-06: Non-standard fallback handler ───────────────────────────
    if fallback not in STANDARD_FALLBACK_HANDLERS and fallback != ZERO_ADDR:
        result.findings.append(Finding(
            severity="medium", code="CONFIG-06",
            title=f"Non-standard fallback handler",
            detail=f"fallbackHandler {safe_info.get('fallbackHandler')} is not in the known-safe list.",
            audit_language=(
                f"A non-standard fallback handler ({safe_info.get('fallbackHandler')}) is configured. "
                f"The fallback handler receives EIP-1271 signature validation calls and all unmatched "
                f"function selectors. A custom handler could manipulate signature verification."
            ),
            evidence={"fallbackHandler": safe_info.get("fallbackHandler")},
            score=10,
        ))

    # ── HISTORY-01: Threshold decreased ───────────────────────────────────
    threshold_decreases = []
    for tx in executed:
        dd = tx.get("dataDecoded") or {}
        if dd.get("method") == "changeThreshold":
            params = dd.get("parameters") or []
            new_val = next((int(p["value"]) for p in params if p.get("name") == "_threshold"), None)
            if new_val is not None and new_val < threshold:
                threshold_decreases.append(tx)

    if threshold_decreases:
        result.findings.append(Finding(
            severity="high", code="HISTORY-01",
            title=f"Threshold decreased ({len(threshold_decreases)} time(s))",
            detail=f"changeThreshold executed with lower value - governance was weakened.",
            audit_language=(
                f"The threshold was decreased {len(threshold_decreases)} time(s) in transaction history. "
                f"Threshold reductions weaken the multisig's security posture. Unexplained threshold "
                f"reductions are a red flag for governance attacks."
            ),
            evidence={"count": len(threshold_decreases), "nonces": [t["nonce"] for t in threshold_decreases]},
            score=20,
        ))

    # ── HISTORY-02/03: Owner changes ──────────────────────────────────────
    owner_adds = [t for t in executed if (t.get("dataDecoded") or {}).get("method") in ("addOwner", "addOwnerWithThreshold")]
    owner_changes = [t for t in executed if (t.get("dataDecoded") or {}).get("method") in ("removeOwner", "swapOwner")]

    if owner_adds:
        result.findings.append(Finding(
            severity="medium", code="HISTORY-02",
            title=f"Owner(s) added in history ({len(owner_adds)} tx(s))",
            detail="Owner additions found - verify each was an authorized governance action.",
            audit_language=(
                f"{len(owner_adds)} owner addition(s) were executed. Each addition expands the attack surface. "
                f"Verify these were authorized governance decisions and that new owners' key management is adequate."
            ),
            evidence={"count": len(owner_adds), "nonces": [t["nonce"] for t in owner_adds[:5]]},
            score=10,
        ))

    if owner_changes:
        result.findings.append(Finding(
            severity="medium", code="HISTORY-03",
            title=f"Owner removal/swap in history ({len(owner_changes)} tx(s))",
            detail="Owner removal or swap detected - may indicate compromise or forced key rotation.",
            audit_language=(
                f"{len(owner_changes)} owner removal/swap transaction(s) found in history. "
                f"Verify these were authorized and that no owner was forcibly removed following a compromise."
            ),
            evidence={"count": len(owner_changes), "nonces": [t["nonce"] for t in owner_changes[:5]]},
            score=10,
        ))

    # ── HISTORY-04: Untrusted delegatecall ────────────────────────────────
    untrusted_delegatecalls = [
        t for t in executed
        if t.get("operation") == 1 and t.get("to", "").lower() not in TRUSTED_DELEGATES
    ]
    if untrusted_delegatecalls:
        targets = list({t["to"] for t in untrusted_delegatecalls})[:3]
        result.findings.append(Finding(
            severity="high", code="HISTORY-04",
            title=f"Delegatecall to non-standard contract ({len(untrusted_delegatecalls)} tx(s))",
            detail=f"operation=1 to non-whitelisted contracts: {', '.join(targets)}",
            audit_language=(
                f"{len(untrusted_delegatecalls)} delegatecall(s) to non-standard contract(s) "
                f"({', '.join(targets)}) found in history. Delegatecalls execute code in the Safe's "
                f"storage context and can modify ownership or drain funds. Any target not in the trusted "
                f"whitelist requires review."
            ),
            evidence={"count": len(untrusted_delegatecalls), "targets": targets},
            score=25,
        ))

    # ── HISTORY-05: Gas token attack pattern ──────────────────────────────
    gas_attacks = [
        t for t in executed
        if (t.get("gasToken") or ZERO_ADDR) != ZERO_ADDR
        and (t.get("refundReceiver") or ZERO_ADDR).lower() != ZERO_ADDR
    ]
    if gas_attacks:
        result.findings.append(Finding(
            severity="high", code="HISTORY-05",
            title=f"Gas token attack pattern ({len(gas_attacks)} tx(s))",
            detail="Transactions with custom gasToken + custom refundReceiver - potential gas drainage.",
            audit_language=(
                f"{len(gas_attacks)} transaction(s) with a custom gasToken and refundReceiver found. "
                f"This pattern can drain Safe funds via gas refund manipulation. In legitimate usage, "
                f"both fields should be the zero address."
            ),
            evidence={"count": len(gas_attacks), "nonces": [t["nonce"] for t in gas_attacks[:5]]},
            score=20,
        ))

    # ── HISTORY-06: Single executor ───────────────────────────────────────
    executed_with_executor = [t for t in executed if t.get("executor")]
    if len(executed_with_executor) >= 5:
        executors = [t["executor"] for t in executed_with_executor]
        unique = set(executors)
        dominant = max(unique, key=executors.count)
        dominant_count = executors.count(dominant)
        if dominant_count / len(executors) > 0.9:
            result.findings.append(Finding(
                severity="low", code="HISTORY-06",
                title="Single executor pattern",
                detail=f"{dominant_count}/{len(executors)} txs executed by same address ({dominant[:10]}...).",
                audit_language=(
                    f"All {dominant_count} recent executed transactions were submitted by a single executor "
                    f"({dominant}). While threshold requires multiple signatures, one party controls execution "
                    f"timing and can delay or front-run transactions."
                ),
                evidence={"executor": dominant, "count": dominant_count, "total": len(executors)},
                score=5,
            ))

    # ── HISTORY-07: Execution failures ────────────────────────────────────
    failures = [t for t in txs if t.get("isExecuted") and t.get("isSuccessful") is False]
    if len(failures) >= 2:
        result.findings.append(Finding(
            severity="medium", code="HISTORY-07",
            title=f"Execution failures in history ({len(failures)})",
            detail="Repeated failed executions may indicate misconfiguration or attempted exploits.",
            audit_language=(
                f"{len(failures)} execution failure(s) found in history. Failed executions still consume "
                f"nonce and gas. Repeated failures may indicate misconfigured transactions or attempted manipulation."
            ),
            evidence={"count": len(failures), "nonces": [t["nonce"] for t in failures[:5]]},
            score=10,
        ))

    # ── HISTORY-08: Pending governance tx ─────────────────────────────────
    pending_governance = [
        t for t in pending
        if (t.get("dataDecoded") or {}).get("method") in GOVERNANCE_METHODS
    ]
    for tx in pending_governance:
        method = tx["dataDecoded"]["method"]
        confs = len(tx.get("confirmations") or [])
        required = tx.get("confirmationsRequired", threshold)
        is_critical = method in ("addOwnerWithThreshold", "addOwner", "removeOwner",
                                  "swapOwner", "changeThreshold", "enableModule", "changeMasterCopy")
        result.findings.append(Finding(
            severity="critical" if is_critical else "high",
            code="HISTORY-08",
            title=f"Pending governance tx: {method} (nonce {tx['nonce']})",
            detail=f"{confs}/{required} confirmations - not yet executed.",
            audit_language=(
                f"A pending {method} transaction (nonce {tx['nonce']}) has {confs}/{required} confirmations "
                f"and has not yet executed. This represents an active governance change. Review urgently."
            ),
            evidence={"method": method, "nonce": tx["nonce"], "confirmations": confs, "required": required},
            score=35 if is_critical else 20,
        ))

    # Compound escalation: threshold=1 + unknown module → bump score
    has_threshold_1 = any(f.code == "CONFIG-01" for f in result.findings)
    has_unknown_module = any(f.code == "CONFIG-04" for f in result.findings)
    if has_threshold_1 and has_unknown_module:
        result.risk_score += 10  # escalation bonus

    result.risk_score = min(sum(f.score for f in result.findings) + result.risk_score, 100)
    return result

# ──────────────────────────────────────────────
# Discovery
# ──────────────────────────────────────────────

async def get_treasury_protocols(session: aiohttp.ClientSession) -> list[tuple[str, str]]:
    """Returns list of (protocol_name, treasury_slug)."""
    async with session.get(DEFILLAMA_PROTOCOLS_URL, timeout=aiohttp.ClientTimeout(total=120)) as r:
        data = await r.json(content_type=None)
    return [(p["name"], p["treasury"]) for p in data if p.get("treasury")]


async def extract_addresses_from_adapter(session: aiohttp.ClientSession, slug: str) -> list[str]:
    """Fetches DeFiLlama treasury adapter JS and extracts all Ethereum addresses."""
    url = f"{DEFILLAMA_ADAPTER_BASE}{slug}"
    if not slug.endswith(".js"):
        url += ".js" if "." not in slug else ""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status != 200:
                return []
            text = await r.text()
    except Exception:
        return []

    addresses = list(set(ETH_ADDR_RE.findall(text)))
    checksummed = []
    for a in addresses:
        if a.lower() != ZERO_ADDR and len(a) == 42:
            try:
                checksummed.append(checksum_address(a))
            except Exception:
                pass
    return list(set(checksummed))


async def audit_address(session: aiohttp.ClientSession, address: str, network: str, protocol: str, sem: asyncio.Semaphore) -> SafeResult:
    async with sem:
        safe_info = await fetch_safe_info(session, address, network)
        if safe_info is None:
            return SafeResult(address=address, network=network, protocol=protocol, error="Not a Safe or unreachable")
        txs = await fetch_transactions(session, address, network, limit=50)
        await asyncio.sleep(0.2)  # polite delay
    return analyze_safe(safe_info, txs, address, network, protocol)

# ──────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────

def render_report(results: list[SafeResult], mode: str, network: str) -> str:
    from datetime import timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Safe Governance Hunt Report",
        f"Generated: {now} | Mode: {mode} | Network: {network}",
        f"Audited: {len(results)} Safe(s) | Findings: {sum(len(r.findings) for r in results if not r.error)}",
        "",
    ]

    valid = [r for r in results if not r.error and r.safe_info]
    errored = [r for r in results if r.error]

    buckets = {
        "🔴 CRITICAL / HIGH RISK (score ≥ 56)": [r for r in valid if r.risk_score >= 56],
        "🟠 MEDIUM RISK (score 36–55)": [r for r in valid if 36 <= r.risk_score < 56],
        "🟡 LOW RISK (score 16–35)": [r for r in valid if 16 <= r.risk_score < 36],
        "✅ CLEAN (score < 16)": [r for r in valid if r.risk_score < 16],
    }

    for bucket_label, bucket_results in buckets.items():
        if not bucket_results:
            continue
        lines.append(f"## {bucket_label}")
        lines.append("")
        for r in sorted(bucket_results, key=lambda x: x.risk_score, reverse=True):
            info = r.safe_info or {}
            owners = info.get("owners", [])
            modules = info.get("modules") or []
            lines += [
                f"### [{r.protocol}] `{r.address}` ({r.network})",
                f"Risk Score: **{r.risk_score}/100** {r.risk_label}",
                f"Owners: {len(owners)} | Threshold: {info.get('threshold', '?')}/{len(owners)} | "
                f"Version: {info.get('version', '?')} | Guard: {'Set' if (info.get('guard') or ZERO_ADDR) != ZERO_ADDR else 'None'} | "
                f"Modules: {len(modules)} {'(unknown)' if modules else ''}",
                "",
            ]
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            for finding in sorted(r.findings, key=lambda f: severity_order.get(f.severity, 5)):
                emoji = {"critical": "🚨", "high": "🔴", "medium": "🟠", "low": "🟡", "info": "ℹ️"}.get(finding.severity, "•")
                lines += [
                    f"**{emoji} [{finding.severity.upper()}] {finding.code}: {finding.title}**",
                    f"_{finding.detail}_",
                    f"> {finding.audit_language}",
                    f"Evidence: `{json.dumps(finding.evidence)}`",
                    "",
                ]
            lines.append("---")
            lines.append("")

    if errored:
        lines += ["## ⚠️ Skipped (not a Safe or unreachable)", ""]
        for r in errored:
            lines.append(f"- `{r.address}` ({r.network}, {r.protocol}): {r.error}")
        lines.append("")

    return "\n".join(lines)

# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Safe Governance Hunt")
    parser.add_argument("--address", help="Single Safe address to audit")
    parser.add_argument("--protocol", help="Protocol name to look up via DeFiLlama")
    parser.add_argument("--sweep", action="store_true", help="Sweep all DeFiLlama treasury protocols")
    parser.add_argument("--network", default="ethereum", help="Network (default: ethereum)")
    parser.add_argument("--top", type=int, help="Show only top N results by risk score")
    parser.add_argument("--output", help="Write report to file (default: stdout)")
    parser.add_argument("--min-score", type=int, default=0, help="Only show results with risk_score >= N")
    args = parser.parse_args()

    sem = asyncio.Semaphore(8)
    results: list[SafeResult] = []

    connector = aiohttp.TCPConnector(limit=20, ssl=ssl.create_default_context(cafile=certifi.where()))
    async with aiohttp.ClientSession(connector=connector) as session:

        # ── Mode 1: Single address ─────────────────────────────────────────
        if args.address:
            print(f"[*] Auditing {args.address} on {args.network}...", file=sys.stderr)
            r = await audit_address(session, args.address, args.network, "manual", sem)
            results.append(r)
            mode = "targeted"

        # ── Mode 2: Protocol lookup ────────────────────────────────────────
        elif args.protocol:
            print(f"[*] Looking up '{args.protocol}' in DeFiLlama...", file=sys.stderr)
            protocols = await get_treasury_protocols(session)
            query = args.protocol.lower()
            matches = [(name, slug) for name, slug in protocols if query in name.lower()]

            if not matches:
                print(f"[!] No DeFiLlama treasury found for '{args.protocol}'", file=sys.stderr)
                sys.exit(1)
            if len(matches) > 1:
                print(f"[?] Multiple matches - using first: {matches[0][0]}", file=sys.stderr)

            name, slug = matches[0]
            print(f"[*] Found: {name} (slug: {slug})", file=sys.stderr)
            addresses = await extract_addresses_from_adapter(session, slug)
            print(f"[*] Extracted {len(addresses)} address(es) - checking Safe API...", file=sys.stderr)

            tasks = [audit_address(session, addr, args.network, name, sem) for addr in addresses]
            results = await asyncio.gather(*tasks)
            mode = "protocol"

        # ── Mode 3: Sweep ──────────────────────────────────────────────────
        elif args.sweep:
            print("[*] Fetching DeFiLlama protocol list...", file=sys.stderr)
            protocols = await get_treasury_protocols(session)
            print(f"[*] Found {len(protocols)} protocols with treasury adapters", file=sys.stderr)

            all_targets: list[tuple[str, str]] = []  # (address, protocol_name)
            for i, (name, slug) in enumerate(protocols):
                addrs = await extract_addresses_from_adapter(session, slug)
                for addr in addrs:
                    all_targets.append((addr, name))
                if i % 20 == 0:
                    print(f"[*] Parsed {i+1}/{len(protocols)} adapters, {len(all_targets)} addresses so far...", file=sys.stderr)
                await asyncio.sleep(0.05)

            print(f"[*] Auditing {len(all_targets)} addresses across {len(protocols)} protocols...", file=sys.stderr)
            tasks = [audit_address(session, addr, args.network, proto, sem) for addr, proto in all_targets]
            completed = 0
            total = len(tasks)
            results_list = []
            for coro in asyncio.as_completed(tasks):
                r = await coro
                results_list.append(r)
                completed += 1
                if completed % 50 == 0 or completed == total:
                    found = sum(1 for x in results_list if not x.error and x.risk_score >= (args.min_score or 0))
                    print(f"[*] Progress: {completed}/{total} | findings ≥{args.min_score or 0}: {found}", file=sys.stderr)
            results = results_list
            mode = "sweep"

        else:
            parser.print_help()
            sys.exit(0)

    # Filter and sort
    valid_results = [r for r in results if not r.error]
    valid_results.sort(key=lambda r: r.risk_score, reverse=True)

    if args.min_score:
        valid_results = [r for r in valid_results if r.risk_score >= args.min_score]
    if args.top:
        valid_results = valid_results[:args.top]

    errored = [r for r in results if r.error]
    final_results = valid_results + errored

    report = render_report(final_results, mode, args.network)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"[+] Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    asyncio.run(main())
