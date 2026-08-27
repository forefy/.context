#!/bin/bash
# electron-triage.sh <app.asar | .app | install-dir> - map an Electron app's
# renderer<->main attack surface without node. Self-contained (writes the asar
# parser to /tmp). Needs python3 on the guest. Runs ON the guest (push via rcs).
#
# Reports: package.json entry, per-bundle IPC map (exposeInMainWorld / .handle /
# openExternal / openPath / child_process / custom schemes), webPreferences
# security flags, and the exposeInMainWorld bridge names.  Minified-JS proof:
# handlers compile to <alias>.handle("chan") so `.handle("` catches them; and
# true=>!0 false=>!1 for the webPreferences flags.
set -u
A="$1"
# resolve .app / dir -> app.asar
[ -d "$A" ] && [ -f "$A/Contents/Resources/app.asar" ] && A="$A/Contents/Resources/app.asar"
[ -d "$A" ] && [ -f "$A/resources/app.asar" ] && A="$A/resources/app.asar"   # win/linux
[ -f "$A" ] || { echo "electron-triage: no app.asar at: $1"; exit 1; }
command -v python3 >/dev/null || { echo "electron-triage: needs python3 on the guest"; exit 1; }

PY=/tmp/_vmdl_asar.py
cat > "$PY" <<'PYEOF'
import sys, struct, json
def load(p):
    with open(p,'rb') as f:
        struct.unpack('<I',f.read(4)); hs=struct.unpack('<I',f.read(4))[0]
        struct.unpack('<I',f.read(4)); jl=struct.unpack('<I',f.read(4))[0]
        h=json.loads(f.read(jl).decode('utf-8','replace'))
    return h, 8+hs
def walk(n,pre=''):
    for k,m in n.get('files',{}).items():
        p=pre+'/'+k
        if 'files' in m: yield from walk(m,p)
        else: yield p,m
p,sel=sys.argv[1],sys.argv[2]; h,base=load(p); fs=list(walk(h))
if sel=='--list':
    for q,m in fs: print(f"{m.get('size','?'):>10} {'UNP' if m.get('unpacked') else '   '} {q}")
else:
    c=[(q,m) for q,m in fs if sel in q and not m.get('unpacked')]
    pk=[x for x in c if x[0]==sel] or c
    if pk:
        q,m=pk[0]
        with open(p,'rb') as f: f.seek(base+int(m['offset'])); sys.stdout.buffer.write(f.read(m['size']))
PYEOF

echo "================ ELECTRON TRIAGE: $A ($(wc -c < "$A") bytes) ================"
python3 "$PY" "$A" --list > /tmp/_vmdl_list.txt 2>/dev/null
echo "files in asar: $(wc -l < /tmp/_vmdl_list.txt | tr -d ' ')"

echo; echo "--- package.json (entry point) ---"
python3 "$PY" "$A" /package.json 2>/dev/null > /tmp/_vmdl_pkg.json
python3 - <<'PY'
import json
try:
    d=json.load(open('/tmp/_vmdl_pkg.json'))
    for k in ('name','version','productName','main'):
        if k in d: print(f"  {k} = {d[k]}")
except Exception as e: print("  (root package.json not parsed:",e,")")
PY

echo; echo "--- per-bundle IPC map (eiw=exposeInMainWorld, handle=.handle(\"..\") count) ---"
# Single extraction pass: each bundle is pulled from the asar once, scanned for the
# map, and appended to the tally reused below for flags/bridge-names/protocols.
FLAGS_TALLY=/tmp/_vmdl_flags; : > "$FLAGS_TALLY"
for f in $(grep -E '\.(js|cjs|mjs)$' /tmp/_vmdl_list.txt | awk '{print $NF}'); do
  python3 "$PY" "$A" "$f" 2>/dev/null > /tmp/_vmdl_f.js
  cat /tmp/_vmdl_f.js >> "$FLAGS_TALLY"
  eiw=$(grep -ac exposeInMainWorld /tmp/_vmdl_f.js)
  hnd=$(grep -aoE '\.handle\("[^"]+"' /tmp/_vmdl_f.js | sort -u | wc -l | tr -d ' ')
  oe=$(grep -ac openExternal /tmp/_vmdl_f.js); op=$(grep -ac openPath /tmp/_vmdl_f.js)
  cp=$(grep -ac child_process /tmp/_vmdl_f.js)
  sch=$(grep -aoE 'scheme:"[a-z0-9-]+"' /tmp/_vmdl_f.js | sort -u | tr '\n' ' ')
  [ "$eiw$hnd$oe$op$cp" = "00000" ] && [ -z "$sch" ] && continue
  printf '  %-46s eiw=%s handle=%s openExt=%s openPath=%s cproc=%s %s\n' \
    "${f#/}" "$eiw" "$hnd" "$oe" "$op" "$cp" "${sch:+schemes:[$sch]}"
done

echo; echo "--- webPreferences security flags (across bundles; !0=true !1=false) ---"
for t in "contextIsolation:!0" "contextIsolation:!1" "sandbox:!0" "sandbox:!1" \
         "nodeIntegration:!0" "nodeIntegration:!1" "webviewTag:!0" \
         "webSecurity:!1" "allowRunningInsecureContent:!0"; do
  printf "  %-32s %s\n" "$t" "$(grep -aoF "$t" "$FLAGS_TALLY" | wc -l | tr -d ' ')"
done

echo; echo "--- exposeInMainWorld bridge names (renderer-facing API) ---"
grep -aoE 'exposeInMainWorld\(`[^`]+`|exposeInMainWorld\("[^"]+"' "$FLAGS_TALLY" | sort -u | head -30

echo; echo "--- privileged custom protocols ---"
grep -aoE 'registerSchemesAsPrivileged|protocol\.handle' "$FLAGS_TALLY" | sort | uniq -c
rm -f /tmp/_vmdl_f.js "$FLAGS_TALLY" "$PY" /tmp/_vmdl_list.txt /tmp/_vmdl_pkg.json
