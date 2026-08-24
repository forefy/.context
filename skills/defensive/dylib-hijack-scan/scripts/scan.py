#!/usr/bin/env python3
"""
dylib-hijack-scan: detect macOS applications susceptible to (or already victims of)
dylib hijacking.

Pure-stdlib Mach-O parser. The only external process invoked is the native
`codesign` tool, and only on candidate binaries (those with a real hijack slot),
so there is no fork-per-file cost across a full-system sweep.

Detection is based on Patrick Wardle's dylib-hijacking research:

  1. Weak-dylib hijack   -- an LC_LOAD_WEAK_DYLIB import whose file does not exist
                            on disk. The binary runs fine without it, so an attacker
                            can plant a dylib at that path and get it loaded.

  2. Rpath-order hijack  -- an @rpath-relative import that resolves via a LATER
                            LC_RPATH entry, while an EARLIER rpath directory is
                            attacker-writable (or creatable) and lacks the file.
                            dyld searches rpaths in order and loads the first match,
                            so the attacker's planted copy wins.

The vector is neutralised by **library validation** (hardened runtime without the
`com.apple.security.cs.disable-library-validation` entitlement): dyld refuses to
load a dylib not signed by the host's Team ID (or Apple). Findings are severity-
scored with that mitigation in mind.
"""

import argparse
import ctypes
import ctypes.util
import json
import mmap
import os
import plistlib
import re
import struct
import subprocess
import sys
import time


MH_MAGIC     = 0xFEEDFACE
MH_CIGAM     = 0xCEFAEDFE
MH_MAGIC_64  = 0xFEEDFACF
MH_CIGAM_64  = 0xCFFAEDFE
FAT_MAGIC    = 0xCAFEBABE
FAT_CIGAM    = 0xBEBAFECA
FAT_MAGIC_64 = 0xCAFEBABF
FAT_CIGAM_64 = 0xBFBAFECA

MACHO_MAGICS = {MH_MAGIC, MH_CIGAM, MH_MAGIC_64, MH_CIGAM_64}
FAT_MAGICS   = {FAT_MAGIC, FAT_CIGAM, FAT_MAGIC_64, FAT_CIGAM_64}

LC_REQ_DYLD          = 0x80000000
LC_LOAD_DYLIB        = 0x0C
LC_LOAD_WEAK_DYLIB   = 0x18 | LC_REQ_DYLD
LC_RPATH             = 0x1C | LC_REQ_DYLD
LC_REEXPORT_DYLIB    = 0x1F | LC_REQ_DYLD
LC_LOAD_UPWARD_DYLIB = 0x23 | LC_REQ_DYLD
LC_CODE_SIGNATURE    = 0x1D

MH_EXECUTE = 0x2
MH_DYLIB   = 0x6
MH_BUNDLE  = 0x8


DEFAULT_EXCLUDES = {
    "/dev", "/Volumes", "/System/Volumes/Data", "/System/Volumes/Preboot",
    "/System/Volumes/VM", "/System/Volumes/Update", "/private/var/vm",
    "/.Spotlight-V100", "/.fseventsd", "/.DocumentRevisions-V100",
    "/private/var/folders",


    os.path.expanduser("~/Library/Mobile Documents"),
    os.path.expanduser("~/Library/CloudStorage"),
    os.path.expanduser("~/.Trash"),
}


class MachOImage:
    __slots__ = ("filetype", "rpaths", "imports", "has_code_sig")

    def __init__(self):
        self.filetype = 0
        self.rpaths = []
        self.imports = []
        self.has_code_sig = False


def _cstr(buf, start, limit):
    end = buf.find(b"\x00", start, limit)
    if end == -1:
        end = limit
    return buf[start:end].decode("utf-8", "replace")


def _parse_slice(mm, base, size):
    """Parse one thin Mach-O at offset `base`. Returns MachOImage or None."""
    if base + 28 > len(mm):
        return None
    magic = struct.unpack_from("<I", mm, base)[0]
    if magic in (MH_MAGIC_64, MH_CIGAM_64):
        endian = "<" if magic == MH_MAGIC_64 else ">"
        is64 = True
    elif magic in (MH_MAGIC, MH_CIGAM):
        endian = "<" if magic == MH_MAGIC else ">"
        is64 = False
    else:
        return None

    hdr_fmt = endian + "IiiIII" + ("I" if is64 else "")

    fields = struct.unpack_from(hdr_fmt, mm, base)
    filetype = fields[3]
    ncmds = fields[4]
    hdr_size = 32 if is64 else 28

    img = MachOImage()
    img.filetype = filetype

    off = base + hdr_size
    limit = min(len(mm), base + size) if size else len(mm)
    for _ in range(ncmds):
        if off + 8 > limit:
            break
        cmd, cmdsize = struct.unpack_from(endian + "II", mm, off)
        if cmdsize < 8 or off + cmdsize > limit:
            break
        c = cmd & 0xFFFFFFFF
        if c in (LC_LOAD_DYLIB, LC_LOAD_WEAK_DYLIB, LC_REEXPORT_DYLIB, LC_LOAD_UPWARD_DYLIB):
            str_off = struct.unpack_from(endian + "I", mm, off + 8)[0]
            if 0 < str_off < cmdsize:
                path = _cstr(mm, off + str_off, off + cmdsize)
                img.imports.append((path, c == LC_LOAD_WEAK_DYLIB))
        elif c == LC_RPATH:
            str_off = struct.unpack_from(endian + "I", mm, off + 8)[0]
            if 0 < str_off < cmdsize:
                img.rpaths.append(_cstr(mm, off + str_off, off + cmdsize))
        elif c == LC_CODE_SIGNATURE:
            img.has_code_sig = True
        off += cmdsize
    return img


def parse_macho(path):
    """Return a merged MachOImage for the file, or None if not Mach-O.

    For fat binaries the arm64(e) slice is preferred; load commands are otherwise
    near-identical across slices, so one representative slice suffices.
    """
    try:
        with open(path, "rb") as f:
            fileno = f.fileno()
            fsize = os.fstat(fileno).st_size
            if fsize < 28:
                return None
            mm = mmap.mmap(fileno, 0, prot=mmap.PROT_READ)
    except (OSError, ValueError):
        return None

    try:
        magic_be = struct.unpack_from(">I", mm, 0)[0]
        if magic_be in FAT_MAGICS:
            is64 = magic_be in (FAT_MAGIC_64, FAT_CIGAM_64)
            nfat = struct.unpack_from(">I", mm, 4)[0]
            if nfat > 64:
                return None
            entry_sz = 32 if is64 else 20
            slices = []
            pos = 8
            for _ in range(nfat):
                if pos + entry_sz > len(mm):
                    break
                if is64:
                    cputype, _sub, offset, size, _al = struct.unpack_from(">iiQQI", mm, pos)
                else:
                    cputype, _sub, offset, size, _al = struct.unpack_from(">iiIII", mm, pos)
                slices.append((cputype, offset, size))
                pos += entry_sz
            if not slices:
                return None

            chosen = next((s for s in slices if s[0] == 0x0100000C), slices[0])
            return _parse_slice(mm, chosen[1], chosen[2])
        elif struct.unpack_from("<I", mm, 0)[0] in MACHO_MAGICS:
            return _parse_slice(mm, 0, len(mm))
        return None
    except (struct.error, ValueError):
        return None
    finally:
        mm.close()


def looks_macho(path):
    """Cheap gate: read the first 4 bytes and check for a Mach-O/fat magic."""
    try:
        with open(path, "rb") as f:
            head = f.read(4)
    except OSError:
        return False
    if len(head) < 4:
        return False
    be = struct.unpack(">I", head)[0]
    le = struct.unpack("<I", head)[0]
    return be in FAT_MAGICS or le in MACHO_MAGICS or be in MACHO_MAGICS


def resolve_special(p, exec_dir, loader_dir):
    if p.startswith("@executable_path"):
        return os.path.normpath(exec_dir + p[len("@executable_path"):])
    if p.startswith("@loader_path"):
        return os.path.normpath(loader_dir + p[len("@loader_path"):])
    return p


STAFF_GID = 20
ADMIN_GID = 80
NONROOT_WRITERS = ("world", "anylocal", "admin", "user")


def _nearest_existing(directory):
    d = directory
    while d and not os.path.exists(d):
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    return d if d and os.path.exists(d) else None


_ACL_TYPE_EXTENDED = 0x00000100
_ACL_GROUP_CLASS = {"everyone": "world", "staff": "anylocal",
                    "admin": "admin", "wheel": "root"}
_ACL_WRITE_RIGHTS = ("add_file", "write", "append", "delete", "write_data",
                     "add_subdirectory", "delete_child")
try:
    _libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
    _libc.acl_get_file.restype = ctypes.c_void_p
    _libc.acl_get_file.argtypes = [ctypes.c_char_p, ctypes.c_uint]
    _libc.acl_free.argtypes = [ctypes.c_void_p]
except Exception:
    _libc = None


def _has_acl(path):
    """True iff `path` carries an extended ACL. macOS returns NULL (no ACL) or a
    non-null acl_t; we only need presence, so we free it immediately."""
    if _libc is None:
        return False
    try:
        a = _libc.acl_get_file(os.fsencode(path), _ACL_TYPE_EXTENDED)
    except Exception:
        return False
    if a:
        _libc.acl_free(a)
        return True
    return False


def _acl_grant_class(directory):
    """Least-privileged writer class an ACL *allow* entry grants on `directory`
    (or 'none'). Only called for dirs that actually have an ACL, so the `ls`
    fork is rare. Deny-downgrade is intentionally not applied -- for a scanner,
    over-reporting a writable slot is safer than missing one."""
    try:
        out = subprocess.run(["/bin/ls", "-lde", directory],
                             capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return "none"
    decided = {}
    for line in out.splitlines():
        m = re.match(r"\s*\d+:\s+(user|group):([^\s]+(?:\s[^\s]+)*?)\s+(allow|deny)\s+(.*)",
                     line)
        if not m:
            continue
        typ, name, act, rights = m.group(1), m.group(2), m.group(3), m.group(4)
        if "only_inherit" in rights:
            continue
        if not any(r in rights for r in _ACL_WRITE_RIGHTS):
            continue
        key = (typ, name)
        decided.setdefault(key, act)
    granted = []
    for (typ, name), act in decided.items():
        if act != "allow":
            continue
        if typ == "group":
            granted.append(_ACL_GROUP_CLASS.get(name, "user"))
        else:
            granted.append("root" if name == "root" else "user")
    if not granted:
        return "none"
    return min(granted, key=lambda c: _WRITER_RANK.get(c, 9))


def slot_writer(slot_path):
    """Least-privileged principal that can create a planted dylib at slot_path.

    Determined from the slot directory's permission BITS and owner/group -- NOT
    from the euid running the scan -- so the verdict is the same whether the scan
    runs as a standard user, an admin, or root. Returns (klass, detail):

      world    -- any user (o+w)
      anylocal -- any local user (group staff, gid 20)
      admin    -- administrators only (group admin, gid 80)
      user     -- one specific non-root user (owner, or a service group)
      root     -- only root/wheel can plant  -> NOT attacker-exploitable
      none     -- not writable by anyone / no ancestor
    """
    d = _nearest_existing(os.path.dirname(slot_path))
    if not d:
        return ("none", "no existing ancestor")
    try:
        st = os.stat(d)
    except OSError:
        return ("none", "stat failed")
    m = st.st_mode
    where = d if d == os.path.dirname(slot_path) else f"creatable via ancestor {d}"
    if m & 0o0002:
        klass, detail = "world", f"world-writable ({where})"
    elif m & 0o0020:
        if st.st_gid == STAFF_GID:
            klass, detail = "anylocal", f"group staff-writable ({where})"
        elif st.st_gid == ADMIN_GID:
            klass, detail = "admin", f"group admin-writable ({where})"
        elif st.st_gid == 0:
            klass, detail = "root", f"group wheel-writable ({where})"
        else:
            klass, detail = "user", f"group {st.st_gid}-writable ({where})"
    elif m & 0o0200:
        if st.st_uid == 0:
            klass, detail = "root", f"root-owned, root-only ({where})"
        else:
            klass, detail = "user", f"owned by uid {st.st_uid} ({where})"
    else:
        klass, detail = "none", f"not writable ({where})"


    if _has_acl(d):
        acl_cls = _acl_grant_class(d)
        if acl_cls != "none" and _WRITER_RANK.get(acl_cls, 9) < _WRITER_RANK.get(klass, 9):
            klass, detail = acl_cls, f"ACL grants write to {acl_cls} ({d})"
    return (klass, detail)


_WRITER_RANK = {"world": 0, "anylocal": 1, "admin": 2, "user": 2, "root": 3, "none": 4}


def elevation_verdict(host, writer_class, lib_val, root_ctx):
    """Given a plantable slot, decide severity + whether it crosses a privilege
    boundary. Returns (severity, elevation: bool, kind, loader_reason)."""
    if lib_val:
        return ("low", False, "library validation blocks a foreign dylib", None)
    is_root, reason = root_execution(host, root_ctx)
    if is_root and _WRITER_RANK.get(writer_class, 9) < 3:
        if writer_class in ("world", "anylocal"):
            return ("critical", True, "ordinary local user -> root", reason)
        if writer_class == "admin":
            return ("high", True, "admin -> root", reason)
        return ("high", True, "another user -> root", reason)

    return ("high", False, "same user context (no privilege gain)", None)


_codesign_cache = {}

def library_validation(path):
    """Return dict describing the host's signing posture, via native `codesign`.

    Only called for candidate binaries, so the subprocess cost is negligible.
    """
    if path in _codesign_cache:
        return _codesign_cache[path]
    info = {"signed": False, "hardened_runtime": False,
            "disable_lv_entitlement": False, "library_validation": False,
            "team_id": None}
    require_lv = False
    try:
        p = subprocess.run(["/usr/bin/codesign", "--display", "--verbose=2", path],
                           capture_output=True, text=True, timeout=20)
        err = p.stderr
        if "code object is not signed" not in err and p.returncode == 0:
            info["signed"] = True


        m = re.search(r"flags=0x[0-9a-fA-F]+\s*\(([^)]*)\)", err)
        if m:
            annot = m.group(1)
            info["hardened_runtime"] = "runtime" in annot
            require_lv = "library-validation" in annot
        for line in err.splitlines():
            if line.startswith("TeamIdentifier="):
                tid = line.split("=", 1)[1].strip()
                info["team_id"] = None if tid in ("", "not set") else tid
    except (OSError, subprocess.SubprocessError):
        pass

    if info["signed"]:
        try:
            e = subprocess.run(
                ["/usr/bin/codesign", "-d", "--entitlements", "-", "--xml", path],
                capture_output=True, text=True, timeout=20)
            blob = (e.stdout or "") + (e.stderr or "")
            info["disable_lv_entitlement"] = "disable-library-validation" in blob
        except (OSError, subprocess.SubprocessError):
            pass


    info["library_validation"] = (
        info["signed"]
        and (info["hardened_runtime"] or require_lv)
        and not info["disable_lv_entitlement"]
        and info["team_id"] is not None
    )
    _codesign_cache[path] = info
    return info


DYLD_CACHE_ROOTS = ("/usr/lib/", "/System/Library/", "/System/iOSSupport/")


def classify_imports(path, img):
    """Return one record per imported dylib of a host, each with a verdict:
    'hijackable' (plantable slot), 'missing' (required, absent), or 'ok'.

    Severity on hijackable rows is filled in by the caller once it knows the
    host's library-validation posture."""
    host_dir = os.path.dirname(os.path.abspath(path))
    exec_dir = host_dir if img.filetype == MH_EXECUTE else None
    loader_dir = host_dir

    resolved_rpaths = []
    for rp in img.rpaths:
        if rp.startswith("@executable_path") and exec_dir is None:
            resolved_rpaths.append((rp, None))
        else:
            resolved_rpaths.append((rp, resolve_special(rp, exec_dir or host_dir, loader_dir)))

    def plant(cand):
        """(plantable_by_non_root, writer_class, detail) for a candidate slot."""
        wk, detail = slot_writer(cand)
        return (wk in NONROOT_WRITERS, wk, detail)

    records = []
    for imp_path, weak in img.imports:
        rec = {"import": imp_path, "weak": weak, "verdict": "ok", "severity": None,
               "slot": None, "reason": "", "resolved": None, "writer": None}

        if imp_path.startswith("@rpath/"):
            suffix = imp_path[len("@rpath/"):]
            existing_idx = None
            cands = []
            for raw, rdir in resolved_rpaths:
                if rdir is None:
                    cands.append((raw, None, False)); continue
                c = os.path.join(rdir, suffix)
                e = os.path.exists(c)
                cands.append((raw, c, e))
                if e and existing_idx is None:
                    existing_idx = len(cands) - 1
            if existing_idx is None:
                hit = None
                for raw, c, _ in cands:
                    if c is None:
                        continue
                    ok, wk, detail = plant(c)
                    if ok:
                        hit = (c, wk, detail); break
                if weak and hit:
                    rec.update(verdict="hijackable", slot=hit[0], writer=hit[1],
                               reason="weak import, dylib absent everywhere; " + hit[2])
                elif weak:
                    rec.update(reason="weak import, absent, but no non-root-writable rpath slot")
                else:
                    rec.update(verdict="missing", reason="required dylib not found in any rpath")
            else:
                rec["resolved"] = cands[existing_idx][1]
                hit = None
                for i in range(existing_idx):
                    raw, c, _ = cands[i]
                    if c is None:
                        continue
                    ok, wk, detail = plant(c)
                    if ok:
                        hit = (c, wk, detail); break
                if hit:
                    rec.update(verdict="hijackable", slot=hit[0], writer=hit[1],
                               reason="earlier rpath is plantable; " + hit[2])
                else:
                    rec.update(reason="resolves via rpath; no earlier non-root-writable slot")

        elif imp_path.startswith("@loader_path") or imp_path.startswith("@executable_path"):
            resolved = resolve_special(imp_path, exec_dir or host_dir, loader_dir)
            rec["resolved"] = resolved
            if not resolved.startswith("@") and not os.path.exists(resolved):
                ok, wk, detail = plant(resolved)
                if weak and ok:
                    rec.update(verdict="hijackable", slot=resolved, writer=wk,
                               reason="weak import, missing; " + detail)
                elif weak:
                    rec.update(reason="weak import, missing, slot not non-root-writable")
                else:
                    rec.update(verdict="missing", reason="required dylib missing")
            else:
                rec.update(reason="resolves relative to loader")
        else:
            rec["resolved"] = imp_path
            if imp_path.startswith(DYLD_CACHE_ROOTS):


                rec.update(reason="system / dyld shared cache (SIP-protected)")
            elif not os.path.exists(imp_path):
                ok, wk, detail = plant(imp_path)
                if weak and ok:
                    rec.update(verdict="hijackable", slot=imp_path, writer=wk,
                               reason="weak import, missing; " + detail)
                elif weak:
                    rec.update(reason="weak import, missing, slot not non-root-writable")
                else:
                    rec.update(verdict="missing", reason="required dylib missing")
            else:
                rec.update(reason="absolute system/bundled path")
        records.append(rec)
    return records


def build_root_context():
    """Map executable realpath -> reason, for binaries that execute as root.

    A hijackable slot only escalates privilege when the *host* runs as root: then
    an unprivileged user who can plant the dylib gets root code execution. Sources:
      - LaunchDaemons (root at boot unless UserName overrides) -- NOT LaunchAgents,
        which run as the logged-in user.
      - Privileged helper tools (SMJobBless, run as root).
    setuid/setgid-root executables are detected per-host during the walk.
    """
    ctx = {}
    for dd in ("/Library/LaunchDaemons", "/System/Library/LaunchDaemons"):
        try:
            names = os.listdir(dd)
        except OSError:
            continue
        for name in names:
            if not name.endswith(".plist"):
                continue
            try:
                with open(os.path.join(dd, name), "rb") as fh:
                    pl = plistlib.load(fh)
            except Exception:
                continue
            user = pl.get("UserName")
            if user and user != "root":
                continue
            prog = pl.get("Program")
            if not prog:
                args = pl.get("ProgramArguments")
                prog = args[0] if isinstance(args, list) and args else None
            if isinstance(prog, str) and prog:
                ctx.setdefault(os.path.realpath(prog), f"LaunchDaemon {name} (root)")
    try:
        pht = "/Library/PrivilegedHelperTools"
        for name in os.listdir(pht):
            fp = os.path.join(pht, name)
            if os.path.isfile(fp):
                ctx.setdefault(os.path.realpath(fp), "privileged helper tool (root)")
    except OSError:
        pass
    return ctx


def root_execution(path, root_ctx):
    """Return (runs_as_root, reason) for a host path."""
    rp = os.path.realpath(path)
    if rp in root_ctx:
        return True, root_ctx[rp]
    try:
        st = os.stat(path)
        if st.st_mode & 0o4000 and st.st_uid == 0:
            return True, "setuid root"
        if st.st_mode & 0o2000 and st.st_gid == 0:
            return True, "setgid wheel"
    except OSError:
        pass
    return False, None


SKIP_EXTS = frozenset({

    ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".map", ".json", ".json5",
    ".py", ".pyc", ".pyi", ".rb", ".go", ".rs", ".java", ".kt", ".swift",
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".m", ".mm", ".cs", ".php",
    ".pl", ".lua", ".sh", ".bash", ".zsh", ".fish", ".sql", ".r",
    ".html", ".htm", ".xml", ".xhtml", ".css", ".scss", ".sass", ".less",
    ".md", ".markdown", ".rst", ".txt", ".text", ".rtf", ".tex", ".csv", ".tsv",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".properties",
    ".lock", ".log", ".gitignore", ".gitattributes", ".editorconfig", ".env",

    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".ico",
    ".svg", ".icns", ".heic", ".psd", ".ai", ".sketch",
    ".mp3", ".wav", ".aiff", ".flac", ".m4a", ".ogg", ".mp4", ".mov", ".avi",
    ".mkv", ".webm", ".m4v", ".pdf",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",

    ".zip", ".gz", ".tgz", ".bz2", ".xz", ".zst", ".7z", ".rar", ".tar",
    ".jar", ".war", ".class", ".wasm", ".db", ".sqlite", ".sqlite3", ".dat",
    ".plist", ".strings", ".nib", ".storyboardc", ".car", ".pak", ".bin",
    ".pack", ".idx", ".ncd", ".metallib", ".spv", ".glsl",
    ".a", ".lib", ".o", ".d", ".pdb", ".dSYM",
})

def _could_be_macho(name, dirpath, is_exec):
    """Cheap name/mode gate applied before opening a file to read its magic.

    Open (return True) unless the file carries a known non-Mach-O text/asset
    extension. Executables are always opened. This keeps the residual blind spot
    to Mach-O files that both lack the executable bit AND wear a deny-listed
    extension -- practically nonexistent.
    """
    if is_exec:
        return True
    dot = name.rfind(".")
    if dot <= 0:
        return True
    return name[dot:].lower() not in SKIP_EXTS


def iter_macho_files(roots, excludes, stats, no_prefilter=False):
    seen = set()
    hb = [0]
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False,
                                                     onerror=lambda e: stats.__setitem__(
                                                         "unreadable_dirs", stats["unreadable_dirs"] + 1)):

            if stats["files_walked"] - hb[0] >= 400000:
                hb[0] = stats["files_walked"]
                print(f"  [walk] {stats['files_walked']:,} files, at {dirpath}",
                      file=sys.stderr, flush=True)

            dirnames[:] = [d for d in dirnames
                           if os.path.join(dirpath, d) not in excludes]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                try:
                    st = os.lstat(fp)
                except OSError:
                    stats["unreadable_files"] += 1
                    continue
                if not (st.st_mode & 0o170000) == 0o100000:
                    continue
                if st.st_size < 28:
                    continue
                stats["files_walked"] += 1
                if not no_prefilter and not _could_be_macho(fn, dirpath, bool(st.st_mode & 0o111)):
                    stats["skipped_prefilter"] += 1
                    continue
                real = (st.st_dev, st.st_ino)
                if real in seen:
                    continue
                seen.add(real)
                stats["files_examined"] += 1
                if looks_macho(fp):
                    yield fp


def main():
    ap = argparse.ArgumentParser(description="Scan for dylib-hijackable Mach-O binaries.")
    ap.add_argument("roots", nargs="*", default=None,
                    help="Directories to scan (default: whole system, '/').")
    ap.add_argument("--json", metavar="FILE", help="Write full findings as JSON.")
    ap.add_argument("--min-severity", default="low",
                    choices=["info", "low", "medium", "high", "critical"],
                    help="Minimum severity to print (default: low).")
    ap.add_argument("--quiet", action="store_true", help="Only print the summary.")
    ap.add_argument("--no-prefilter", action="store_true",
                    help="Open EVERY regular file to read its magic (literal full "
                         "coverage; much slower on dev machines with node_modules).")
    args = ap.parse_args()

    roots = args.roots if args.roots else ["/"]
    excludes = set(DEFAULT_EXCLUDES)

    stats = {"files_walked": 0, "skipped_prefilter": 0, "files_examined": 0,
             "macho_parsed": 0, "parse_failures": 0, "unreadable_files": 0,
             "unreadable_dirs": 0, "hosts_with_findings": 0}
    sev_rank = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    min_rank = sev_rank[args.min_severity]

    ftype_name = {MH_EXECUTE: "executable", MH_DYLIB: "dylib", MH_BUNDLE: "bundle"}
    root_ctx = build_root_context()
    all_findings = []
    inventory = []
    t0 = time.time()
    for fp in iter_macho_files(roots, excludes, stats, no_prefilter=args.no_prefilter):
        img = parse_macho(fp)
        if img is None:
            stats["parse_failures"] += 1
            continue
        stats["macho_parsed"] += 1
        if stats["macho_parsed"] % 3000 == 0:
            print(f"  ... {stats['macho_parsed']:,} Mach-O parsed, "
                  f"{stats['files_walked']:,} files walked, {time.time() - t0:.0f}s",
                  file=sys.stderr, flush=True)
        if img.filetype not in ftype_name or not img.imports:
            continue
        recs = classify_imports(fp, img)
        hij = [r for r in recs if r["verdict"] == "hijackable"]
        runs_as_root, root_reason = root_execution(fp, root_ctx)
        if hij:
            sig = library_validation(fp)
            lv = sig["library_validation"]
            for r in hij:


                sev, elev, kind, lreason = elevation_verdict(fp, r.get("writer"), lv, root_ctx)
                r["severity"] = sev
                r["elevation"] = elev
                r["elevation_kind"] = kind
                all_findings.append({
                    "host": fp, "filetype": ftype_name[img.filetype],
                    "kind": "weak-missing" if "weak import" in r["reason"] else "rpath-order",
                    "import": r["import"], "hijack_slot": r["slot"], "reason": r["reason"],
                    "writer": r.get("writer"), "elevation": elev, "elevation_kind": kind,
                    "signed": sig["signed"], "hardened_runtime": sig["hardened_runtime"],
                    "library_validation": lv, "team_id": sig["team_id"],
                    "runs_as_root": runs_as_root, "root_reason": root_reason,
                    "severity": sev})
            host_sig = {"signed": sig["signed"], "hardened_runtime": sig["hardened_runtime"],
                        "library_validation": lv, "team_id": sig["team_id"]}
            stats["hosts_with_findings"] += 1
        else:
            host_sig = {"signed": None, "hardened_runtime": None,
                        "library_validation": None, "team_id": None}
        inventory.append({"host": fp, "filetype": ftype_name[img.filetype],
                          "imports": recs, "runs_as_root": runs_as_root,
                          "root_reason": root_reason, **host_sig})
    elapsed = time.time() - t0

    all_findings.sort(key=lambda f: -sev_rank[f["severity"]])
    counts = {"info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    for f in all_findings:
        counts[f["severity"]] += 1

    if not args.quiet:
        for f in all_findings:
            if sev_rank[f["severity"]] < min_rank:
                continue
            lv = "LV-protected" if f["library_validation"] else "NO library validation"
            print(f"[{f['severity'].upper():6}] {f['kind']}  ({lv})")
            print(f"         host : {f['host']}")
            print(f"         import: {f['import']}")
            print(f"         slot  : {f['hijack_slot']}")
            print(f"         why   : {f['reason']}")
            print()

    print("=" * 70)
    print("COVERAGE")
    print(f"  files walked       : {stats['files_walked']:,}")
    print(f"  skipped (prefilter): {stats['skipped_prefilter']:,}  (can't be Mach-O by name/mode)")
    print(f"  magic-checked      : {stats['files_examined']:,}")
    print(f"  Mach-O parsed      : {stats['macho_parsed']:,}")
    print(f"  parse failures     : {stats['parse_failures']:,}")
    print(f"  unreadable files   : {stats['unreadable_files']:,}  (blind spot: permissions)")
    print(f"  unreadable dirs    : {stats['unreadable_dirs']:,}  (blind spot: permissions/SIP)")
    print(f"  elapsed            : {elapsed:.1f}s")
    print("  NOTE: system dylibs in the dyld shared cache are not on-disk files;")
    print("        they are Apple-signed with library validation and out of scope.")
    n_elev = sum(1 for f in all_findings if f.get("elevation"))
    print("FINDINGS")
    print(f"  hosts with findings: {stats['hosts_with_findings']:,}")
    print(f"  ELEVATION (privesc): {n_elev:,}   (writer less privileged than loader -> crosses a boundary)")
    print(f"    of which CRITICAL: {counts['critical']:,}   (ordinary local user -> root)")
    print(f"  high    : {counts['high']:,}   (plantable slot, NO library validation)")
    print(f"  low     : {counts['low']:,}   (slot exists but library validation blocks it)")
    print("=" * 70)

    if args.json:


        with open(args.json, "w") as fh:
            json.dump({"stats": stats, "elapsed_seconds": elapsed,
                       "counts": counts, "findings": all_findings,
                       "inventory": inventory}, fh, separators=(",", ":"))
        print(f"Findings + full inventory written to {args.json} "
              f"({len(inventory):,} hosts)")


if __name__ == "__main__":
    main()
