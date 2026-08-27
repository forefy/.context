#!/bin/bash
# inspect-macos.sh <app-name-or-.app-path> - one-shot triage of an installed/running
# macOS app. Runs ON the guest (push via rcs). Prints an ELECTRON_ASAR= line the
# host dispatcher uses to chain electron-triage.
set -u
Q="$1"

# resolve to a .app bundle
if [ -d "$Q" ]; then P="$Q"
else
  P=$(ls -d /Applications/*"$Q"*.app "$HOME/Applications/"*"$Q"*.app 2>/dev/null | head -1)
  [ -z "$P" ] && P=$(mdfind "kMDItemContentType==com.apple.application-bundle" 2>/dev/null | grep -i "$Q" | head -1)
fi
[ -z "$P" ] || [ ! -d "$P" ] && { echo "inspect: app not found for: $Q"; exit 1; }
EXE="$P/Contents/MacOS/$(defaults read "$P/Contents/Info" CFBundleExecutable 2>/dev/null)"

echo "================ APP: $P ================"
echo "--- identity ---"
echo "  BundleID : $(defaults read "$P/Contents/Info" CFBundleIdentifier 2>/dev/null)"
echo "  Version  : $(defaults read "$P/Contents/Info" CFBundleShortVersionString 2>/dev/null) ($(defaults read "$P/Contents/Info" CFBundleVersion 2>/dev/null))"
echo "  Exec     : $EXE"

echo; echo "--- code signing / notarization ---"
codesign -dv --verbose=4 "$P" 2>&1 | grep -iE 'Identifier=|TeamIdentifier=|Authority=|flags=|format=' | sed 's/^/  /'
echo "  Gatekeeper: $(spctl -a -vv -t exec "$P" 2>&1 | tr '\n' ' ')"

echo; echo "--- hardened runtime / injectability (does the skill's Frida path work?) ---"
FLAGS=$(codesign -dv --verbose=4 "$P" 2>&1 | grep -oE 'flags=0x[0-9a-f]+\([^)]*\)')
ENT=$(codesign -d --entitlements - --xml "$P" 2>/dev/null)
hr=no;  echo "$FLAGS" | grep -q runtime && hr=yes
dlv=no; printf '%s' "$ENT" | grep -q disable-library-validation && dlv=yes
dye=no; printf '%s' "$ENT" | grep -q allow-dyld-environment-variables && dye=yes
gta=no; printf '%s' "$ENT" | grep -q get-task-allow && gta=yes
echo "  hardened-runtime=$hr  disable-lib-validation=$dlv  allow-dyld-env=$dye  get-task-allow=$gta"
if [ "$hr" = yes ] && [ "$dlv" = no ] && [ "$gta" = no ]; then
  echo "  => Frida/dylib injection BLOCKED (hardened + LV, no get-task-allow). Need SIP off or re-sign; use static + observational."
else
  echo "  => Frida/dylib injection likely POSSIBLE (weak hardening) - try the skill's Frida recipe."
fi

echo; echo "--- entitlements (keys) ---"
printf '%s' "$ENT" | grep -oE '<key>[^<]+</key>' | sed 's/<[^>]*>//g' | sed 's/^/  /' | head -40

echo; echo "--- registered URL schemes (deep-link surface) ---"
plutil -extract CFBundleURLTypes xml1 -o - "$P/Contents/Info.plist" 2>/dev/null \
  | grep -A2 CFBundleURLSchemes | grep '<string>' \
  | sed -E 's|.*<string>(.*)</string>.*|  \1|' | sort -u

echo; echo "--- running processes ---"
ps -axo pid,ppid,user,command | grep -iF "$P" | grep -v grep | sed 's/^/  /' | head -12

echo; echo "--- third-party linked dylibs (non-system) of main exec ---"
otool -L "$EXE" 2>/dev/null | awk 'NR>1{print $1}' | grep -vE '^\s*(/usr/lib|/System)' | sed 's/^/  /' | head -20

echo; echo "--- bundled runtimes / framework ---"
[ -d "$P/Contents/Frameworks/Electron Framework.framework" ] && echo "  Electron detected"
ls "$P/Contents/Frameworks" 2>/dev/null | grep -iE 'electron|node|bun|cef' | sed 's/^/  /'
find "$P/Contents" -maxdepth 4 -type f \( -name 'node' -o -name 'bun' \) 2>/dev/null | sed 's/^/  bundled: /' | head

# signal for the dispatcher to chain electron-triage
ASAR="$P/Contents/Resources/app.asar"
[ -f "$ASAR" ] && echo "ELECTRON_ASAR=$ASAR"
