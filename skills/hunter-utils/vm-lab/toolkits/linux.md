# Linux guest toolkit (x64 on AMD/Intel, or arm64 on Apple Silicon)

Linux is the easiest guest: SSH is one `apt`/`dnf` away, package managers install
everything, and (unlike macOS SIP / Windows PMU limits) most tracing works in a VM
- with two caveats noted below. Commands assume `rc lin '<cmd>'` and `rc_sudo lin '<cmd>'`.

## Run-commands-over-SSH gotchas
- Dead simple vs. the other two: one login shell, real `timeout`, real signals.
- Non-interactive sudo: `rc_sudo lin '<cmd>'` (echoes `$PW | sudo -S`), or set up
  `NOPASSWD` for the lab user. Passwordless key auth is the norm here.
- Bound a live capture with `timeout 5 <cmd>` (present on all distros) - no macOS-style dance.

## One-time setup (per distro family)
```bash
# Debian/Ubuntu:
sudo apt-get update && sudo apt-get install -y \
  strace ltrace gdb lsof tcpdump linux-perf bpfcc-tools bpftrace \
  auditd sysstat htop
# Fedora/RHEL:
sudo dnf install -y strace ltrace gdb lsof tcpdump perf bcc-tools bpftrace audit sysstat htop
# Arch:
sudo pacman -S --noconfirm strace ltrace gdb lsof tcpdump perf bcc bpftrace audit sysstat htop
```
`perf` package name is `linux-perf` (Debian) / `perf` (Fedora) and must match the
running kernel version; in a minimal cloud image you may need `linux-tools-$(uname -r)`.

## Task → tool matrix
| Task | Tool |
|------|------|
| Process tree + cmdline | `ps -ef --forest` · `pstree -ap` · `cat /proc/<pid>/cmdline` |
| Live exec/fork events | `bpftrace -e 'tracepoint:sched:sched_process_exec{...}'` · `execsnoop-bpfcc` · auditd `execve` |
| File activity | `opensnoop-bpfcc` · `strace -f -e trace=file -p <pid>` · `fatrace` |
| Socket ↔ process | `ss -tanp` (state+pid) · `lsof -nP -iTCP -sTCP:ESTABLISHED` |
| Byte throughput | `nethogs` (per-proc) · `ss -i` · `/proc/net/dev` |
| Packet capture | `sudo tcpdump -i any -w x.pcap` |
| Loaded libs (live proc) | `cat /proc/<pid>/maps` · `ldd <bin>` · `lsof -p <pid>` |
| Symbols / imports | `nm -D` · `readelf -d` · `objdump -T` |
| Signature / integrity | `debsums` / `rpm -V` · `sha256sum` (no code-signing like mac/win) |
| Persistence / autostart | `systemctl list-unit-files --state=enabled` · `systemd-analyze` · crontab · `~/.config/autostart` |
| File locks / open handles | `lsof <path>` · `fuser -v <path>` |
| RAM/CPU per process | `top`/`htop` · `/proc/<pid>/status` · `pidstat 1` |
| CPU stacks / profiling | `perf record -g -p <pid>` → `perf report` (see VM note) · `pstack`/`gstack` |
| Syscall trace | `strace -f -p <pid>` · `ltrace` (library calls) |
| Kernel/event tracing | `bpftrace` · `ftrace` (`/sys/kernel/tracing`) · `auditctl` |
| Memory dump | `gcore <pid>` · `/proc/<pid>/mem` via gdb |
| Dynamic instrumentation | `gdb -p <pid>` · Frida (`pip install frida-tools`; no SIP, so system bins hookable as root) |

## VM-specific limitations
- **`perf` hardware counters** (cycles, cache-misses, PMU events) are usually not
  virtualized - `perf stat` reports `<not supported>` for hardware events. Software
  events (`task-clock`, `context-switches`, `page-faults`) and `perf record`
  call-graph sampling via software clock (`-e cpu-clock`) still work. Enable guest
  PMU passthrough if your hypervisor supports it (VMware `vpmc`, KVM `-cpu host`).
- **eBPF / bpftrace** need a kernel with BTF (`CONFIG_DEBUG_INFO_BTF`) and, on some
  distros, `sudo`. Ubuntu 20.04+ / Fedora ship it. If `bpftrace` errors on BTF, use
  `strace`/`auditd`/`ftrace` as the portable fallback.
- Running as **root inside the guest** removes the usual ptrace-scope limits; on a
  non-root setup you may need `sudo sysctl kernel.yama.ptrace_scope=0` to attach.
