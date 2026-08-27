---
name: dylib-hijack-scan
description: Scan macOS for hijackable dynamic libraries, separating exploitable privesc hijacks from harmless ones. Use to check if an app is hijackable.
---

# Dylib Hijack Scan

## Identity

macOS dylib-hijacking auditor. Parse Mach-O load commands from scratch, decide exploitability by library validation, and separate user-context hijacks from real privilege escalation by reading directory permissions. Read/query only - never plant, modify, or delete. Report susceptibility and coverage honestly; state blind spots as loudly as findings. Ambiguous slot is not a finding.

---

## When to use

Targeted, explainable dylib-hijack analysis: is this app hijackable and why, does any hijack cross a privilege boundary, sweep a whole machine and reason about each hit. For a raw full-disk sweep where only speed matters, Objective-See's compiled DylibHijackScanner is faster; the value here is that every finding carries the load command, the writable slot, the writer principal, and the mitigation.

## The two vulnerability classes

1. Weak-dylib hijack (`LC_LOAD_WEAK_DYLIB`): the binary weak-links a dylib that does not exist on disk. Because the link is weak the app still runs, so anyone who can write that path plants a dylib and gets code execution inside the process.
2. Rpath-order hijack (`@rpath/...` import with multiple `LC_RPATH`): dyld searches the rpath directories in declared order and loads the first match. An earlier, attacker-writable rpath that lacks the file lets a planted copy win over the real one found later.

## The mitigation that decides exploitability

Library validation. Under the hardened runtime, absent the `com.apple.security.cs.disable-library-validation` entitlement and with a real Team ID, dyld refuses to load a dylib not signed by the host's team or Apple. A plantable slot on such a host is not practically exploitable. Determined from `codesign`, invoked only on hosts that have a slot, so there is no per-file cost.

## Elevation: ordinary hijack vs privilege escalation

The axis that matters is whether a principal who can write the slot is less privileged than the one who loads it.

- Who can write is read from the slot directory's permission bits and owner/group, and from any ACL - never from the euid running the scan, so the verdict is identical as standard user, admin, or root. Classes: `world` (any user), `anylocal` (group staff, gid 20, meaning any local user), `admin` (gid 80), `user` (one owner), and `root`/`none` (only root can plant, so not attacker-exploitable and never reported).
- Who loads is the loader principal: root iff a LaunchDaemon with no or `root` `UserName`, a setuid/setgid-root binary, or a `/Library/PrivilegedHelperTools` helper. A normal app runs as whoever launches it.
- Severity: `world`/`anylocal` writer plus root loader plus library validation off is CRITICAL (any local user to root). `admin`/`user` writer plus root loader is HIGH elevation. Writer equal to the loader's own user is HIGH but no elevation (user-context code execution, most findings). Library validation on is LOW.

ACLs are honored. A `chmod +a` grant can widen access beyond the POSIX bits. `slot_writer()` checks for an extended ACL in-process via `acl_get_file` (one C call, no fork; dirs without an ACL are the vast majority) and parses `ls -lde` only for the rare dirs that carry one. An allow of a write right to a broader principal upgrades the writer class. Deny entries are not applied as a downgrade - for a scanner, over-reporting a writable slot is safer than missing one.

## Running it

```bash
python3 scripts/scan.py / --json /tmp/scan.json
python3 scripts/build_report.py /tmp/scan.json --html /tmp/report.html
```

`scan.py --json` always emits the full inventory: every analyzable Mach-O host (executable, dylib, bundle) with all its imports classified. It reads the magic bytes of every regular file, skipping known text and asset extensions so a full-disk walk stays tractable, and parses each Mach-O in process. Scan as a normal or admin user, not `sudo`, or the writability test no longer reflects a real attacker.

Scope options:

```bash
python3 scripts/scan.py "/Applications/Target.app"            # one app, fast
python3 scripts/build_report.py /tmp/scan.json --match target # focus report by substring
```

## The report

`build_report.py` renders the inventory into a per-app page. Flagged binaries get a full verdict table with a who-can-plant column; clean binaries are grouped at each app's foot as a compact dylib list, keeping a whole-system page inside the artifact size limit. It is theme-aware and self-contained, orders apps and rows most-severe first, starts collapsed, and offers a live text filter and an Elevation (privesc) only toggle. `--json` also writes the structured report.

## Reporting

Lead with a one-line verdict (elevation count first, then user-context hijackable, then protected). Group multiple binaries in one bundle rather than listing near-identical lines. State the coverage numbers and named blind spots the tool prints: files and directories unreadable without elevation, and the dyld shared cache, whose system dylibs are not on-disk files and are Apple-signed with library validation. Never claim literal full coverage.

## Verifying a finding by hand

```bash
otool -l "<host>" | grep -A2 -E 'LC_RPATH|LC_LOAD_WEAK_DYLIB|LC_LOAD_DYLIB'
codesign -d --entitlements - --xml "<host>" | grep disable-library-validation
codesign --display --verbose=2 "<host>"
ls -lde "<slot directory>"
```

See `references/methodology.md` for the full detection algorithm, the writer and loader classification, the ACL handling, and the blind spots.
