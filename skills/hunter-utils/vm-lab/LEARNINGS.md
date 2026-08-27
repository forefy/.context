# LEARNINGS - environment quirks & recipes discovered in the field

Append here whenever you learn something that isn't obvious from the docs: a tool
that fails in a VM, an install gotcha, a provider quirk. Keep entries dated and
tagged `[os/arch/provider]` so they stay searchable. This file ships with the repo
so the knowledge compounds across sessions and users. **Do not put secrets here**
(IPs/keys/passwords live in the gitignored config.local.env).

Format:
```
## YYYY-MM-DD - short title  [os/arch/provider]
What broke / what works, with the exact command.
```

---

## 2026-08-27 - Electron IPC audit: minification-proof grep patterns  [any/electron]
Auditing an Electron app's app.asar (JS is stored plaintext, grep-able directly):
handlers minify to `<alias>.handle("chan")` so grep `.handle("` (NOT `ipcMain.handle`,
which is aliased). webPreferences flags minify booleans: `contextIsolation:!0`=true,
`:!1`=false. Custom-IPC channel names may be templated with a per-build UUID prefix
(`$eipc_message$_<uuid>_$_<ns>_$_<svc>_$_<method>`) so `.handle("literal")` finds
zero - the surface lives in the preload's exposeInMainWorld + the templated channels.
`tools/asar.py` extracts individual files with no node. `tools/electron-triage.sh`
automates the whole map; `./inspect-app.sh <tag> <app>` chains it after signing/entitlement
triage. Validated on Claude.app (Electron 42, contextIsolation+sandbox on, nodeIntegration off).

## 2026-08-27 - hardened+notarized macOS apps block the Frida path  [macos/arm64]
A Developer-ID app with Hardened Runtime (`flags=0x10000(runtime)`) and no
`disable-library-validation` / `allow-dyld-environment-variables` / `get-task-allow`
entitlement CANNOT be Frida/dylib-injected without SIP off or re-signing. inspect-app.sh
prints this verdict from codesign flags+entitlements. For such targets use static
(asar/IPC map) + observational (eslogger/fs_usage/tcpdump), not injection.

## 2026-08-27 - lib.sh must be zsh-safe (macOS default shell)  [host/any]
`source lib.sh` from an interactive shell runs under **zsh** on macOS, not bash.
Three bashisms broke it: (1) `gp()` indirect expansion `${!v}` → "bad substitution"
(fixed via `eval "printf '%s' \"\${$v-}\""`); (2) `${BASH_SOURCE[0]}` self-path
(fixed with a ZSH_VERSION branch using eval-deferred `${(%):-%x}`); (3) unquoted
`$GUESTS` word-splitting - zsh does NOT split unquoted expansions (fixed: guest_list
emits newlines via tr, guest_exists uses while-read). The bash-shebang scripts
(ctl.sh/verify.sh) were unaffected. Verified: `source lib.sh; rc mac ...; rc win ...`
now works in zsh. Caught by live-testing against the real VMs.

## 2026-08-22 - powermetrics hardware samplers fail in a VM  [macos/arm64/parallels]
`powermetrics --samplers cpu_power|gpu_power` → "cannot find the IO registry entry
for IODeviceTree:/arm-io/pmgr" (VM has no SMC/pmgr). The **tasks sampler works**:
`sudo powermetrics -n 1 --samplers tasks` (per-proc CPU ms/s, wakeups). Likely
applies to VMware Fusion too (same missing hardware).

## 2026-08-22 - wpr can't profile in a VM  [windows/arm64/parallels]
Every `wpr` profile → `0x80070032` ERROR_NOT_SUPPORTED (no PMU/kernel profiling in
the guest). Binary runs (`-status`/`-cancel` fine). Substitutes that work in-VM:
`logman create trace ... -p Microsoft-Windows-Kernel-Process -ets` (real .etl), and
Procmon (behavioral). CPU stack-sampling has no in-VM substitute - needs bare metal
or PMU passthrough. Expect the same on VirtualBox/VMware unless vPMC is enabled.

## 2026-08-22 - dtruss is SIP-blocked  [macos/arm64]
`dtruss /bin/echo` → "Operation not permitted" (SIP). Use `eslogger` + `log stream`
for behavior instead of dtruss/ktrace.

## 2026-08-23 - eslogger block-buffers over SSH  [macos/arm64]
Plain-pipe `eslogger` capture flakes to 0 events (flushes at ~8 KB / clean exit) and
often ignores SIGINT (a `wait` can hang). Fix: force a pty - `sudo script -q out
eslogger exec &`, trigger activity, `pkill -INT eslogger`. Never `wait` on it.

## 2026-08-23 - Frida needs Python 3.10+, injection needs root  [macos/arm64]
Stock CLT Python 3.9 fails frida-tools import. Install python.org 3.12 headlessly,
`pip install frida-tools`. `frida.attach()` needs root (task_for_pid); SIP-on means
only non-Apple/self-signed binaries are hookable. Frida 17:
`Module.getGlobalExportByName(n)` replaced `getExportByName(null,n)`.

## 2026-08-23 - cdb symbol resolution hangs over SSH  [windows/arm64]
`lm` / any symbol lookup hangs cdb via the msdl server under SSH. Set
`$env:_NT_SYMBOL_PATH=''` (or a local cache) first, wrap in `Start-Job` +
`Wait-Job -Timeout` so a stuck session can't hang the SSH call.

## 2026-08-xx - Windows OpenSSH FoD won't fetch on fresh VMs  [windows/arm64]
`Add-WindowsCapability -Online -Name OpenSSH.Server` can fail (0x800f0950 /
0x800f0954) even with internet. Fallback: the Win32-OpenSSH GitHub release
(bootstrap/windows.ps1 auto-picks ARM64 vs Win64). Admin key auth requires
`administrators_authorized_keys` with an ACL granting only Administrators+SYSTEM.

## 2026-08-xx - GUI console mangles synthetic input without guest tools  [any/parallels]
With no guest tools installed, computer-use into the console is unreliable (every
char → `a`; paste/scroll/clipboard-sync ignored; single `key` presses work but not
`/` or uppercase). Prefer: human pastes the one bootstrap line, or use VirtualBox
`prov_type` (VBoxManage keyboardputstring), or Path B unattended install.
