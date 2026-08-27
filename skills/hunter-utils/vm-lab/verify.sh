#!/usr/bin/env bash
# verify.sh - prove the toolkit is present + callable on each guest, per OS/arch,
# with an install hint for anything missing. Hypervisor-agnostic (runs over SSH).
#   ./verify.sh            # every guest in $GUESTS
#   ./verify.sh mac        # one guest by tag
set -uo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
. ./lib.sh

hdr() { echo "=========== $1  [$(gp "$1" OS)/$(gp "$1" ARCH) via $(gp "$1" PROVIDER)] @ $(gp "$1" USER)@$(gp "$1" IP) ==========="; }

verify_macos() {
  local t="$1"
  rc "$t" 'bash -s' <<'EOF'
chk(){ command -v "$1" >/dev/null 2>&1 && printf "  OK   %-11s %s\n" "$1" "$2" || printf "  MISS %-11s %s  <-- %s\n" "$1" "$2" "$3"; }
xcode-select -p >/dev/null 2>&1 && CLT=1 || CLT=0
cchk(){ [ "$CLT" = 1 ] && printf "  OK   %-11s %s\n" "$1" "$2" || printf "  MISS %-11s %s  <-- xcode-select --install (GUI)\n" "$1" "$2"; }
echo "[proc] "; chk ps "tree+cmdline" base
echo "[event]"; chk eslogger "ESF exec/fork/file" "built-in 13+"; chk fs_usage "file activity" base
echo "[net]  "; chk lsof "sock<->proc" base; chk nettop "byte flow" base; chk tcpdump "pcap" base
echo "[bin]  "; chk vmmap "images" base; chk codesign sign base; chk spctl gatekeeper base; cchk otool "dylib deps"; cchk nm symbols
echo "[mem]  "; chk footprint "per-proc mem" base; chk sample "user stacks" base; chk spindump "full stacks" base
echo "[log]  "; chk log "unified log" base
EOF
}

verify_linux() {
  local t="$1"
  rc "$t" 'bash -s' <<'EOF'
chk(){ command -v "$1" >/dev/null 2>&1 && printf "  OK   %-11s %s\n" "$1" "$2" || printf "  MISS %-11s %s  <-- %s\n" "$1" "$2" "$3"; }
PM=apt; command -v dnf >/dev/null && PM=dnf; command -v pacman >/dev/null && PM=pacman
echo "[proc] "; chk ps tree base; chk pstree tree "$PM install psmisc"
echo "[event]"; chk strace syscalls "$PM install strace"; chk bpftrace ebpf "$PM install bpftrace"; chk auditctl audit "$PM install auditd"
echo "[net]  "; chk ss "sock<->proc" base; chk lsof handles "$PM install lsof"; chk tcpdump pcap "$PM install tcpdump"
echo "[bin]  "; chk readelf elf binutils; chk nm symbols binutils; chk ldd libs base
echo "[mem]  "; chk gcore "core dump" gdb; chk gdb debugger "$PM install gdb"
echo "[prof] "; chk perf "profiling" "$PM install linux-perf (VM: sw events only)"
EOF
}

verify_windows() {
  local t="$1"
  run_win "$t" '
function chk($n,$d,$h){ if(Get-Command $n -EA SilentlyContinue){"  OK   {0,-24} {1}" -f $n,$d}else{"  MISS {0,-24} {1}  <-- {2}" -f $n,$d,$h} }
"[proc] "; chk Get-CimInstance "Win32_Process tree" native; chk tasklist "quick list" native
"[net]  "; chk Get-NetTCPConnection "sock<->proc" native; chk netstat "netstat -ano" native; chk pktmon "pcap" native
"[bin]  "; chk Get-Process "loaded DLLs" native; chk Get-AuthenticodeSignature sign native
"[mem]  "; chk Get-Counter counters native
"[log]  "; chk Get-WinEvent "event log" native; chk logman "ETW (wpr fails in-VM 0x80070032)" native; chk driverquery drivers native
"[persist]"; chk Get-ScheduledTask tasks native
$dir="C:\Tools\Sysinternals"
foreach($x in "autorunsc64.exe","handle64.exe","sigcheck64.exe","procdump64.exe"){
  if(Test-Path "$dir\$x"){"  OK   {0,-24} sysinternals" -f $x}
  else{"  MISS {0,-24} <-- iwr https://live.sysinternals.com/$x -OutFile $dir\$x" -f $x}}
'
}

verify_one() {
  local t="$1"
  guest_exists "$t" || { echo "unknown guest tag: $t (have: $(echo $GUESTS))"; return 1; }
  hdr "$t"
  if ! reachable "$t"; then
    echo "  UNREACHABLE - try: ./ctl.sh $t up   (or run bootstrap/$(gp "$t" OS).* )"; echo; return; fi
  case "$(gp "$t" OS)" in
    macos)   verify_macos   "$t" ;;
    linux)   verify_linux   "$t" ;;
    windows) verify_windows "$t" ;;
    *) echo "  unknown OS '$(gp "$t" OS)'" ;;
  esac
  echo
}

if [ $# -ge 1 ]; then verify_one "$1"; else for t in $(guest_list); do verify_one "$t"; done; fi
