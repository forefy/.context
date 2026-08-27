---
name: vm-lab
description: Spin up and drive disposable local VMs (macOS, Windows, Linux) for real cross-OS debugging over SSH - process/network/file/memory triage, live event capture, code-signing checks, dynamic instrumentation, malware/RE repro - on any of three free hypervisors (Parallels, VirtualBox, VMware Fusion/Workstation) with no paid CLIs. Use whenever a task needs to run commands or inspect a real, isolated macOS/Windows/Linux machine that is not this host. Covers picking a provider+guest, bootstrapping a fresh guest to SSH, per-OS "run commands reliably over SSH" gotchas, a task→tool matrix, arch-forked toolkit install recipes, and a verifier. Connection details live in config.local.env; ./verify.sh proves the toolkits are callable.
---

# VM Lab - cross-OS debugging on any free hypervisor

Disposable local VMs - real macOS, Windows, and Linux, isolated from this host -
for cross-OS repro, live process/network/file/memory triage, code-signing checks,
and dynamic instrumentation. Works on **Parallels, VirtualBox, or VMware** with
**no paid tooling**.

## The core idea
**SSH is the universal substrate.** The hypervisor only ever does four things -
`list`, `get-ip`, `power`, `snapshot` - and each of the three has a *free* way to do
all four (`providers/*.sh`). Everything valuable (the debug toolkit) runs over SSH
and is hypervisor-agnostic; it only varies by **guest OS** and **CPU arch**. So this
skill is a thin swappable provider layer + a big OS/arch-specific debugging core.

## On every invocation - ask first, then route
This skill serves three OSes and three providers. Before doing anything, establish:
1. **Which guest** - macOS, Windows, or Linux? (drives `toolkits/<os>.md` + SSH gotchas)
2. **Which provider** - Parallels / VirtualBox / VMware? (drives `providers/<name>.sh`)
3. **Set up fresh, or use an existing guest?**
   - *Existing* → confirm it's in `config.local.env`, `./ctl.sh <tag> up`, `./verify.sh <tag>`, go.
   - *Fresh* → `bootstrap/` (Path A one-liner, or Path B unattended), then add to config, verify, **snapshot**.

If a `config.local.env` already defines the guest the task needs, skip the questions
and use it. Ask only what's genuinely unresolved.

## Config & connect
All mutable details live in **`config.local.env`** (copy from `config.example.env`;
it's gitignored so your IPs/keys never get shared). Then:
```bash
source lib.sh                 # loads config + helpers (rc, rc_sudo, ssh_cmd, prov, ctl)
rc mac 'uname -a'             # run on the macOS guest
rc win 'whoami'              # Windows: auto-wrapped as base64 PowerShell
rc lin 'uname -a'            # Linux
rc_sudo mac 'fs_usage -w'    # sudo on mac/linux (echoes the guest pw via -S)
./verify.sh                   # every guest: tools present + callable, with hints
./ctl.sh doctor               # host preflight: which providers/tools are present here
./ctl.sh win up               # boot + WAIT for sshd; then down|ip|ssh|snaps|vms
push mac ./tool /tmp/tool     # copy to guest (scp); pull mac /tmp/x.pcap ./  to fetch
tun  mac -L 8080:127.0.0.1:8080   # port-forward (MITM/reach a guest service)
./ctl.sh mac reset            # restore the clean snapshot (RESET_SNAPSHOT) - the disposable loop
```
Guests are tags (`mac`/`win`/`lin`, your choice) with `{PROVIDER, OS, ARCH, VMNAME,
IP, USER, AUTH, KEY/PW}`. Leave `IP` blank to auto-discover (provider → mDNS → ARP).

**Quoting caveat:** `rc <tag> 'cmd'` single-quotes the command, so an embedded `'`
breaks it. For anything non-trivial (or with quotes) use **`rcs <tag> <script> [args]`**
- it pushes a local script, runs it (bash for mac/linux, `powershell -File` for
windows), and cleans up. Or the heredoc form `rc mac 'bash -s' <<'EOF' … EOF`.
`run_win` (base64) is quote-safe for Windows one-liners.

## Inspecting an app (installed or running)
`./inspect-app.sh <tag> <app>` - one-command triage of any app on a guest:
identity, code signing / notarization, **hardened-runtime + injectability verdict**
(tells you whether the Frida path will even work), entitlements, URL schemes,
process tree, loaded modules, bundled runtimes. It **auto-detects Electron** and
chains `tools/electron-triage.sh`, which maps the renderer↔main attack surface -
`exposeInMainWorld` bridges, `.handle("…")` IPC channels, `webPreferences` security
flags (contextIsolation/sandbox/nodeIntegration), and privileged custom protocols -
all without `node` (a pure-python `tools/asar.py` extracts the asar on the guest).
```bash
./inspect-app.sh mac Claude        # macOS: codesign/entitlements/schemes + electron map
./inspect-app.sh lin firefox       # linux: dpkg/rpm/flatpak + systemd + maps
./inspect-app.sh win Claude        # windows: uninstall-registry + signature + modules
```
Per-OS logic is in `tools/inspect-<os>.{sh,ps1}`; `asar.py` is a reusable
standalone Electron extractor (`python3 tools/asar.py app.asar --list`).

## Fresh guest → SSH (bootstrap)
A pristine guest has no sshd/key, and only VirtualBox can type into the console
headlessly. Two paths (Path B detailed in `bootstrap/unattended.md`):
- **Path A - one-line paste:** paste `bootstrap/<os>.{sh,ps1}` into the guest
  console once (a human is most reliable here; some GUI consoles mangle synthetic
  input), then everything is over SSH.
- **Path B - unattended/seed** (best for VirtualBox/VMware): bake sshd+key in at
  install via cloud-init / autounattend.xml (`bootstrap/unattended.md`).
After it connects: pin/blank the IP in config, `./verify.sh <tag>`, then **snapshot**
so you never bootstrap again. You supply ISOs; `bootstrap/unattended.md` lists
official sources and can seed them.

## Run commands reliably over SSH - per OS
- **macOS** (`toolkits/macos.md`): no `timeout`; bound live captures with
  background+`sleep`+`kill -INT` (never `-9`); `eslogger` needs a pty (`script`) or
  it shows 0 events.
- **Windows** (`toolkits/windows.md`): `run_win` sends PowerShell as UTF-16LE
  base64 and strips CLIXML noise; structured output → write-to-file-then-read;
  `cmd` one-liners are reliable.
- **Linux** (`toolkits/linux.md`): the easy one - one shell, real `timeout`, real
  signals; `rc_sudo` for root.

## Toolkits (task → tool matrix + install recipes)
Each `toolkits/<os>.md` has the full matrix and arch-forked install steps:
- **macOS/arm64** - built-ins first (`ps`, `eslogger`, `lsof`, `nettop`, `tcpdump`,
  `vmmap`, `codesign`, `sample`, `log`); CLT for `otool`/`nm`; optional Frida.
  VM caveat: `powermetrics` needs `--samplers tasks`; `dtruss` SIP-blocked.
- **Windows/arm64|x64** - native cmdlets first; add only `autorunsc`/`handle`/
  `sigcheck`/`procdump`/`Procmon`; optional `cdb`. VM caveat: `wpr` fails
  (0x80070032) → use `logman`/`Procmon`. **Pick ARM64 vs x64 downloads by `ARCH`.**
- **Linux/x64|arm64** - `apt`/`dnf`/`pacman` install everything: `strace`,
  `bpftrace`, `perf`, `gdb`, `ss`, `lsof`, `tcpdump`, `auditd`. VM caveat: `perf`
  hardware counters usually unavailable → software events only.

## Maintainable & self-remembering
When you learn a new environment quirk, install recipe, or gotcha, **append it to
`LEARNINGS.md`** (dated, tagged by OS/arch/provider) - that file travels with the
repo, so the knowledge compounds across sessions and users instead of living in one
machine's memory. Re-run `./verify.sh` anytime to re-prove every tool is callable.

## Notes
- **Safety** - the default `SSH_OPTS` disable host-key checking (right for
  disposable, re-snapshotted VMs; removes MITM protection). Never point this at a
  machine you care about; override `SSH_OPTS` in config for anything non-throwaway.
  `config.local.env` is sourced as shell - only use configs you trust.
- **Disposable** - installing tools, killing processes, editing config, rebooting
  are all fair game; a snapshot restore recovers anything. Take a clean snapshot
  right after bootstrap.
- **No paid CLIs**: Parallels needs only free `prlctl list`; VirtualBox's
  `VBoxManage` is fully free; VMware Fusion/Workstation are free for personal use.
  The provider layer degrades to SSH-based fallbacks when a native verb is gated.
