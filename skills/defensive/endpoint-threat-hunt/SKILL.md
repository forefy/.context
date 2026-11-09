---
name: endpoint-threat-hunt
description: Hunt a live macOS, Linux, or Windows endpoint for malware across process, network, and persistence. Use to scan for threats or check for compromise.
compatibility: macOS/Linux/Windows; full coverage needs sudo/admin
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
| `references/known-attacks-macos.md` | OS = macOS - cross-check named campaigns |
| `references/known-attacks-linux.md` | OS = Linux - cross-check named campaigns |
| `references/known-attacks-windows.md` | OS = Windows - cross-check named campaigns |
| `references/coverage-constraints.md` | Naming blind spots for the SKIP row |
| `scripts/t2_batch.sh` | T2 interactive run - one-prompt batch of every elevated macOS check |

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

**If T1 detected → ask before proceeding (interactive sessions only):**
> Non-interactive/cron runs: do NOT ask - proceed T1-only and mark T2 items SKIP.
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

The ENTIRE report is one verdict line + one table. Nothing else - no prose sections, no bullet lists, no headers beyond the verdict line. The 8-phase structure still drives the scan - only the report layout changes.

**Status symbols (table cells):**
- `CLEAN` - ran clean, no IOCs (use for phases; FAIL wording below if malicious)
- `ACT` - FAIL or SUSPICIOUS, needs operator action
- `FIXED` - previously flagged item, now resolved
- `BENIGN` - changed but attributed to known-good cause
- `SKIP` - not checked this run (reason in detail cell)
- **Never SKIP just because a command needs sudo** - SKIP is for absent binaries or KEXT/SIP/agent-only checks; sudo-gated items are SKIP with "sudo" as the reason.

**Format:**
```
MAC HUNT <date> · <T1|T2> <interactive|unattended> · <CLEAN|NEEDS REVIEW> · X FAIL | X SUSP | X SKIP | X PASS

| status | item | detail | action |
|--------|------|--------|--------|
| ACT | <finding> | <what+why, one clause> | <concrete one-liner command or step> |
| FIXED | <prev item> | <how it resolved> | - |
| BENIGN | <change> | <attribution> | - |
| CLEAN | <phases that ran clean> | <what was checked in them> | - |
| SKIP | <N> checks | <comma list with short reason each>. Blind spots: <what native checks cannot see here> | - |
```

**Rules:**
- Verdict line first, table second; zero text outside them (a `FIXED`/`BENIGN`/`NEW` delta row replaces any "since last run" section).
- One row per finding/phase/check-class; a finding row beats the CLEAN row for that phase (drop the phase from the P1-P8 row text if it has its own row).
- Every ACT row's action cell must be runnable without rereading the report.
- Table stays <=8 rows ideally; compress multiple benign deltas into one `BENIGN` row (detail = comma list).
- The count line `X FAIL | X SUSPICIOUS | X SKIP | X PASS` stays exact.
- The SKIP row always ends with `Blind spots:` naming what native checks cannot see on this host, at least kernel-mode rootkits and memory-only malware, plus anything elevated that could not be verified at this tier.
- The SKIP row names every check that did not run, each with its reason (for example `T1 only - rerun elevated`). Compressing rows never drops a skipped check.
- Package-verify drift on config files (`dpkg -V` or `rpm -Va` lines marked `c`) is normal and stays out of the table. Only checksum changes on binaries count.
- CLEAN lists only phases that actually ran clean. A phase with no collected output goes in SKIP. A phase whose output cannot be trusted (hidden PID, `/etc/ld.so.preload` present, a replaced system binary) gets its own `ACT` row reading `output unreliable`.

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
