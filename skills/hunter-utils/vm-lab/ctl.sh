#!/usr/bin/env bash
# ctl.sh - control a guest through its provider (list/ip/power/snapshot), the four
# hypervisor verbs. Everything else you do over SSH with rc/rc_sudo (see lib.sh).
#   ./ctl.sh mac up            # power on (provider-native, free path)
#   ./ctl.sh mac down          # graceful power off
#   ./ctl.sh mac ip            # discover IP (provider -> mDNS -> ARP)
#   ./ctl.sh mac ssh           # print the ssh command (eval to connect)
#   ./ctl.sh mac snap <name>   # take snapshot        (Parallels std: prints GUI hint)
#   ./ctl.sh mac restore <nm>  # restore snapshot
#   ./ctl.sh mac snaps         # list snapshots
#   ./ctl.sh <tag> vms         # list all VMs the provider knows
set -uo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
. ./lib.sh

# Host preflight: `ctl.sh doctor` - no tag needed.
if [ "${1:-}" = "doctor" ]; then
  echo "== host preflight =="
  for c in ssh scp iconv base64 sshpass; do
    command -v "$c" >/dev/null 2>&1 && echo "  OK   $c" || echo "  MISS $c $([ "$c" = sshpass ] && echo '(only needed for AUTH=password)')"
  done
  echo "== providers detected =="
  command -v prlctl     >/dev/null 2>&1 && echo "  OK   parallels  (prlctl)"      || echo "  --   parallels  (prlctl not found)"
  command -v VBoxManage >/dev/null 2>&1 && echo "  OK   virtualbox (VBoxManage)"  || echo "  --   virtualbox (VBoxManage not found)"
  { command -v vmrun >/dev/null 2>&1 || [ -x "/Applications/VMware Fusion.app/Contents/Library/vmrun" ]; } \
       && echo "  OK   vmware     (vmrun)" || echo "  --   vmware     (vmrun not found)"
  echo "== configured guests =="; for g in $(guest_list); do
    echo "  $g -> $(gp "$g" OS)/$(gp "$g" ARCH) via $(gp "$g" PROVIDER) @ ${g}=$(gp "$g" IP)"; done
  exit 0
fi

t="${1:?usage: ctl.sh doctor | ctl.sh <tag> <up|down|ip|ssh|push|pull|tunnel|snap|restore|reset|snaps|vms>}"
verb="${2:?missing verb}"; shift 2 || true
guest_exists "$t" || { echo "unknown guest tag: $t (have: $GUESTS)"; exit 1; }

case "$verb" in
  up|start)    prov "$t" start; wait_ssh "$t" "${1:-90}" ;;
  down|stop)   prov "$t" stop ;;
  ip)          discover_ip "$t" || echo "(no IP - is it booted? try ./ctl.sh $t up)" ;;
  ssh)         ssh_cmd "$t"; echo ;;
  push)        push "$t" "${1:?local path}" "${2:?remote path}" ;;
  pull)        pull "$t" "${1:?remote path}" "${2:?local path}" ;;
  tunnel|tun)  tun "$t" "$@" ;;
  snap)        prov "$t" snapshot_take "${1:?snapshot name}" ;;
  restore)     prov "$t" snapshot_restore "${1:?snapshot name/id}" ;;
  reset)       # restore the known-clean snapshot for this guest (RESET_SNAPSHOT)
               s="${1:-$(gp "$t" RESET_SNAPSHOT)}"
               [ -z "$s" ] && { echo "no snapshot given and GUEST_${t}_RESET_SNAPSHOT unset"; exit 1; }
               echo "restoring $t -> snapshot '$s'"; prov "$t" snapshot_restore "$s" ;;
  snaps)       prov "$t" snapshot_list ;;
  vms)         prov "$t" list ;;
  *) echo "unknown verb: $verb"; exit 1 ;;
esac
