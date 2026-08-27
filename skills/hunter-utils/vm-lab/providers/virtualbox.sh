# providers/virtualbox.sh - Oracle VirtualBox (any host). VBoxManage is fully
# free and open - the most capable of the three providers. All four verbs native.
#   Host->guest net: NAT gateway is 10.0.2.2; for stable guest IPs prefer a
#   Host-Only adapter (vboxnet0, 192.168.56.0/24) or bridged.
#
# Verbs: prov_list prov_ip prov_start prov_stop prov_snapshot_*  (tag-based)

prov_list() { VBoxManage list vms 2>/dev/null; VBoxManage list runningvms 2>/dev/null | sed 's/^/running: /'; }

prov_ip() {  # prov_ip <tag> -> IPv4. Needs Guest Additions for guestproperty;
             # falls back to DHCP leases. (mDNS/ARP fallback handled by lib.sh.)
  local vm; vm=$(gp "$1" VMNAME)
  local ip
  ip=$(VBoxManage guestproperty get "$vm" "/VirtualBox/GuestInfo/Net/0/V4/IP" 2>/dev/null \
        | awk '/^Value:/{print $2}')
  [ -n "$ip" ] && [ "$ip" != "No" ] && { printf '%s' "$ip"; return; }
  # DHCP-lease fallback (host-only network): match by VM's NIC MAC
  local mac
  mac=$(VBoxManage showvminfo "$vm" --machinereadable 2>/dev/null \
        | sed -n 's/^macaddress1="\(.*\)"/\1/p' | tr 'A-F' 'a-f')
  [ -n "$mac" ] && grep -A3 -i "$mac" "$HOME/.config/VirtualBox/"*.leases 2>/dev/null \
        | grep -oE '([0-9]+\.){3}[0-9]+' | head -1
}

prov_start()  { VBoxManage startvm "$(gp "$1" VMNAME)" --type headless 2>/dev/null \
                  && echo "started headless (wait for sshd)"; }
prov_stop()   { VBoxManage controlvm "$(gp "$1" VMNAME)" acpipowerbutton 2>/dev/null \
                  || VBoxManage controlvm "$(gp "$1" VMNAME)" poweroff 2>/dev/null; }

prov_snapshot_list()    { VBoxManage snapshot "$(gp "$1" VMNAME)" list 2>/dev/null; }
prov_snapshot_take()    { VBoxManage snapshot "$(gp "$1" VMNAME)" take "$2" --live 2>/dev/null \
                            || VBoxManage snapshot "$(gp "$1" VMNAME)" take "$2"; }
prov_snapshot_restore() { VBoxManage controlvm "$(gp "$1" VMNAME)" poweroff 2>/dev/null
                          VBoxManage snapshot "$(gp "$1" VMNAME)" restore "$2"; }

# Truly-fresh guest (no SSH, no Additions): VirtualBox can type into the console
# headlessly with keyboardputstring - used by bootstrap/ to seed the SSH key.
prov_type() { VBoxManage controlvm "$(gp "$1" VMNAME)" keyboardputstring "$2"; }
