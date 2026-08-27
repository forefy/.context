# providers/parallels.sh - Parallels Desktop (macOS host, Apple Silicon).
# Standard edition ONLY needs `prlctl list` (free). start/stop/exec/snapshot are
# Pro/Business-gated, so we DON'T depend on them: power via `open` on the bundle,
# snapshots deferred to the GUI. If you have Pro, the commented prlctl paths work.
#
# Verbs: prov_list  prov_ip  prov_start  prov_stop  prov_snapshot_*  (tag-based)

prov_list() {  # list all VMs + state (works on standard edition)
  prlctl list -a -o name,status,uuid 2>/dev/null
}

prov_ip() {  # prov_ip <tag> -> IPv4 (prlctl list -f is free)
  local vm; vm=$(gp "$1" VMNAME)
  prlctl list -f 2>/dev/null | awk -v n="$vm" '
    $0 ~ n { for(i=1;i<=NF;i++) if($i ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/){print $i; exit} }'
}

prov_start() {  # standard edition: prlctl start is gated -> boot the bundle
  local vm; vm=$(gp "$1" VMNAME)
  # Pro: prlctl start "$vm" ; standard: open the .pvm/.macvm bundle
  local b
  b=$(ls -d "$HOME/Parallels/$vm."* 2>/dev/null | head -1)
  if [ -n "$b" ]; then open "$b"; echo "booting $vm via $b (wait ~30-60s for sshd)"
  else prlctl start "$vm" 2>/dev/null || echo "start gated; open the VM from the Parallels GUI"; fi
}

prov_stop() {  # Pro: prlctl stop. Standard edition: prlctl stop is gated, so shut
               # the guest down gracefully from the inside over SSH (the free path).
  local t="$1" vm os; vm=$(gp "$t" VMNAME); os=$(gp "$t" OS)
  if prlctl stop "$vm" 2>/dev/null; then return; fi
  if ! reachable "$t"; then
    echo "prlctl stop gated and $t unreachable - power off from the Parallels GUI"; return; fi
  echo "prlctl stop gated (standard edition) - shutting down $t from inside over SSH…"
  case "$os" in
    windows) rc      "$t" 'shutdown /s /t 0 /f' >/dev/null 2>&1 ;;
    *)       rc_sudo "$t" 'shutdown -h now'     >/dev/null 2>&1 ;;
  esac
  # the shutdown drops the SSH connection, so a non-zero return here is expected
  echo "  shutdown issued - VM will power off shortly."
}

prov_snapshot_list()    { prlctl snapshot-list "$(gp "$1" VMNAME)" 2>/dev/null \
    || echo "snapshots are Pro-gated on standard edition - use the Parallels GUI (⌘S)"; }
prov_snapshot_take()    { prlctl snapshot "$(gp "$1" VMNAME)" -n "$2" 2>/dev/null \
    || echo "snapshot create is Pro-gated - Parallels GUI: Actions > Take Snapshot"; }
prov_snapshot_restore() { prlctl snapshot-switch "$(gp "$1" VMNAME)" -i "$2" 2>/dev/null \
    || echo "snapshot restore is Pro-gated - Parallels GUI: Manage Snapshots"; }
