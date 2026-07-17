# Coverage Constraints Reference

> Defines what skill CANNOT detect + why. Overstating coverage → false confidence. Report gaps every hunt.

---

## Coverage Score Summary

| Category | macOS T1 | macOS T2 | Linux T1 | Linux T2 | Windows T1 | Windows T2 |
|---|---|---|---|---|---|---|
| Process Activity | 60% | 75% | 65% | 80% | 65% | 80% |
| Network Activity | 85% | 90% | 85% | 95% | 85% | 90% |
| Persistence | 80% | 90% | 80% | 90% | 75% | 90% |
| File Activity | 65% | 75% | 70% | 85% | 70% | 80% |
| User/Account | 75% | 90% | 80% | 90% | 75% | 90% |
| Driver/Module | 40% | 55% | 30% | 70% | 30% | 70% |
| Script Activity | 70% | 80% | 75% | 85% | 75% | 85% |
| Process Injection | 5% | 10% | 5% | 15% | 5% | 15% |
| Memory-only Threats | 0% | 0% | 0% | 0% | 0% | 0% |
| EDR Status | 90% | 95% | 90% | 95% | 90% | 95% |

**Score meaning:**
- % = fraction of real-world techniques detectable with native OS commands at privilege level.
- 0% ≠ no value - native-command approach blind to that threat class. Needs dedicated tool.
- Even 60% catches real compromise - attackers make mistakes, leave artifacts in high-coverage categories.

---

## macOS Coverage Constraints

### Cannot Detect: Real-Time Process Injection

**Missed:** Dylib injection, `task_for_pid` exploitation, `DYLD_INSERT_LIBRARIES` abuse in running process.

**Why blind:** Needs Apple ESF - kernel framework streaming process events to userspace. ESF requires:
1. System Extension (needs SIP + Apple's System Extension entitlement)
2. `com.apple.developer.endpoint-security.client` entitlement (Apple-granted)
3. FDA for System Extension

None available to ad-hoc terminal session.

**CAN detect (partial):**
- Past `task_for_pid` in historical logs (T2, via `log show`)
- Unusual dylibs in process memory maps (retrospective, not real-time)
- Unusual `DYLD_INSERT_LIBRARIES` env var via `ps auxeww`

**Fix:** Deploy EDR with ESF system extension (CrowdStrike, SentinelOne, Elastic, MDE).

---

### Cannot Detect: Memory-Only Malware

**Missed:** Malware entirely in RAM - shellcode injected into legit process, `NSCreateObjectFileImageFromMemory`, fileless execution. Never writes binary to disk.

**Why blind:** Toolset only queries OS structures (process lists, file paths, network). Memory forensics needs:
1. Memory acquisition tool (`osxpmem`)
2. Analysis framework (Volatility + macOS profile)
3. Root + kernel extension for acquisition

**CAN detect (partial):**
- Network connections FROM injected legit process - activity still shows up
- Anomalous behavior FROM legit process (unusual CPU, unexpected network)
- Disk artifacts if dropper wrote to disk before deleting

**Fix:** Deploy memory forensics. Volatility + `osxpmem` for post-incident.

---

### Cannot Detect (Without FDA): TCC Database Full Contents

**Missed:** Camera, Mic, Screen Capture, Contacts, Calendar, FDA, and other TCC permissions - complete visibility.

**Why blind:** TCC DB at:
- `/Library/Application Support/com.apple.TCC/TCC.db` (system-level, SIP-protected)
- `~/Library/Application Support/com.apple.TCC/TCC.db` (user-level, needs T2 + FDA)

**T1:** No access to either.  
**T2 without FDA:** User-level only.  
**T2 with FDA:** Full access.

**Fix:** Grant Terminal FDA in System Settings > Privacy & Security > Full Disk Access, re-run at T2.

---

### Cannot Detect: XPC Service Abuse

**Missed:** Attacker abuses misconfigured XPC services to escalate privs or execute code in privileged service context - no new process spawned.

**Why blind:** XPC comms = kernel space. Needs ESF or custom kext to monitor.

**CAN detect (partial):**
- Unusual processes receiving XPC connections (via `lsof`)
- Anomalous XPC service behavior (unusual network, file writes)

---

### SIP-Protected Paths (Cannot Read)

Unreadable even with root (T2):
- `/System/Library/*` - system frameworks + daemons
- `/usr/lib/*` - system libraries
- `/usr/bin/`, `/usr/sbin/` - utilities (executable, not writable)
- `/dev/kmem` - fully inaccessible

**Hunting implications:**
- Malware compromising these (needs SIP disabled) → undetectable
- `csrutil status` - if SIP disabled, all paths suspect
- `codesign --verify` for integrity (reads cached sig info)

---

### Cannot Detect: Gatekeeper Bypass via Already-Approved Apps

**Missed:** Attacker smuggles malicious code inside Gatekeeper-approved app downloading payloads at runtime - Gatekeeper won't recheck runtime downloads.

**Why blind:** Gatekeeper runs only at first launch + Safari/Mail/Finder downloads. Runtime downloads bypass check entirely.

**CAN detect:**
- Payloads on disk (file checks)
- Download network connections (network checks)
- Payload execution (process checks)

---

### macOS Logging Gaps

| Log Source | T1 | T2 | Notes |
|------------|----|----|-------|
| Unified Logging (`log show`) | No | Yes | Needs sudo |
| System.log | No | Yes | Protected |
| XProtect/MRT events | No | Yes | Via `log show` |
| TCC events | No | Yes + FDA | |
| Security daemon events | No | Yes | `com.apple.securityd` subsystem |
| SSH auth events | No | Yes | |
| Sudo events | No | Yes | |
| `eslogger` | No | Yes | macOS 13+, needs entitlement |

---

## Linux Coverage Constraints

### Cannot Detect: Kernel-Mode Rootkits

**Missed:** LKM rootkits patching running kernel to hide processes, files, connections, modules. Classic: Diamorphine, Reptile, Azazel.

**Why blind:** Rootkit patches `/proc` handlers - `ps`, `ss`, `ls`, `lsmod` only show what rootkit allows. Detection needs:
1. Compare kernel symbols against clean baseline (`/proc/kallsyms`)
2. Hardware-level memory acquisition (no native tool)
3. `rkhunter` or `chkrootkit` (specialized, not native)
4. Compare syscall tables against expected values
5. Memory dump via Volatility

**CAN detect (partial):**
- `lsmod` empty vs `/proc/modules` has content
- `ss`/`netstat` vs `/proc/net/tcp` mismatch
- Unexpected syscall table mods (T2, via `dmesg`)

**Heuristic:** `ps aux | wc -l` vs `ls /proc | grep -c '^[0-9]'` - count differs = rootkit hiding procs.

---

### Cannot Detect Without CAP_SYS_ADMIN: eBPF by Other Users

**Missed:** eBPF programs from other users using kernel probes - intercept syscalls, network, file access. eBPF rootkit hides connections, steals creds, filters audit events.

**Why blind:** `bpftool prog list` needs `CAP_SYS_ADMIN`.

**T1:** No eBPF enumeration.  
**T2:** Enumerate ALL eBPF with `bpftool`.

---

### Cannot Detect Without ptrace: Process Memory Inspection

**Missed:** Injected shellcode, heap-sprayed payloads, in-memory payloads in other users' processes.

**Why blind:** `/proc/PID/mem` needs root or `CAP_SYS_PTRACE`.

**T1:** Own processes only (`/proc/self/mem`).  
**T2:** Any process's memory.

---

### Cannot Detect: Container Escapes

**Missed:** Process inside container escaped to host via breakout (CVE-2019-5736 runc, dirty COW, etc.).

**Why blind:** Hunt inside container = only container namespace visible. Host FS, proc list, network namespace invisible.

**Proper hunt:** Run from HOST. Check for unexpected processes in host namespaces.

---

### Audit Coverage Gaps Without auditd

**Missed (no auditd):**
- No historical process execution (current state via `ps` only)
- No record of created-then-deleted files
- No record of who ran what commands as which user
- No closed network connection record
- No login failures beyond `/var/log/auth.log` (if exists)
- No syscall audit trail

**Core limit:** Hunt is POINT-IN-TIME. Current state + recent log history + uncleaned artifacts only. Cannot reconstruct timeline without configured logs.

**Fix:** Install + configure `auditd`. Key rules:
```
-a always,exit -F arch=b64 -S execve -k process_exec
-a always,exit -F arch=b64 -S connect -k network_connect
-w /etc/passwd -p wa -k account_changes
-w /etc/shadow -p wa -k account_changes
-w /etc/sudoers -p wa -k sudoers
```

---

### Cannot Detect: Supply Chain / Trojanized Packages

**Missed:** System binary (`/usr/bin/ls`, `/usr/bin/ps`) replaced via compromised package repo or build pipeline - commands lie.

**CAN detect (partial):**
- Package hash comparison: `rpm -V` (RHEL) or `debsums` (Debian)
- `aide`/`tripwire` DB comparison (if pre-installed with baseline)
- Binary modification timestamps vs package install dates

---

## Windows Coverage Constraints

### Cannot Detect Without Admin: Kernel-Mode Rootkits

**Missed:** DKOM rootkits, bootkits, MBR/VBR infection, UEFI implants. Run below OS - manipulate OS structures to hide processes, connections, registry.

**Why blind:** Ring 0 or below. PowerShell only sees what kernel reports. Compromised kernel = compromised PowerShell. Detection needs:
1. Virtualization-based security analysis
2. Kernel debugger
3. Memory forensics with `winpmem` + Volatility
4. Bootkit scanning (specialized offline tools)

---

### Cannot Detect: Process Hollowing

**Missed:** Attacker creates legit process (`svchost.exe`), unmaps memory, maps malicious code. `Get-Process` shows legit path - running malware.

**Why blind:** `Get-Process` + `Win32_Process` show binary PATH, not in-memory code. Post-hollow: path still shows `C:\Windows\System32\svchost.exe`.

**CAN detect (partial):**
- `svchost.exe` with suspicious cmd args (legit has `-k NetworkService` etc.)
- `svchost.exe` not from `C:\Windows\System32\`
- Authenticode mismatch on binary file (file on disk may be legit - only memory hollow)

**Heuristic:** `Get-AuthenticodeSignature` on path - FILE should match. In-memory differs → won't catch without memory scan.

**Fix:** Deploy memory integrity scanning (CrowdStrike, SentinelOne, MDE detect hollowing real-time).

---

### Cannot Detect Without ETW Kernel Providers: DLL Injection

**Missed:** DLL injection into legit processes (CreateRemoteThread, SetWindowsHookEx, AppInit_DLLs, reflective DLL loading).

**Why blind:** Detection needs comparing DLL list against known-good baseline - requires process memory access. PowerShell can't enumerate in-memory modules without kernel access.

**CAN detect (partial):**
- `AppInit_DLLs` registry key (static config - see Windows checks)
- DLL files on disk in suspicious locations pre-injection
- Authenticode check for DLLs in suspicious locations

---

### Logging Gaps Without Audit Policy

**Missed (no audit policy):**
- **4688 (Process Creation):** Not logged without "Audit Process Creation" enabled. No process record.
- **4688 + cmd line:** Needs `ProcessCreationIncludeCmdLine_Enabled = 1`
- **4104 (Script Block Logging):** Needs Group Policy config
- **4656/4663 (Object Access):** Needs "Audit Object Access" + SACL on objects

**Implication:** No audit policy = no PowerShell, no script execution, no file access logging. Current state only.

**Check:** `auditpol /get /category:*` (T2 required)

---

### Cannot Detect Without Admin: Other Users' WMI Subscriptions

**Missed:** WMI subscriptions in non-default namespaces or owned by other users (most malware uses `root\subscription`).

**T1:** Can read `root\subscription` (most malware location).  
**T2:** Enumerate all namespaces.

---

### Cannot Detect: AMSI Bypass

**Missed:** AMSI bypass patches in PowerShell process memory - patches in-memory AMSI table to return "clean". No persistent registry or file change.

**Why blind:** Memory-only patch. No file/registry artifact. Needs live memory scan.

**CAN detect (partial):**
- History showing AMSI bypass: `[Ref].Assembly.GetType('System.Management.Automation.Am' + 'siUtils').GetField('am' + 'siInitFailed','NonPublic,Static').SetValue($null,$true)` (+ variants)
- Script Block Logging showing obfuscated bypass attempts (logged BEFORE bypass succeeds, if SBL enabled)

---

### Cannot Detect: UEFI/Firmware Implants

**Missed:** Malware in UEFI firmware (LoJax, MosaicRegressor, CosmicStrand). Survives OS reinstall, disk replacement, all user-space security.

**Why blind:** UEFI runs below OS. PowerShell has no firmware visibility.

**Fix:** `chipsec` (needs admin) for UEFI integrity. Kaspersky/ESET have UEFI scanning.

---

## Universal Constraints (All OSes)

### Memory-Only Malware

**Coverage: 0% at any privilege level - native tools only**

No native OS command does memory forensics. Detecting memory-only threats needs:
1. **Acquisition:** `osxpmem` (macOS), `LiME` kmod (Linux), `winpmem` (Windows)
2. **Analysis:** Volatility + OS-specific profiles
3. **Look for:** Injected shellcode, process hollowing, syscall table hooks, hidden connections

Dedicated discipline (DFIR memory forensics) - specialized tools + training required.

---

### Historical File Activity

**Coverage: Limited at all levels**

Only see currently existing files. Malware can:
- Drop + execute + delete binary → only visible via lsof/proc if still running
- Modify + restore file → mtime may show, can't recover change
- Create + delete file (no longer running) → invisible

**Partial help:**
- `auditd`/Windows audit policy configured BEFORE incident
- File timestamps reveal activity sequence
- `.bash_history` + logs may reference deleted files

---

### Encrypted C2 Channels

**Coverage: Network detection only**

CAN detect: process with connection + destination IP/domain + timing (beacon intervals = suspicious).

CANNOT:
- Decrypt TLS/HTTPS to inspect C2 commands
- Distinguish legit HTTPS from HTTPS-mimicking C2 by content
- Detect DoH C2 (looks same as legit DoH)

---

### Baseline-Dependent Coverage

**All % assume no pre-existing baseline.**

With clean baseline (file hashes, proc list, connections, scheduled tasks) → coverage improves significantly via diff. Maintaining baselines = key gap in most programs without dedicated EDR.

---

## Tools to Fill Coverage Gaps

| Gap | Tool | Notes |
|-----|------|-------|
| Memory forensics (all OS) | Volatility + OS-specific acquisition | `osxpmem`, `LiME`, `winpmem` |
| Real-time process monitoring (macOS) | ESF-based EDR (CrowdStrike, SentinelOne, MDE, Elastic) | Needs System Extension entitlement |
| Kernel rootkit detection (Linux) | `rkhunter`, `chkrootkit`, `aide` | Compare against known-good DB |
| eBPF monitoring (Linux) | `tetragon` (Cilium), Falco | Open-source kernel-level |
| Process hollowing detection (Windows) | CrowdStrike, SentinelOne, MDE | Memory scanning in EDR |
| UEFI/firmware scanning (Windows) | `chipsec`, ESET, Kaspersky | Specialized firmware analysis |
| File integrity monitoring (all OS) | `aide` (Linux), `tripwire` (all), `osquery` | Needs pre-established baseline |
| Historical activity reconstruction | SIEM + endpoint log forwarding | Needs continuous logging |
