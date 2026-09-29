# macOS Endpoint Threat Hunt - Command Reference

> T1 = no elevated privs | T2 = sudo/admin required

---

## Contents

- [Phase 1: Process Activity](#phase-1-process-activity)
  - [1.1 - Full Process Listing with Paths](#11---full-process-listing-with-paths)
  - [1.2 - Processes with Unlinked (Deleted) Executables](#12---processes-with-unlinked-deleted-executables)
  - [1.3 - Open Files and Network Connections for Suspicious Process](#13---open-files-and-network-connections-for-suspicious-process)
  - [1.4 - Parent Process Relationships](#14---parent-process-relationships)
  - [1.5 - Resource Anomalies (CPU Burn and Process Lifetime)](#15---resource-anomalies-cpu-burn-and-process-lifetime)
  - [1.6 - Injected Libraries and Tool Integrity](#16---injected-libraries-and-tool-integrity)
- [Phase 2: Network Activity](#phase-2-network-activity)
  - [2.1 - All Network Connections with Owning Processes](#21---all-network-connections-with-owning-processes)
  - [2.2 - Listening Ports](#22---listening-ports)
  - [2.3 - DNS Configuration](#23---dns-configuration)
  - [2.4 - Hosts File](#24---hosts-file)
  - [2.5 - Network Connections (Summarized by Process)](#25---network-connections-summarized-by-process)
- [Phase 3: Persistence Mechanisms](#phase-3-persistence-mechanisms)
  - [3.1 - LaunchAgents and LaunchDaemons (Primary macOS Persistence)](#31---launchagents-and-launchdaemons-primary-macos-persistence)
  - [3.2 - Crontab](#32---crontab)
  - [3.3 - Login Items (macOS 13+ Background Task Management)](#33---login-items-macos-13-background-task-management)
  - [3.4 - Configuration Profiles (MDM/Malicious Profiles)](#34---configuration-profiles-mdmmalicious-profiles)
- [Phase 4: File Activity](#phase-4-file-activity)
  - [4.1 - Files in Temp Directories](#41---files-in-temp-directories)
  - [4.2 - Scripts in Library Directories](#42---scripts-in-library-directories)
  - [4.3 - Recently Installed Applications](#43---recently-installed-applications)
  - [4.4 - Code Signing Verification for Suspicious Files](#44---code-signing-verification-for-suspicious-files)
- [Phase 5: User & Account Activity](#phase-5-user--account-activity)
  - [5.1 - Local User Accounts](#51---local-user-accounts)
  - [5.2 - Login History](#52---login-history)
  - [5.3 - SSH Configuration and Authorized Keys](#53---ssh-configuration-and-authorized-keys)
  - [5.4 - T2: Authentication Logs](#54---t2-authentication-logs)
- [Phase 6: Driver/Module Activity](#phase-6-drivermodule-activity)
  - [6.1 - System Extensions (macOS 10.15+)](#61---system-extensions-macos-1015)
  - [6.2 - Kernel Extensions (Legacy, Still Active)](#62---kernel-extensions-legacy-still-active)
- [Phase 7: Script & Command Execution](#phase-7-script--command-execution)
  - [7.1 - Shell History](#71---shell-history)
  - [7.2 - Application Script Artifacts](#72---application-script-artifacts)
  - [7.3 - T2: XProtect and MRT Logs](#73---t2-xprotect-and-mrt-logs)
- [Phase 8: EDR/Security Tool Status](#phase-8-edrsecurity-tool-status)
  - [8.1 - Detect Running Security Agents](#81---detect-running-security-agents)
  - [8.2 - macOS Built-in Security Status](#82---macos-built-in-security-status)
  - [8.3 - T2: TCC Privacy Database](#83---t2-tcc-privacy-database)
- [Quick Reference: macOS IOC Severity Ratings](#quick-reference-macos-ioc-severity-ratings)

---

## Phase 1: Process Activity


---

### 1.1 - Full Process Listing with Paths
**Tier:** T1  

```bash
ps auxww
```

**Flag:**
- Root processes that shouldn't be (`bash`, `python`, `nc`)
- `COMMAND` paths in `/tmp`, `/var/folders`, `~/Library/Application Support`, or no dir (running from cwd)
- Long cmdlines with base64 arguments
- Daemon names with subtle misspellings (`launchdaemon` vs `launchd`, etc.)
- Processes with `(deleted)` in path
- Args containing IPs, ports, or encoded strings

**False+:**
- Electron apps (`Slack`, `VSCode`, `Discord`) - many helpers from `.app/Contents/Frameworks/` - legit
- Homebrew: `/usr/local/bin` or `/opt/homebrew/bin` - legit
- JetBrains IDEs - many JVM processes - legit

---

### 1.2 - Processes with Unlinked (Deleted) Executables
**Tier:** T1  

```bash
lsof +L1 2>/dev/null
```

**Flag:**
- Any entry where `NLINK` is `0` - binary deleted from disk while still running
- Classic technique: malware drops, executes, deletes to hinder recovery
- `NAME` column shows original path + `(deleted)` or link count

**False+:**
- Rare on macOS - almost always significant
- Some updaters briefly during self-update
- Ephemeral sandbox processes may show briefly

---

### 1.3 - Open Files and Network Connections for Suspicious Process
**Tier:** T1  

```bash
lsof -p <PID> 2>/dev/null
```

Replace `<PID>` with the PID of a suspicious process from the `ps` output.

**Flag:**
- `inet` entries: outbound connections from process with no business having network access
- `REG` entries: files read/written from unusual locations
- `PIPE` entries: named pipe connections (IPC - possible process injection)
- `mem` entries showing shared libs from unusual paths

---

### 1.4 - Parent Process Relationships
**Tier:** T1  

```bash
ps -eo pid,ppid,user,comm,args | head -80
```

**Flag:**
- Unusual process with `launchd` as parent - may have registered as LaunchAgent/Daemon
- `bash`/`zsh` spawning `nc`, `python -c`, `perl -e`
- Web browser spawning shells (exploitation indicator)
- Office apps spawning scripting interpreters
- `osascript` spawning shell commands

**Cross-ref:** For suspicious parent-child pairs, check for LaunchAgent/Daemon plist explaining relationship (Phase 3).

---

### 1.5 - Resource Anomalies (CPU Burn and Process Lifetime)
**Tier:** T1  

```bash
# Lifetime-average CPU. ELAPSED format: [[dd-]hh:]mm:ss
ps -eo pid,ppid,%cpu,%mem,etime,user,comm | sort -k3 -nr | head -30

# Same data filtered to the miner profile: 80%+ average CPU sustained over 3h
ps -eo pid,ppid,pcpu,etime,user,comm | awk 'NR==1{print;next} {e=$4;d=0; if(e~/-/){split(e,a,"-");d=a[1];e=a[2]} n=split(e,t,":"); s=(n==3)?t[1]*3600+t[2]*60+t[3]:t[1]*60+t[2]; s+=d*86400; if($3>=80 && s>=10800) print}'

# Instantaneous sample - ps %cpu is a lifetime average and hides throttled miners
top -l 2 -n 15 -o cpu -stats pid,command,cpu,time | tail -20
```

**Note:** `%cpu` is percent of one core, so multithreaded processes legitimately exceed 100.

**Flag:**
- `%cpu` >= 80 with `etime` over 3h on a process that maps to no workload you can name - cryptominer profile, the most common macOS resource abuse
- `%cpu` >= 25 with `etime` in days (`dd-hh:mm:ss`) on a binary nobody launched - throttled long-haul miner or a malware retry loop
- High CPU in `top` but low `%cpu` in `ps` - miner that idles while the user is active and spins up when the machine is unattended. The divergence between the two readings IS the indicator
- Sustained CPU inside `bash`, `zsh`, `python`, `osascript` or `curl` - these are not compute workloads, check args in 1.1
- Process wearing an Apple daemon name (`mdworker_shared`, `cloudd`, `nsurlsessiond`) burning CPU from a path outside `/usr/libexec`, `/System` or `/usr/sbin` - masquerade, cross-ref 1.1
- Any of the above from `/tmp`, `/var/folders`, `~/Library/Application Support`, or with a deleted binary - cross-ref 1.1 and 1.2, escalate to Critical

**False+:**
- `kernel_task` - high CPU IS its job, it soaks cycles to hold the CPU temperature down
- `mds`, `mds_stores`, `mdworker_shared` - Spotlight, legitimately hours of high CPU after a large write or an OS update
- `backupd`, `photoanalysisd`, `mediaanalysisd`, `photolibraryd` - Time Machine and Photos ML, long high-CPU runs by design
- `WindowServer`, browsers and their `Helper (Renderer)` children, Electron apps, `Xcode`, `clang`, `swift-frontend`, `node`, `ffmpeg`, `com.docker.hyperkit`, `qemu` - legit heavy compute
- Long `etime` alone means nothing for `launchd`, `loginwindow`, `UserEventAgent` and per-session agents - they live as long as the boot or login session. Lifetime only matters paired with CPU burn

**Cross-ref:** A miner needs a pool. Check Phase 2 for `stratum`, pool ports (3333, 4444, 5555, 7777, 8888, 14444, 45700) or pool domains on the same PID - that pairing turns this from Suspicious into Confirmed. If 1.5 comes back clean on a host you have other reasons to suspect, run 1.6 before believing it.

---

### 1.6 - Injected Libraries and Tool Integrity
**Tier:** T1 (own processes) / T2 (all processes)  

**Run this before trusting 1.1 through 1.5.** SIP is what makes the Phase 1 tooling trustworthy: with it on, `/bin/ps` cannot be replaced and `DYLD_INSERT_LIBRARIES` is stripped for platform binaries. With it off, every reading in this phase is advisory.

```bash
# SIP first - it decides whether anything below can be trusted
csrutil status

# Per-process injected libraries (T2 for other users' environments)
ps auxeww 2>/dev/null | grep -i 'DYLD_INSERT_LIBRARIES' | grep -v grep

# Global injection - applies to everything launchd spawns from boot
launchctl getenv DYLD_INSERT_LIBRARIES

# Integrity of the binaries Phase 1 reads from
codesign -vv --strict /bin/ps /usr/bin/top /usr/sbin/lsof 2>&1
```

**Flag:**
- `csrutil status` anything but `enabled` - `/bin/ps` becomes replaceable and platform binaries honor `DYLD_INSERT_LIBRARIES`. Treat all of Phase 1 as advisory and cross-ref Phase 8
- `DYLD_INSERT_LIBRARIES` in any process environment that is not a debugging or profiling session you can account for
- `launchctl getenv DYLD_INSERT_LIBRARIES` returning a value - everything launchd starts is injected from boot onward
- `codesign` reporting anything other than a valid signature on `/bin/ps`, `/usr/bin/top` or `/usr/sbin/lsof` - the tool has been replaced, and nothing in Phase 1 can be believed

**False+:**
- SIP is legitimately off on kernel-development and some CI machines - confirm intent with the owner before reading it as compromise
- `DYLD_INSERT_LIBRARIES` shows up in real profiling and instrumentation sessions and in some crash reporters
- `ps auxeww` reveals other users' environments only at T2, so a T1 run can miss an injected daemon entirely

**Cross-ref:** Dylib injection into an already-running process is not visible here at all - see `coverage-constraints.md`.

---

## Phase 2: Network Activity


---

### 2.1 - All Network Connections with Owning Processes
**Tier:** T1  

```bash
lsof -i -n -P 2>/dev/null
```

**Flag:**
- `LISTEN` on non-standard ports (not 80/443/22/3306/5432/known app ports) - investigate
- `ESTABLISHED` from system utilities, `bash`, `python` - shouldn't have network access
- RFC1918 connections on non-standard ports - lateral movement indicator
- High ports (>10000) to unfamiliar IPs - C2 beacon pattern
- Process with multiple simultaneous connections to different IPs

**False+:**
- iCloud, Photos, Music, App Store - many Apple CDN connections (17.x.x.x)
- Dropbox, Google Drive, OneDrive - persistent sync
- Browser processes - many legit connections

---

### 2.2 - Listening Ports
**Tier:** T1  

```bash
netstat -an | grep LISTEN
```

**Flag:**
- Listening on `0.0.0.0` or `*` unexpectedly - accessible from network
- Unexpected services on localhost (127.0.0.1) - possible C2 proxy or staging
- Persistent high-numbered ephemeral ports

---

### 2.3 - DNS Configuration
**Tier:** T1  

```bash
scutil --dns
```

**Flag:**
- `nameserver[0]` not router IP, ISP DNS, or well-known public DNS (8.8.8.8, 1.1.1.1, 9.9.9.9)
- `127.0.0.1` as nameserver with unexpected local DNS service - DNS hijacking
- Multiple conflicting DNS configs across interfaces
- `domain` set to unexpected domain - VPN or malicious config profile

---

### 2.4 - Hosts File
**Tier:** T1  

```bash
cat /etc/hosts
```

**Flag:**
- Redirects of major domains: `google.com`, `apple.com`, `microsoft.com`, `github.com`, `ocsp.apple.com` pointing to non-legit IPs
- Security tool update domains redirected: `update.crowdstrike.com`, `sentinelone.com` - tool disruption
- `127.0.0.1` for ad-blocking = common + benign on dev machines
- New entries recently (mtime: `ls -la /etc/hosts`)

---

### 2.5 - Network Connections (Summarized by Process)
**Tier:** T1  

```bash
lsof -i -n -P 2>/dev/null | awk '{print $1}' | sort | uniq -c | sort -rn | head -20
```

**Flag:** Processes with unusually high network connection counts.

---

## Phase 3: Persistence Mechanisms


---

### 3.1 - LaunchAgents and LaunchDaemons (Primary macOS Persistence)
**Tier:** T1 (read), T2 for system-level  

```bash
# List all currently loaded launchd items NOT from Apple
launchctl list | grep -v com.apple

# User-level LaunchAgents (run as current user on login)
ls -la ~/Library/LaunchAgents/ 2>/dev/null

# System-level LaunchAgents (run as current user for ALL users on login)
ls -la /Library/LaunchAgents/ 2>/dev/null

# System-level LaunchDaemons (run as root at boot, regardless of login)
ls -la /Library/LaunchDaemons/ 2>/dev/null
```

**For each suspicious `.plist` found, inspect it:**
```bash
plutil -p ~/Library/LaunchAgents/<suspicious.plist>
# or
cat ~/Library/LaunchAgents/<suspicious.plist>
```

**Flag:**
- `ProgramArguments` pointing to `~/Library/`, `/tmp/`, `/var/folders/`, `~/Downloads/`, `~/Desktop/`
- `ProgramArguments` with shell one-liners, curl/wget, base64 decode
- Plist names not matching legit installed apps
- `RunAtLoad = true` + unusual script path
- `KeepAlive = true` - restart-on-kill watchdog (common malware pattern)
- Labels with random strings or slightly-off Apple domain mimics

**False+:**
- `com.github.homebrew.*` - Homebrew services
- `com.adobe.*` - Adobe LaunchAgents (verify paths point to `/Applications/Adobe*`)
- `com.google.keystone*` - Google Software Update
- `com.microsoft.*` - Office update agents

---

### 3.2 - Crontab
**Tier:** T1 (user crontab), T2 (root + system crontab)  

```bash
# User crontab
crontab -l 2>/dev/null

# System crontab
cat /etc/crontab 2>/dev/null

# Additional cron directories
ls -la /etc/cron.d/ 2>/dev/null
ls -la /etc/periodic/ 2>/dev/null
ls -la /etc/periodic/daily/ /etc/periodic/weekly/ /etc/periodic/monthly/ 2>/dev/null
```

**T2 - Root crontab:**
```bash
sudo crontab -l
```

**Flag:**
- Cron running scripts from home dirs, `/tmp`, or unusual paths
- `curl | bash` or `wget -O- | sh` patterns - download and execute
- Very frequent schedules on unknown tasks (every minute, every 5 min)
- `@reboot` entries running unusual scripts

---

### 3.3 - Login Items (macOS 13+ Background Task Management)
**Tier:** T1  

```bash
# macOS 13+ - Background Task Management
sfltool dump-login-items 2>/dev/null

# Legacy login items plist
defaults read ~/Library/Preferences/com.apple.loginitems.plist 2>/dev/null

# BTM database (macOS 13+)
ls -la ~/Library/Application\ Support/com.apple.backgroundtaskmanagementagent/ 2>/dev/null

# Legacy StartupItems (rarely used but check)
ls -la /Library/StartupItems/ 2>/dev/null
ls -la /System/Library/StartupItems/ 2>/dev/null
```

**Flag:**
- Login items pointing to apps not installed via App Store or recognized installers
- Items in unusual paths (Downloads, Desktop, temp dirs)
- Recently added items (check mtime)

---

### 3.4 - Configuration Profiles (MDM/Malicious Profiles)
**Tier:** T1  

```bash
# List installed configuration profiles
profiles list 2>/dev/null

# More detail
profiles show -all 2>/dev/null
```

**Flag:**
- Profiles not installed by your MDM or IT
- Profiles configuring proxy, DNS, or VPN to unusual servers
- Unusual org names or no signing cert
- Profiles disabling SIP, Gatekeeper, or security policies

---

## Phase 4: File Activity


---

### 4.1 - Files in Temp Directories
**Tier:** T1  

```bash
# Files in /tmp
find /tmp -type f -maxdepth 5 2>/dev/null | head -50

# Files in user temp directories (macOS uses /var/folders)
find /var/folders -name "*.sh" -o -name "*.py" -o -name "*.rb" -o -name "*.pl" 2>/dev/null | head -30

# Executables specifically
find /tmp /var/folders -perm +111 -type f 2>/dev/null | head -30
```

**Flag:**
- Shell scripts or interpreter scripts in temp dirs
- Executables with no extension or misleading extensions (`.pdf`, `.doc`, `.jpg`)
- Files with random-looking names (8+ hex chars, UUID-style)
- Recently created files (check mtime)

---

### 4.2 - Scripts in Library Directories
**Tier:** T1  

```bash
find ~/Library -name "*.sh" -o -name "*.py" -o -name "*.rb" -o -name "*.pl" -o -name "*.swift" 2>/dev/null | grep -v ".app/" | head -30
```

**Flag:**
- Shell/script files in `~/Library` not inside `.app` bundles
- Scripts in `~/Library/Application Scripts/` for unexpected apps
- Scripts with suspicious names or referencing network addresses

---

### 4.3 - Recently Installed Applications
**Tier:** T1  

```bash
# Applications sorted by modification date
ls -lat /Applications/ | head -20

# Check for apps installed in unusual locations
find ~/Applications/ -maxdepth 2 -type d -name "*.app" 2>/dev/null
find ~/Downloads/ -type d -name "*.app" 2>/dev/null
```

**Flag:**
- Recently installed apps (last few days) you don't recognize
- Apps in `~/Applications` or `~/Downloads` instead of `/Applications` - shadow installation
- `.app` bundles in non-standard locations

---

### 4.4 - Code Signing Verification for Suspicious Files
**Tier:** T1  

```bash
# Check code signature for a specific file
codesign -dv --verbose=4 /path/to/suspicious/binary 2>&1

# Gatekeeper assessment
spctl --assess --verbose /path/to/suspicious/binary 2>&1

# Check quarantine attribute (should be present on downloaded files, absence may indicate bypass)
xattr -l /path/to/suspicious/binary | grep com.apple.quarantine

# Check all extended attributes
xattr -l /path/to/suspicious/binary
```

**Flag:**
- `code object is not signed at all` - unsigned
- `CSSMERR_TP_NOT_TRUSTED` - self-signed or untrusted cert
- `rejected` from `spctl` - failed Gatekeeper assessment
- Missing `com.apple.quarantine` on supposedly-downloaded file - Gatekeeper bypass
- Unknown developer ID (note Team ID for research)

---

## Phase 5: User & Account Activity


---

### 5.1 - Local User Accounts
**Tier:** T1  

```bash
# List all local user accounts
dscl . list /Users | grep -v '^_'

# Get more details on each non-system user
dscl . -read /Users/<username> UniqueID PrimaryGroupID NFSHomeDirectory UserShell RealName 2>/dev/null
```

**Flag:**
- Unrecognized accounts (not owner, not standard system accounts)
- Home dir set to `/var/root`, `/tmp`, or unusual paths
- Unrecognized accounts with `/bin/bash` or `/bin/zsh`
- UID 0 on account other than `root`

**Known system accounts (normal):** `_spotlight`, `_www`, `_mysql`, `_postgres`, `nobody`, `daemon`, `root`

---

### 5.2 - Login History
**Tier:** T1  

```bash
# Recent login history
last -20

# Current logged-in sessions
who

# wtmp / utmp detailed
last -F | head -40
```

**Flag:**
- Logins from unusual source IPs (SSH shows source IP)
- Logins at unusual times (3 AM on 9-5 workstation)
- Multiple rapid logins from different IPs - credential stuffing
- Logins for accounts that shouldn't log in remotely

---

### 5.3 - SSH Configuration and Authorized Keys
**Tier:** T1  

```bash
# Authorized SSH keys for current user
cat ~/.ssh/authorized_keys 2>/dev/null

# SSH config
cat ~/.ssh/config 2>/dev/null

# Check SSH daemon configuration
cat /etc/ssh/sshd_config 2>/dev/null | grep -E "PermitRootLogin|PasswordAuthentication|AuthorizedKeysFile|ListenAddress|Port"
```

**Flag:**
- Unrecognized public keys in `authorized_keys`
- `PermitRootLogin yes` on user workstation - should never be enabled
- `ListenAddress` or `Port` changed from defaults
- Unexpected `Host` entries in `~/.ssh/config` proxying through unusual systems

---

### 5.4 - T2: Authentication Logs
**Tier:** T2 (sudo required)  

```bash
# Authentication events in last 4 hours
sudo log show --predicate 'eventMessage contains "authentication"' --last 4h --style compact 2>/dev/null | head -50

# sudo usage
sudo log show --predicate 'eventMessage contains "sudo"' --last 24h --style compact 2>/dev/null | head -50

# SSH daemon events
sudo log show --predicate 'eventMessage contains "sshd"' --last 24h --style compact 2>/dev/null | head -50

# Failed authentication (brute force indicator)
sudo log show --predicate 'eventMessage contains "failed" AND eventMessage contains "authentication"' --last 24h --style compact 2>/dev/null | head -30
```

---

## Phase 6: Driver/Module Activity


---

### 6.1 - System Extensions (macOS 10.15+)
**Tier:** T1  

```bash
systemextensionsctl list
```

**Flag:**
- Extensions from unrecognized vendors
- Extensions in `[activated waiting for user]` or `[terminated]` unexpectedly
- Security extensions (`com.crowdstrike`, `com.sentinelone`, `co.elastic`) - verify match deployed security tools
- Note Bundle ID + Team ID for unknown extensions

**Known legit vendors:**
- CrowdStrike: `com.crowdstrike.falcon.Agent`
- SentinelOne: `com.sentinelone.SentinelAgent`
- Carbon Black: `com.carbonblack.*`
- Elastic: `co.elastic.systemextension`
- Jamf: `com.jamf.*`

---

### 6.2 - Kernel Extensions (Legacy, Still Active)
**Tier:** T1  

```bash
# List non-Apple kernel extensions
kextstat | grep -v com.apple
```

**Note:** Apple deprecated kexts in favor of System Extensions. macOS 12+: very few third-party kexts expected. Any kext = scrutiny.

**Flag:**
- Kexts not from known vendors
- Random or obfuscated bundle identifiers
- Kexts loaded from unusual paths (not `/Library/Extensions/` or `/System/Library/Extensions/`)

---

## Phase 7: Script & Command Execution


---

### 7.1 - Shell History
**Tier:** T1  

```bash
# zsh history (default shell on modern macOS)
cat ~/.zsh_history 2>/dev/null | tail -150

# bash history (if bash is used)
cat ~/.bash_history 2>/dev/null | tail -150

# Check history file sizes and modification times
ls -la ~/.zsh_history ~/.bash_history 2>/dev/null
```

**Flag:**
- `curl`/`wget` piped to `bash`/`sh`
- Download + execute: `curl -o /tmp/x http://... && chmod +x /tmp/x && /tmp/x`
- Base64 decode + execute: `echo "..." | base64 -d | bash`
- `osascript -e '...'` with unusual AppleScript - common in macOS malware
- `python -c`, `ruby -e`, `perl -e` one-liners with complex encoded content
- `nc`/`ncat` establishing outbound connections
- Commands modifying LaunchAgents/LaunchDaemons dirs
- `codesign --remove-signature` or `xattr -d com.apple.quarantine` - Gatekeeper bypass

---

### 7.2 - Application Script Artifacts
**Tier:** T1  

```bash
# Application scripts directory
find ~/Library/Application\ Scripts -type f 2>/dev/null

# Check for script-like files in Library
find ~/Library -maxdepth 3 -name "*.sh" -o -name "*.py" -o -name "*.rb" 2>/dev/null | grep -v "\.app/"
```

---

### 7.3 - T2: XProtect and MRT Logs
**Tier:** T2 (sudo required)  

```bash
# XProtect detections (Apple's built-in AV signatures)
sudo log show --predicate 'eventMessage contains "XProtect"' --last 24h --style compact 2>/dev/null | head -30

# Malware Removal Tool (MRT) events
sudo log show --predicate 'eventMessage contains "MRT"' --last 24h --style compact 2>/dev/null | head -30

# Security daemon events
sudo log show --predicate 'subsystem == "com.apple.securityd"' --last 4h --style compact 2>/dev/null | head -50
```

---

## Phase 8: EDR/Security Tool Status


---

### 8.1 - Detect Running Security Agents
**Tier:** T1  

```bash
# Check for common EDR/AV/security agent processes
ps aux | grep -iE "falcon|sentinelagent|elastic|mdatp|wdavdaemon|cbagentd|cylance|eset|sophos|bitdefender|mcafee|malwarebytes|carbon|osquery|wazuh|ossec"

# Check for security-related system extensions
systemextensionsctl list | grep -iE "falcon|sentinel|elastic|carbon|cylance|eset|sophos"
```

**Flag:**
- Agent process listed but not actually running (zombie or binary tampered)
- Extension present but process NOT in `ps` - agent disabled/killed
- Expected security tools not found on managed endpoint

---

### 8.2 - macOS Built-in Security Status
**Tier:** T1  

```bash
# Gatekeeper status
spctl --status

# SIP status
csrutil status

# Firewall status
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

**Flag:**
- `Gatekeeper: disabled` - significant security reduction
- `System Integrity Protection status: disabled` - SIP off (compromise or authorized research)
- Firewall disabled on user machine

---

### 8.3 - T2: TCC Privacy Database
**Tier:** T2 (requires Full Disk Access for Terminal)  

```bash
sudo sqlite3 "/Library/Application Support/com.apple.TCC/TCC.db" \
  "SELECT service,client,auth_value,last_modified FROM access WHERE auth_value=2 ORDER BY last_modified DESC LIMIT 50;" 2>/dev/null
```

**Flag:**
- `kTCCServiceCamera` or `kTCCServiceMicrophone` granted to unrecognized apps
- `kTCCServiceScreenCapture` granted to unusual apps
- `kTCCServiceSystemPolicyAllFiles` (FDA) granted to unrecognized non-system apps
- Recent grants (last_modified) matching when suspicious activity began

---

## Quick Reference: macOS IOC Severity Ratings

| IOC | Severity | Notes |
|-----|----------|-------|
| Process running from `/tmp` | Critical | Almost never legitimate |
| Unlinked process binary (`lsof +L1` hit) | Critical | Classic malware technique |
| LaunchAgent pointing to `/tmp` or `~/Downloads` | Critical | Clear malware persistence |
| Outbound connection from `bash` or `python` | High | C2 beacon or reverse shell |
| Non-Apple kernel extension present | High | Requires investigation |
| Gatekeeper disabled | High | System security bypassed |
| `curl` piped to `bash` in history | High | Download-and-execute |
| Unsigned binary in `/Applications` | Medium | Investigate but common for dev tools |
| New user account added recently | Medium | Could be legitimate IT action |
| `com.apple.quarantine` removed from file | Medium | Gatekeeper bypass |
| Unusual authorized_keys entry | High | Remote access backdoor |
| WMI-equivalent: unusual LaunchDaemon | High | Persistence mechanism |
| `osascript` in history | Medium | Could be automation or malware |
| Sustained 80%+ CPU over 3h on an unaccounted process | High | Cryptominer profile - Critical if paired with a stratum or pool connection |
| `DYLD_INSERT_LIBRARIES` set globally via `launchctl` | Critical | Library injection into everything launchd spawns |
| SIP disabled (`csrutil status`) | High | Phase 1 tooling and platform binaries no longer protected |
