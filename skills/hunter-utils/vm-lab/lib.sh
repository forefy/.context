# lib.sh - shared core for vm-lab. Source this, never execute it.
#   source lib.sh                 # loads config.local.env (or config.example.env) + helpers
# Portable across bash (incl. macOS's bash 3.2) AND zsh: no associative arrays,
# and gp() uses eval-based indirection instead of the bash-only ${!v}.
# NOTE: the config is sourced as shell - only use configs you trust.

# ---- locate & load config -------------------------------------------------
# Resolve this file's dir when sourced, under bash OR zsh (eval defers the
# zsh-only ${(%):-%x} so bash doesn't choke parsing it).
if [ -n "${BASH_SOURCE:-}" ]; then _vmdl_self="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION:-}" ]; then eval '_vmdl_self="${(%):-%x}"'
else _vmdl_self="$0"; fi
VMDL_DIR="${VMDL_DIR:-$(cd "$(dirname "$_vmdl_self")" && pwd)}"
if   [ -f "$VMDL_DIR/config.local.env" ]; then VMDL_CFG="$VMDL_DIR/config.local.env"
elif [ -f "$VMDL_DIR/config.example.env" ]; then VMDL_CFG="$VMDL_DIR/config.example.env"
else echo "lib.sh: no config found (copy config.example.env -> config.local.env)" >&2; fi
# shellcheck disable=SC1090
[ -n "${VMDL_CFG:-}" ] && . "$VMDL_CFG"

# ---- guest registry accessors --------------------------------------------
# Each guest <tag> is defined by GUEST_<tag>_<PROP> vars in the config.
# GUESTS is the space-separated list of tags. Props: PROVIDER OS ARCH VMNAME
# IP USER AUTH KEY PW HOSTNAME MAC.
gp() {  # gp <tag> <PROP> -> value (empty if unset). eval-based indirection so it
        # works in BOTH bash (${!v}) and zsh (${(P)v}) - macOS default is zsh.
  local v="GUEST_${1}_${2}"; eval "printf '%s' \"\${$v-}\""
}
# Emit one tag per line (zsh doesn't word-split unquoted $GUESTS; tr does it for us).
guest_list() { printf '%s' "${GUESTS:-}" | tr ' \t' '\n\n' | grep -v '^$'; }

guest_exists() {
  local g; while IFS= read -r g; do [ "$g" = "$1" ] && return 0; done <<EOF
$(guest_list)
EOF
  return 1
}

# ---- SSH command builder (hypervisor-agnostic substrate) ------------------
# SSH_OPTS defaults dodge a host ssh-agent (1Password etc.) and skip host-key
# churn on disposable, re-snapshotted VMs. Override in config if you need to.
: "${SSH_OPTS:=-o IdentitiesOnly=yes -o IdentityAgent=none -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR -o ConnectTimeout=10}"

# ssh_cmd <tag> -> prints the ssh invocation string for eval.
# Uses key auth when AUTH=key; falls back to sshpass for AUTH=password.
ssh_cmd() {
  local t="$1" ip user auth key pw
  ip=$(gp "$t" IP); user=$(gp "$t" USER); auth=$(gp "$t" AUTH)
  key=$(gp "$t" KEY); pw=$(gp "$t" PW)
  [ -z "$ip" ] && ip=$(discover_ip "$t")   # lazy discovery if IP not pinned
  if [ "$auth" = "password" ]; then
    if command -v sshpass >/dev/null 2>&1; then
      printf 'sshpass -p %q ssh %s %s@%s' "$pw" "$SSH_OPTS" "$user" "$ip"
    else
      echo "ssh_cmd: AUTH=password needs sshpass (brew install sshpass) - or switch to key auth" >&2
      printf 'ssh %s %s@%s' "$SSH_OPTS" "$user" "$ip"
    fi
  else
    printf 'ssh %s -i %s %s@%s' "$SSH_OPTS" "$key" "$user" "$ip"
  fi
}

# rc <tag> <remote-cmd...> - run a command on a guest, OS-aware.
#   macOS/Linux: passed to the login shell as-is.
#   Windows:     wrapped so PowerShell/cmd one-liners behave (see run_win).
rc() {
  local t="$1"; shift
  case "$(gp "$t" OS)" in
    windows) run_win "$t" "$*" ;;
    *)       eval "$(ssh_cmd "$t") '$*'" ;;
  esac
}

# run_win <tag> <powershell> - send PowerShell as UTF-16LE base64 to dodge
# quoting hell + set ProgressPreference (CLIXML noise). For structured output,
# write-to-file-then-read on the guest; see toolkits/windows.md.
run_win() {
  local t="$1" ps="$2" b64
  ps="\$ProgressPreference='SilentlyContinue'; $ps"
  b64=$(printf '%s' "$ps" | iconv -f UTF-8 -t UTF-16LE | base64 | tr -d '\n')
  eval "$(ssh_cmd "$t") \"powershell -NoProfile -EncodedCommand $b64\"" 2>&1 \
    | grep -vE '^#< CLIXML|<Objs '
}

# sudo helper for macOS/Linux guests: echo pw | sudo -S ...
rc_sudo() {
  local t="$1"; shift
  local pw; pw=$(gp "$t" PW)
  eval "$(ssh_cmd "$t") 'echo $pw | sudo -S $*'"
}

reachable() { rc "$1" 'echo ok' >/dev/null 2>&1; }

# wait_ssh <tag> [timeout_s] - block until the guest answers SSH (after a boot).
wait_ssh() {
  local t="$1" max="${2:-90}" i=0
  printf 'waiting for %s ssh' "$t" >&2
  while [ "$i" -lt "$max" ]; do
    reachable "$t" && { echo " - up" >&2; return 0; }
    printf '.' >&2; sleep 3; i=$((i+3))
  done
  echo " - TIMEOUT after ${max}s" >&2; return 1
}

# ---- file transfer (scp over the same opts/auth) --------------------------
# scp works with OpenSSH on all three guest OSes. Windows remote paths use
# forward slashes under sshd, e.g. C:/Users/user/o.txt.
scp_cmd() {  # scp_cmd <tag> -> prints the scp base command
  local t="$1" user auth key pw ip
  ip=$(gp "$t" IP); [ -z "$ip" ] && ip=$(discover_ip "$t")
  user=$(gp "$t" USER); auth=$(gp "$t" AUTH); key=$(gp "$t" KEY); pw=$(gp "$t" PW)
  if [ "$auth" = "password" ] && command -v sshpass >/dev/null 2>&1; then
    printf 'sshpass -p %q scp %s' "$pw" "$SSH_OPTS"
  else
    printf 'scp %s -i %s' "$SSH_OPTS" "$key"
  fi
}
_hostspec() { local t="$1"; local ip; ip=$(gp "$t" IP); [ -z "$ip" ] && ip=$(discover_ip "$t"); printf '%s@%s' "$(gp "$t" USER)" "$ip"; }
push() {  # push <tag> <local-path> <remote-path>
  local t="$1"; eval "$(scp_cmd "$t") -r '$2' '$(_hostspec "$t"):$3'"; }
pull() {  # pull <tag> <remote-path> <local-path>
  local t="$1"; eval "$(scp_cmd "$t") -r '$(_hostspec "$t"):$2' '$3'"; }

# rcs <tag> <local-script> [args...] - push a script to the guest, run it, clean up.
# The robust alternative to `rc <tag> 'complex '\''quoted'\'' cmd'` (avoids the
# single-quote caveat). Interpreter chosen by OS: bash for mac/linux, powershell
# -File for windows (.ps1). Needs the guest to have that interpreter (+ python3 for
# the electron/asar tooling). Returns the script's exit output on stdout.
rcs() {
  local t="$1" script="$2"; shift 2
  [ -f "$script" ] || { echo "rcs: no such script: $script" >&2; return 2; }
  local os base rp a args=""; os=$(gp "$t" OS); base="_vmdl_$(basename "$script")"
  if [ "$os" = windows ]; then
    for a in "$@"; do args="$args \"$a\""; done          # double-quote for powershell
    rp="C:/Windows/Temp/$base"
    push "$t" "$script" "$rp" >/dev/null 2>&1 || { echo "rcs: push failed" >&2; return 1; }
    eval "$(ssh_cmd "$t") \"powershell -NoProfile -ExecutionPolicy Bypass -File $rp$args\"" 2>&1 \
      | grep -vE '^#< CLIXML|<Objs '
    # cleanup via PowerShell Remove-Item - `cmd /c del C:/...` fails (cmd reads / as a switch)
    eval "$(ssh_cmd "$t") \"powershell -NoProfile -Command Remove-Item -Force -LiteralPath '$rp' -EA SilentlyContinue\"" >/dev/null 2>&1
  else
    for a in "$@"; do args="$args '${a//\'/\'\\\'\'}'"; done  # single-quote, escape embedded '
    rp="/tmp/$base"
    push "$t" "$script" "$rp" >/dev/null 2>&1 || { echo "rcs: push failed" >&2; return 1; }
    eval "$(ssh_cmd "$t") 'bash \"$rp\"$args; rm -f \"$rp\"'"
  fi
}

# tun <tag> <ssh -L/-R forward args...> - open a port forward (foreground, Ctrl-C
# to close). e.g. tun mac -L 8080:127.0.0.1:8080   (reach guest:8080 as host:8080)
tun() {
  local t="$1"; shift
  eval "$(ssh_cmd "$t") -N $*"
}

# ---- provider dispatch ----------------------------------------------------
# Loads providers/<PROVIDER>.sh for a guest and calls prov_<verb>.
prov() {  # prov <tag> <verb> [args...]
  local t="$1" verb="$2"; shift 2
  local prv; prv=$(gp "$t" PROVIDER)
  local f="$VMDL_DIR/providers/${prv}.sh"
  [ -f "$f" ] || { echo "prov: unknown provider '$prv' (providers/${prv}.sh missing)" >&2; return 2; }
  # shellcheck disable=SC1090
  . "$f"
  "prov_${verb}" "$t" "$@"
}

# discover_ip <tag> - provider-native first, then generic fallbacks.
discover_ip() {
  local t="$1" ip
  ip=$(prov "$t" ip 2>/dev/null); [ -n "$ip" ] && { printf '%s' "$ip"; return; }
  # shellcheck disable=SC1090
  . "$VMDL_DIR/providers/common.sh"
  ip=$(ip_via_mdns "$(gp "$t" HOSTNAME)" 2>/dev/null); [ -n "$ip" ] && { printf '%s' "$ip"; return; }
  ip=$(ip_via_arp  "$(gp "$t" MAC)"      2>/dev/null); [ -n "$ip" ] && { printf '%s' "$ip"; return; }
  return 1
}
