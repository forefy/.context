# providers/vmware.sh - VMware Fusion (macOS) / Workstation (Win/Linux).
# Both are now FREE for personal use (Broadcom, 2024+). Driven by `vmrun` (ships
# with the app). VMNAME here is the full path to the guest's .vmx file.
#   Fusion vmrun:      /Applications/VMware Fusion.app/Contents/Library/vmrun
#   Workstation vmrun: on PATH after install
#   Host->guest net:   NAT gateway is .2 of the vmnet subnet.
#
# Verbs: prov_list prov_ip prov_start prov_stop prov_snapshot_*  (tag-based)

# Resolve vmrun (PATH, or Fusion's bundled copy).
_vmrun() {
  if command -v vmrun >/dev/null 2>&1; then vmrun "$@"
  elif [ -x "/Applications/VMware Fusion.app/Contents/Library/vmrun" ]; then
    "/Applications/VMware Fusion.app/Contents/Library/vmrun" "$@"
  else echo "vmrun not found (install VMware Fusion/Workstation)" >&2; return 127; fi
}

prov_list() { _vmrun list; }

prov_ip() {  # needs VMware Tools in the guest; lib.sh handles mDNS/ARP fallback
  local vmx; vmx=$(gp "$1" VMNAME)
  _vmrun getGuestIPAddress "$vmx" -wait 2>/dev/null | grep -E '^([0-9]+\.){3}[0-9]+$'
}

prov_start()  { _vmrun start "$(gp "$1" VMNAME)" nogui 2>/dev/null && echo "started (wait for sshd)"; }
prov_stop()   { _vmrun stop  "$(gp "$1" VMNAME)" soft 2>/dev/null \
                  || _vmrun stop "$(gp "$1" VMNAME)" hard; }

prov_snapshot_list()    { _vmrun listSnapshots      "$(gp "$1" VMNAME)"; }
prov_snapshot_take()    { _vmrun snapshot           "$(gp "$1" VMNAME)" "$2"; }
prov_snapshot_restore() { _vmrun revertToSnapshot   "$(gp "$1" VMNAME)" "$2"; }
