# providers/common.sh - hypervisor-agnostic IP-discovery fallbacks.
# Sourced by lib.sh's discover_ip() when a provider can't answer natively.
# These need no paid tooling and work regardless of hypervisor.

# ip_via_mdns <hostname.local> - resolve a guest by its Bonjour/Avahi name.
# Works when the guest advertises mDNS (macOS always; Linux w/ avahi; Windows w/ Bonjour).
ip_via_mdns() {
  local host="$1"; [ -z "$host" ] && return 1
  # dns-sd (macOS) or getent/ping fallback
  if command -v dscacheutil >/dev/null 2>&1; then
    dscacheutil -q host -a name "$host" 2>/dev/null | awk '/^ip_address:/{print $2; exit}'
  elif command -v getent >/dev/null 2>&1; then
    getent hosts "$host" 2>/dev/null | awk '{print $1; exit}'
  else
    ping -c1 -t1 "$host" 2>/dev/null | sed -n 's/.*(\([0-9.]*\)).*/\1/p' | head -1
  fi
}

# norm_mac <mac> - canonical form: lowercase, zero-padded octets, no separators.
# Needed because `arp -an` prints octets WITHOUT leading zeros (a:1b:3), while a
# configured MAC has them (0a:1b:03) - a plain strip-separators compare never matches.
norm_mac() {
  local o
  printf '%s' "$1" | tr 'A-F' 'a-f' | tr ':-' '\n\n' | while read -r o || [ -n "$o" ]; do
    [ -n "$o" ] && printf '%02x' "0x$o" 2>/dev/null   # || [ -n "$o" ]: read the last, newline-less octet
  done
}

# ip_via_arp <mac> - find a guest's IPv4 by its NIC MAC on the local ARP table.
# Pre-warm the table with arp_sweep first if the guest isn't cached yet.
ip_via_arp() {
  local mac="$1"; [ -z "$mac" ] && return 1
  local norm; norm=$(norm_mac "$mac")
  arp -an 2>/dev/null | while read -r line; do
    local m ip
    ip=$(printf '%s' "$line" | sed -n 's/.*(\([0-9.]*\)).*/\1/p')
    m=$(printf '%s' "$line" | grep -oE '([0-9a-fA-F]{1,2}:){5}[0-9a-fA-F]{1,2}')
    m=$(norm_mac "$m")
    [ -n "$m" ] && [ "$m" = "$norm" ] && { printf '%s' "$ip"; break; }
  done
}

# arp_sweep <cidr-ish base, e.g. 192.168.56> - populate ARP by pinging .1-254.
# Cheap way to make ip_via_arp find a freshly-booted guest. Backgrounded pings.
arp_sweep() {
  local base="$1"; [ -z "$base" ] && return 1
  local i
  for i in $(seq 1 254); do ping -c1 -t1 "$base.$i" >/dev/null 2>&1 & done
  wait 2>/dev/null
}
