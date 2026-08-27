#!/bin/bash
# inspect-linux.sh <app-name-or-path> - one-shot triage of an installed/running
# Linux app. Runs ON the guest (push via rcs). Emits ELECTRON_ASAR= if found.
set -u
Q="$1"

echo "================ APP: $Q ================"
echo "--- package ownership ---"
if command -v dpkg >/dev/null; then dpkg -l 2>/dev/null | grep -i "$Q" | awk '{print "  "$2" "$3}' | head
elif command -v rpm >/dev/null; then rpm -qa 2>/dev/null | grep -i "$Q" | sed 's/^/  /' | head; fi
command -v flatpak >/dev/null && flatpak list 2>/dev/null | grep -i "$Q" | sed 's/^/  flatpak: /'
command -v snap >/dev/null && snap list 2>/dev/null | grep -i "$Q" | sed 's/^/  snap: /'

# resolve a binary path
BIN=$(command -v "$Q" 2>/dev/null); [ -z "$BIN" ] && BIN=$(ls -d /opt/*"$Q"*/ /usr/lib/*"$Q"* 2>/dev/null | head -1)
echo; echo "--- binary ---"; echo "  path: ${BIN:-<not resolved>}"
[ -f "$BIN" ] && file "$BIN" 2>/dev/null | sed 's/^/  /'

echo; echo "--- running processes ---"
ps -ef | grep -iF "$Q" | grep -v grep | awk '{printf "  %s ppid=%s %s\n",$2,$3,$8}' | head -12

echo; echo "--- listening sockets owned by it ---"
if command -v ss >/dev/null; then ss -tanp 2>/dev/null | grep -i "$Q" | sed 's/^/  /' | head; fi

echo; echo "--- systemd units / autostart ---"
systemctl list-unit-files 2>/dev/null | grep -i "$Q" | sed 's/^/  /' | head
ls ~/.config/autostart/ /etc/xdg/autostart/ 2>/dev/null | grep -i "$Q" | sed 's/^/  autostart: /'

echo; echo "--- loaded libs of first live pid (maps) ---"
PID=$(pgrep -f "$Q" 2>/dev/null | head -1)
[ -n "$PID" ] && awk '{print $6}' /proc/$PID/maps 2>/dev/null | grep -E '\.so' | sort -u | grep -vE '^/(usr/)?lib' | sed 's/^/  /' | head -15

echo; echo "--- bundled runtimes / electron ---"
BASE=$(dirname "${BIN:-/}")
find "$BASE" -maxdepth 3 -type f \( -name 'node' -o -name 'bun' -o -name '*.asar' \) 2>/dev/null | sed 's/^/  /' | head
ASAR=$(find "$BASE" -maxdepth 3 -name 'app.asar' 2>/dev/null | head -1)
[ -n "$ASAR" ] && echo "ELECTRON_ASAR=$ASAR"
