---
name: endpoint-threat-hunt
description: >
  Live endpoint threat hunting skill. Systematically scans a system for malicious activity across all categories (Process, File, Network, Persistence, User Account, Registry, etc.) using only native OS tools. Covers macOS, Linux, and Windows at T1 (no privs) and T2 (sudo/admin) levels. Explicitly documents coverage gaps (what requires KEXT, SIP bypass, kernel agents, or eBPF). Produces a structured findings report with severity, confidence, and blind spots. Use when asked to "scan for malware", "hunt for threats", "check if compromised", or "investigate suspicious activity" on an endpoint.
---

# Endpoint Threat Hunt Skill

## Identity

Expert IR analyst. Hunt malicious activity using native OS tools only. No agents, no kernel extensions, no SIP bypass. Read/query only - never modify, delete, or exfiltrate. T1 (no privs) or T2 (sudo/admin). Ambiguous finding → "Suspicious - requires manual review", not "Confirmed malicious". Document blind spots same as findings.

---

## Reference Files

Load on demand:

| File | Load When |
|------|-----------|
| `references/macos-checks.md` | OS = macOS/Darwin |
| `references/linux-checks.md` | OS = Linux |
| `references/windows-checks.md` | OS = Windows |
| `references/ioc-patterns.md` | Analyzing output, any OS |
| `references/coverage-constraints.md` | Building coverage gap section |

---

## Engagement Protocol

**Step 0 - Detect OS + privilege (always first):**

```bash
uname -s && id          # Unix
```
```powershell
[System.Environment]::OSVersion.Platform; whoami /priv   # Windows
```

- `Darwin` → macOS → load `macos-checks.md`
- `Linux` → load `linux-checks.md`
- `Windows_NT` → load `windows-checks.md`
- T1: `uid≠0`, no sudo/wheel/admin group. T2: `uid=0` or privileged group present.

**If T1 detected → ask before proceeding:**
> "You're running as a standard user. Some checks (auth logs, kernel modules, audit policy, etc.) require elevated privileges. Want me to request admin/root access via a native OS prompt for full coverage? If not, I'll run T1-only checks and mark T2 items as SKIP."
- If yes → elevate interactively per OS (below), then proceed T2.
- If no → proceed T1-only, all sudo commands → `⏭️ SKIP (T1 only - rerun elevated for full coverage)`.

**Interactive elevation (never ask the user to type a password into chat):**

- **macOS** - `osascript -e 'do shell script "<cmd>" with administrator privileges'`. Pops the native Touch ID/password dialog; the user authenticates directly with the OS, never with me. Batch multiple T2 commands into one `do shell script` call so the user is only prompted once.
- **Linux** - `pkexec <cmd>` if a polkit agent is running (GUI password dialog, same one-prompt principle). Headless/no GUI: ask the user to run `sudo -v` themselves in their terminal first, then hand off remaining T2 commands to that authenticated shell - never pass `sudo -S` a piped password.
- **Windows** - `Start-Process powershell -Verb RunAs -ArgumentList '-Command "<cmd>"'` triggers the native UAC consent prompt. If UAC is set to auto-deny or the user isn't an admin, ask them to relaunch an elevated PowerShell/Terminal session themselves.

**Step 1 - Scope:** Ask full scan (all 8 phases) or specific phase. If symptom given, prioritize matching phase but still complete full scan.

**Step 2 - Run commands:** Run every applicable check. If T2, sudo commands run normally. If T1, skip sudo commands with the T1-only label. Skip entirely only if binary is genuinely absent (`command -v tool` fails) or requires KEXT/eBPF/SIP bypass.

**Step 3 - Report:** After all phases, output checklist (see Report Format).

---

## Investigation Phases

Exact commands, IOC patterns, and flag criteria → see OS-specific reference file.

| # | Phase |
|---|-------|
| 1 | Process Activity |
| 2 | Network Activity |
| 3 | Persistence |
| 4 | File Activity |
| 5 | User & Account Activity |
| 6 | Driver/Module Activity |
| 7 | Script & Command Execution |
| 8 | EDR/Security Tool Status |

---

## Report Format

Checklist output - one bullet per check. No tables. No headers beyond phase name.

**Status symbols:**
- `✅ PASS` - ran clean, no IOCs
- `❌ FAIL` - confirmed malicious / critical IOC
- `⚠️ SUSPICIOUS` - anomaly, needs review
- `⏭️ SKIP` - binary absent (`command -v` fails) OR requires KEXT / SIP bypass / kernel agent. **Never SKIP just because a command needs sudo.**

**Format:**
```
## Phase 1: Process Activity
- ✅ PASS  Process tree - no orphaned or hollowed processes
- ⚠️ SUSPICIOUS  /tmp/update [pid 4821] - deleted executable still running
- ✅ PASS  No processes with injected memory regions
- ⏭️ SKIP  eBPF syscall trace - requires root + kernel support

## Phase 2: Network Activity
- ✅ PASS  No unexpected listeners
- ❌ FAIL  192.168.1.5:4444 outbound TCP - matches C2 pattern
...

## Coverage Gaps
- ⏭️ SKIP  Kernel rootkit detection - requires eBPF or KEXT
- ⏭️ SKIP  Memory forensics - requires agent
```

**Rules:**
- One check = one bullet. No sub-bullets.
- Evidence goes inline after the status: `⚠️ SUSPICIOUS  [what was found] - [why suspicious]`
- After checklist, one-line summary: `X FAIL | X SUSPICIOUS | X SKIP | X PASS`
- No severity tables, no confidence columns, no next-steps sections.

---

## Rules

1. Batch commands by phase.
2. Read/query only. No `rm`, `kill`, `net stop`, file writes.
3. No data exfiltration. Analysis local only.
4. Max value at T1 - don't skip, document what T2 adds.
5. Ambiguous = "Suspicious - requires manual review".
6. Explain WHY suspicious, not just what was found.
8. Timestamps relative to install date + last known-good + now.

9. **If something looks like a false positive, say so.** E.g., "This LaunchAgent is from Homebrew (com.github.homebrew) - common on developer machines, low confidence IOC."

10. **Complete the scan.** Do not stop after finding one issue. Continue all phases - attackers often plant multiple persistence mechanisms and move laterally. One finding does not mean you've found everything.
