#!/usr/bin/env python3
# Minimal Electron .asar reader - no node/npm needed (runs on any guest with
# python3). List files, or extract one by exact-or-substring path to stdout.
#   asar.py <app.asar> --list                 # size + UNP flag + path, one per line
#   asar.py <app.asar> /package.json          # exact path preferred over substring
#   asar.py <app.asar> build/index.pre.js     # substring match
# asar stores JS as plaintext (no compression/encryption), so grep also works
# directly on the .asar; this tool is for pulling individual files out cleanly.
import sys, struct, json

def load(path):
    with open(path, 'rb') as f:
        struct.unpack('<I', f.read(4))[0]                 # pickle1 size (=4)
        header_size = struct.unpack('<I', f.read(4))[0]   # header pickle total size
        struct.unpack('<I', f.read(4))[0]                 # json pickle payload size
        json_len = struct.unpack('<I', f.read(4))[0]      # json string length
        header = json.loads(f.read(json_len).decode('utf-8', 'replace'))
    return header, 8 + header_size                        # (header, base offset)

def walk(node, prefix=''):
    for name, meta in node.get('files', {}).items():
        p = prefix + '/' + name
        if 'files' in meta:
            yield from walk(meta, p)
        else:
            yield p, meta

def main():
    if len(sys.argv) < 3:
        sys.exit("usage: asar.py <app.asar> (--list | <path-substring>)")
    path, sel = sys.argv[1], sys.argv[2]
    header, base = load(path)
    files = list(walk(header))
    if sel == '--list':
        for p, m in files:
            print(f"{m.get('size','?'):>10} {'UNP' if m.get('unpacked') else '   '} {p}")
        return
    cands = [(p, m) for p, m in files if sel in p and not m.get('unpacked')]
    pick = [c for c in cands if c[0] == sel] or cands
    if not pick:
        sys.exit(f"no packed file matching: {sel}")
    p, m = pick[0]
    sys.stderr.write(f"[extracted {p} ({m['size']}b)]\n")
    with open(path, 'rb') as f:
        f.seek(base + int(m['offset']))
        sys.stdout.buffer.write(f.read(m['size']))

main()
