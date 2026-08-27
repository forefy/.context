#!/usr/bin/env bash
# inspect-app.sh <tag> <app-name-or-path> - one-command triage of an installed or
# running app on a guest: identity, signing, injectability, schemes, process tree,
# loaded modules, bundled runtimes. Auto-chains electron-triage when it detects an
# Electron app. Per-OS logic lives in tools/inspect-<os>.{sh,ps1}.
#   ./inspect-app.sh mac Claude
#   ./inspect-app.sh lin firefox
#   ./inspect-app.sh win Claude
set -uo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
. ./lib.sh

t="${1:?usage: inspect-app.sh <tag> <app-name-or-path>}"
app="${2:?missing app name/path}"
guest_exists "$t" || { echo "unknown guest tag: $t (have: $GUESTS)"; exit 1; }
reachable "$t"    || { echo "$t unreachable - ./ctl.sh $t up"; exit 1; }

os=$(gp "$t" OS)
case "$os" in
  macos)   insp=tools/inspect-macos.sh ;;
  linux)   insp=tools/inspect-linux.sh ;;
  windows) insp=tools/inspect-windows.ps1 ;;
  *) echo "unknown OS: $os"; exit 1 ;;
esac

out=$(rcs "$t" "$insp" "$app")
printf '%s\n' "$out"

# chain electron-triage if the inspector flagged an app.asar
asar=$(printf '%s\n' "$out" | sed -n 's/^ELECTRON_ASAR=//p' | head -1)
if [ -n "$asar" ]; then
  echo; echo ">>> Electron detected - running electron-triage on:"; echo "    $asar"; echo
  case "$os" in
    macos|linux) rcs "$t" tools/electron-triage.sh "$asar" ;;
    windows)
      echo "electron-triage is bash+python3; pull the asar and run it on the host:"
      echo "    source lib.sh && pull $t \"$asar\" /tmp/app.asar"
      echo "    bash tools/electron-triage.sh /tmp/app.asar   # needs python3 on host"
      ;;
  esac
fi
