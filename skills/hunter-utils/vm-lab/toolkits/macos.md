# macOS guest toolkit (Apple Silicon, arm64)

macOS guests are only legal/practical on Apple hardware - Parallels or VMware
Fusion on an Apple Silicon Mac. Built-ins cover almost everything; only ESF
reliability, Command Line Tools, and (optional) Frida need setup.

## Run-commands-over-SSH gotchas
- **Multi-line:** `rc mac 'bash -s' <<'EOF' … EOF` (or `eval "$(ssh_cmd mac) 'bash -s'"`).
- **sudo non-interactively:** `rc_sudo mac '<cmd>'` (does `echo $PW | sudo -S`).
- **No `timeout`** on macOS. Bound a live capture by backgrounding it, `sleep`,
  then `kill -INT` + `wait` - **never `kill -9`** (loses buffered output; for ESF
  it also leaks the client slot).

## Task → tool matrix (all base-system unless noted)
| Task | Tool |
|------|------|
| Process tree + cmdline | `ps -axo pid,ppid,user,command` |
| Live exec/fork/file events | `eslogger exec fork open …` (root; see ESF note) |
| File activity | `sudo fs_usage -w -f filesys` |
| Socket ↔ process | `sudo lsof -nP -iTCP -sTCP:ESTABLISHED` |
| Per-flow byte throughput | `nettop -d -x -P -s1` |
| Packet capture | `sudo tcpdump -i en0 -w x.pcap` |
| Loaded images (live proc) | `vmmap <pid>` · `otool -L <bin>` † |
| Symbols / imports | `nm` · `otool -tV` † · `dyld_info` † |
| Code signing / trust | `codesign -dv --verbose=4` · `spctl -a -vv` |
| Persistence / autostart | launchd (`~/Library/LaunchAgents`, `/Library/Launch*`), `sfltool dumpbtm`, login items |
| File locks / open handles | `sudo lsof <path>` |
| RAM/CPU per process | `top -l1 -stats pid,command,cpu,mem` · `footprint <pid>` · `vm_stat` |
| CPU stacks / profiling | `sample <pid> 5` · `spindump <pid>` |
| Syscall trace | `sudo dtruss`/`ktrace` - **SIP-limited**, prefer `eslogger` |
| Unified log | `log stream --style compact --predicate '…'` |
| Memory dump | `lldb -p N` → `process save-core` · `sample` |
| Dynamic instrumentation | Frida (see below) |

† CLT stubs on a clean VM - `xcode-select --install` (GUI) or run one once to
auto-prompt. `vmmap`+`codesign` cover a lot without CLT.

## ESF (`eslogger`) - reliable capture over SSH
`eslogger` is Apple's built-in ESF CLI (macOS 13+): same exec/fork/file events as
the old Objective-See ProcessMonitor/FileMonitor, as JSON with signing + ancestry.
**No download, no Full Disk Access** - but it **block-buffers** stdout (flushes at
~8 KB / clean exit) and often ignores SIGINT, so naive short captures show 0
events and a `wait` can hang. Force a pty with `script`:
```bash
rc_sudo mac 'script -q /tmp/es.log eslogger exec &'   # pty => line-buffered
# …trigger activity in another rc call…
rc_sudo mac 'pkill -INT eslogger; sleep 0.5; pkill -9 eslogger'
rc mac 'grep -c event_type /tmp/es.log'               # consistent, non-zero
```
Never `wait` on `eslogger`; the pty (not the signal) is what makes it reliable.

## VM-specific limitation (folded in from field notes)
- **`powermetrics`** hardware samplers (`cpu_power`,`gpu_power`) fail in a VM -
  `IODeviceTree:/arm-io/pmgr` doesn't exist (no SMC/pmgr). The **`tasks` sampler
  works**: `sudo powermetrics -n 1 --samplers tasks` (per-proc CPU ms/s, wakeups).
- `dtruss` is SIP-blocked (`Operation not permitted`) - use `eslogger` + `log stream`.
- Objective-See DNSMonitor needs a GUI-approved Network Extension; `log stream`
  on mDNSResponder masks qnames. For a process's domains use live TCP endpoints
  (`lsof`/`nettop`) + reverse-DNS.

## Optional: Frida (dynamic instrumentation)
Stock CLT Python is 3.9; `frida-tools` needs 3.10+. Install python.org 3.12
headlessly, then Frida:
```bash
# on the guest:
curl -LO https://www.python.org/ftp/python/3.12.8/python-3.12.8-macos11.pkg
echo "$PW" | sudo -S installer -pkg python-3.12.8-macos11.pkg -target /
/usr/local/bin/python3.12 -m pip install frida-tools
# CLIs land in /Library/Frameworks/Python.framework/Versions/3.12/bin (add to PATH)
```
- **Injection needs root** (`frida.attach()` as user fails on `task_for_pid`).
- **SIP on** ⇒ can only instrument non-Apple/self-signed binaries; system binaries
  need SIP off. `frida-ps` works without root.
- Frida 17 API: `Module.getExportByName(null,n)` → `Module.getGlobalExportByName(n)`.

## GUI/computer-use on the console (optional)
SSH needs no GUI session, but WindowServer/GUI apps do. Enable headless auto-login
(survives reboots, FileVault must be Off): set `/etc/kcpassword` (pw XOR Apple's
cipher `7D 89 52 23 D2 BC DD EA A3 B9 1F`, padded to ×12) + `defaults write
/Library/Preferences/com.apple.loginwindow autoLoginUser <user>`. Verify with
`stat -f %Su /dev/console`. NOTE: the kcpassword write may trip an agent's
credential classifier - the human may have to run that one line.
