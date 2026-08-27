# Windows guest toolkit (arm64 on Apple Silicon, or x64 on AMD/Intel)

Native tooling covers process/network/signing/logging; add only the Sysinternals
tools native can't do, plus optional cdb for debugging. **Arch matters** for every
download - pick the ARM64 or x64 asset to match `GUEST_win_ARCH`.

## Run-commands-over-SSH gotchas (each one cost real time to learn)
1. **Send PowerShell as UTF-16LE base64** to dodge quoting hell - `run_win`
   (in lib.sh) does this for you: `run_win win 'Get-Process | ...'`.
2. **Non-string output gets CLIXML-mangled** over SSH (blank/garbled). For
   structured data, **write to a file and read it back**:
   `... | Out-File C:\Users\<u>\o.txt` then `rc win 'cmd /c type C:\Users\<u>\o.txt'`.
   `run_win` already strips the `#< CLIXML` / `<Objs …>` noise lines.
3. Always `$ProgressPreference='SilentlyContinue'` (progress leaks as CLIXML) -
   `run_win` prepends this.
4. **`cmd` one-liners are reliable**: `netstat -ano`, `tasklist`, `type`.
   `timeout` errors under redirected SSH stdin - use `ping -n N 127.0.0.1 >nul`
   as a sleep, or `Start-Sleep` in PowerShell.
5. Long/interactive captures: `run_in_background`, or write-to-file-then-read
   (a foreground call can truncate).

## Task → tool matrix
| Task | Native | Sysinternals (add) |
|------|--------|--------------------|
| Process tree + cmdline | `Get-CimInstance Win32_Process` (ParentProcessId, CommandLine) | - |
| Live exec/file/registry events | ETW `logman` (see limits) | `Procmon /BackingFile` |
| Socket ↔ process | `Get-NetTCPConnection -State Established -OwningProcess` · `netstat -ano` | - |
| Byte throughput | `Get-NetAdapterStatistics` | - |
| Packet capture | `pktmon start --capture --pkt-size 0 -f x.etl` → `pktmon etl2pcap x.etl` | - |
| Loaded modules (live proc) | `(Get-Process -Id N).Modules` | `listdlls` · `handle64` |
| Symbols / imports | `dumpbin` (VS) | `sigcheck64 -a` |
| Code signing / trust | `Get-AuthenticodeSignature` | `sigcheck64 -a -h` |
| Persistence / autostart | `Get-ScheduledTask` · `Get-CimInstance Win32_Service` | `autorunsc64 -a * -c` |
| File locks / open handles | - | `handle64 <path>` |
| RAM/CPU per process | `Get-Process` · `Get-Counter '\Process(*)\% Processor Time'` · `tasklist` | - |
| CPU stacks / profiling | `wpr` (see limits) | `procdump64` |
| Syscall/low-level trace | ETW `logman`/`wpr` | `Procmon` |
| Event log | `Get-WinEvent` · `wevtutil` | - |
| Memory dump | - | `procdump64 -ma <pid>` |
| Debugging | `cdb` (see below) | - |

## Sysinternals - install only what native can't do
```powershell
$d='C:\Tools\Sysinternals'; mkdir $d -Force | Out-Null
# x64 host/guest - CLI user-mode tools:
'autorunsc64.exe','handle64.exe','sigcheck64.exe','procdump64.exe' | % {
  iwr "https://live.sysinternals.com/$_" -OutFile "$d\$_" -UseBasicParsing }
# ARM64 guest note: live.sysinternals.com serves x86/x64 only; those x64 CLIs run
# fine under emulation. Only driver-based Procmon needs the NATIVE ARM64 suite:
#   iwr https://download.sysinternals.com/files/SysinternalsSuite-ARM64.zip -OutFile $d\s.zip
#   Expand-Archive $d\s.zip $d -Force
```
Pass `-accepteula` on first run. Skip pslist/pskill/tcpvcon - native beats them.

## Optional: Frida (dynamic instrumentation)
`pip install frida-tools` (needs Python 3.10+; install from python.org if the store
build is older). Match the Frida wheel to the guest arch (arm64 vs x64). Injecting
into another user's / a protected process needs an elevated session - the SSH
session already runs elevated if you seeded `administrators_authorized_keys`. No SIP
equivalent on Windows, so system binaries are hookable (mind PPL/anti-tamper on some).

## VM-specific limitation (folded in from field notes)
- **`wpr`** fails every profile with `0x80070032` ERROR_NOT_SUPPORTED - the guest
  exposes no PMU/kernel-profiling. Substitutes that DO work in-VM:
  - ETW software providers via **`logman`**:
    `logman create trace t -p Microsoft-Windows-Kernel-Process -ets` → real .etl.
  - **Procmon** for behavioral (proc/file/registry) capture.
  - CPU **stack-sampling** has no in-VM substitute (needs PMU) - sample on bare metal.

## Optional: cdb (headless debugger over SSH)
Install the SDK Debuggers feature only (bootstrapper pulls the MSIs; use the
current link from learn.microsoft.com/windows/apps/windows-sdk/downloads):
```powershell
winsdksetup.exe /features OptionId.WindowsDesktopDebuggers /quiet /norestart /ceip off
# -> C:\Program Files (x86)\Windows Kits\10\Debuggers\arm64\cdb.exe  (or \x64\)
```
- cdb is the headless/SSH-friendly one; classic `windbg.exe` ships alongside it;
  modern WinDbgX (`winget install Microsoft.WinDbg`, TTD) is MSIX/GUI - bad headless.
- **Gotcha:** `lm` / symbol resolution hangs cdb over SSH via the msdl server. Set
  `$env:_NT_SYMBOL_PATH=''` (or a local cache) first, and wrap calls in a
  `Start-Job` + `Wait-Job -Timeout` so a stuck session can't hang the SSH call.
