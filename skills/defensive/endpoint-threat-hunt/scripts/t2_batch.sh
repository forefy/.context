#!/bin/sh
# T2 hunt batch - every elevated macOS check in ONE osascript admin prompt.
# Usage (interactive full-tier hunts):
#   osascript -e 'do shell script "sh <abs-path>/scripts/t2_batch.sh" with administrator privileges'
#   - launch as a tracked background process and poll for exit; the admin dialog
#     pops instantly but each `log show` takes minutes - do NOT run it foreground.
#   - results land in /tmp/hunt_t2/*.log - read them after the process exits.
# Custom time window: set WINDOW env (default 24h) or edit below.
# NOTE: the TCC query records "authorization denied" unless the calling terminal
# has Full Disk Access (root alone is not enough on macOS 26) - treat that as SKIP.

WINDOW="${WINDOW:-24h}"
OUT=/tmp/hunt_t2
mkdir -p "$OUT"
cd "$OUT"

# Failed authentication (brute force indicator) - triage rules: macos-checks.md 5.4
log show --last "$WINDOW" --info --style compact \
  --predicate 'eventMessage CONTAINS[c] "failed authentication" OR eventMessage CONTAINS[c] "authentication failed" OR eventMessage CONTAINS[c] "incorrect password"' \
  > auth_fail.log 2>&1

# SSH daemon events (zero lines = no SSH surface touched)
log show --last "$WINDOW" --info --style compact --predicate 'process == "sshd"' > sshd.log 2>&1

# XProtect / MRT (triage the noise: macos-checks.md 7.3)
log show --last "$WINDOW" --info --style compact \
  --predicate 'subsystem CONTAINS "xprotect" OR eventMessage CONTAINS "XProtect" OR process == "MRTDaemon" OR eventMessage CONTAINS "MalwareRemoval"' \
  > xprotect.log 2>&1

# TCC grants (needs FDA even as root on macOS 26)
sqlite3 "/Library/Application Support/com.apple.TCC/TCC.db" \
  "SELECT service, client, datetime(last_modified,'unixepoch') FROM access WHERE auth_value=2 AND service IN ('kTCCServiceSystemPolicyAllFiles','kTCCServiceMicrophone','kTCCServiceCamera','kTCCServiceScreenCapture','kTCCServiceSystemPolicyDesktopFolder','kTCCServiceSystemPolicyDocumentsFolder','kTCCServiceSystemPolicyDownloadsFolder') ORDER BY last_modified DESC LIMIT 40;" \
  > tcc.log 2>&1

# Root crontab + spool
{ crontab -l 2>&1; echo "---spool---"; ls -la /var/at/tabs/ 2>&1; cat /var/at/tabs/root 2>/dev/null; } > rootcron.log 2>&1

# Bulk code-sign verification: every LaunchDaemon binary + PrivilegedHelper tool
{
  for p in /Library/LaunchDaemons/*.plist; do
    bin=$(plutil -extract ProgramArguments.0 raw "$p" 2>/dev/null || plutil -extract Program raw "$p" 2>/dev/null)
    [ -z "$bin" ] && continue
    case "$bin" in /*) ;; *) bin="/Library/LaunchDaemons/$bin";; esac
    [ -f "$bin" ] || continue
    echo "$(basename "$p") :: $bin :: $(codesign --verify --deep --strict "$bin" 2>&1) :: $(codesign -d --verbose=2 "$bin" 2>&1 | grep TeamIdentifier | head -1)"
  done
  echo "--- PrivilegedHelperTools ---"
  for b in /Library/PrivilegedHelperTools/*; do
    [ -f "$b" ] || continue
    echo "$b :: $(codesign --verify --deep --strict "$b" 2>&1) :: $(codesign -d --verbose=2 "$b" 2>&1 | grep TeamIdentifier | head -1)"
  done
} > codesign_sweep.log 2>&1

echo DONE
