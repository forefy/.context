# Detection methodology

## Mach-O parsing (zero dependencies)

`scan.py` reads each file's magic bytes to gate on Mach-O or fat Mach-O, then memory-maps and walks the load commands with `struct`. Per image it extracts the `LC_RPATH` paths in declared order (order is what dyld obeys), the `LC_LOAD_DYLIB` and `LC_LOAD_WEAK_DYLIB` imports tagged with their weak flag, and the presence of `LC_CODE_SIGNATURE`.

Fat binaries: the arm64 slice is preferred; load commands are effectively identical across slices. Java `.class` files also start with `0xCAFEBABE` and are rejected by sanity-checking the fat arch count and re-validating each slice's magic. Only `MH_EXECUTE`, `MH_DYLIB`, and `MH_BUNDLE` are analyzed. For an executable, `@executable_path` resolves to its own directory; for a standalone dylib the hosting executable is unknown, so `@executable_path` rpaths are left unresolved.

## Prefilter

A full-disk walk is dominated by source and asset files in node_modules, caches, and .git trees. The scanner opens a file to read its magic only when the extension is not a known text, source, or asset type, so a Mach-O is never missed for carrying a novel or misleading binary extension. Cloud-synced trees (iCloud `Mobile Documents`, `CloudStorage`) are excluded because `lstat` on a dataless file blocks while macOS materializes it over the network, which stalls a whole-disk walk. Firmlink duplicates and pseudo filesystems are excluded to avoid double counting.

## Hijack candidate

For each imported dylib:

- `@rpath/<suffix>`: resolve `<suffix>` against every rpath in order. If none exist and the import is weak, the slot is the first plantable rpath directory (weak-dylib hijack). If some rpath satisfies it, an earlier plantable rpath directory that lacks the file is an rpath-order hijack. A non-weak import that resolves nowhere is a broken dependency, not a hijack.
- Absolute, `@loader_path`, or `@executable_path` weak imports: if the resolved path does not exist and its directory is plantable, it is a weak-dylib hijack. Paths under `/usr/lib` and `/System` are SIP-protected and dyld-cache-backed, never attacker-writable, and skipped.

## Who can plant (writer class)

`slot_writer()` reports the least-privileged principal that can create a file in the slot directory (or the nearest existing ancestor, for creatable slots), from the directory's permission bits and owner/group - never from the euid running the scan.

| bits / owner | class | meaning |
| --- | --- | --- |
| other-write | world | any user |
| group-write, gid 20 | anylocal | any local user (staff) |
| group-write, gid 80 | admin | administrators |
| group-write, other gid | user | a specific group |
| owner-write, uid != 0 | user | one owner |
| owner-write, uid 0, or none | root / none | only root; not attacker-exploitable, not reported |

ACLs: `acl_get_file` (ctypes, in-process, no fork) detects an extended ACL; only then is `ls -lde` parsed. An allow entry granting a write right (`add_file`, `write`, `append`, `delete`, ...) to a broader principal upgrades the class. Deny entries are not applied as a downgrade.

## Who loads (loader principal)

`build_root_context()` maps executables that run as root: LaunchDaemons in `/Library/LaunchDaemons` and `/System/Library/LaunchDaemons` with no or `root` `UserName` (LaunchAgents run as the user and are excluded), and files in `/Library/PrivilegedHelperTools`. `root_execution()` adds setuid/setgid-root binaries via a mode and owner check. A normal app runs as whoever launches it.

## Library validation

Invoked with native `codesign` only on hosts that have a candidate slot. `codesign --display --verbose=2` yields the `flags=...(runtime)` annotation (hardened runtime) and the Team ID; `codesign -d --entitlements -` reveals `disable-library-validation`. Library validation is enforced when the host is signed, has a real Team ID, has the hardened runtime or explicit `CS_REQUIRE_LV`, and lacks the disable entitlement.

## Severity

| condition | severity |
| --- | --- |
| plantable by ordinary user (world / anylocal), loader root, LV off | critical |
| plantable by admin or one user, loader root, LV off | high (elevation) |
| plantable, loader is the writer's own user, LV off | high (no elevation) |
| plantable, but library validation enforced | low |

## Blind spots (state these in every report)

- dyld shared cache: most `/usr/lib` and `/System` dylibs are not on-disk files; they are Apple-signed with library validation and out of scope.
- Permissions and SIP: files and directories unreadable without elevation are counted but not parsed. Re-run under `sudo` for root-only paths and say so.
- Cloud, firmlink, and network mounts are excluded to keep the walk from stalling or double counting; pass an explicit root to scan them deliberately.
- ACL deny entries are not modeled as a downgrade; a slot denied by an ACL but permitted by the bits may over-report.
- The attacker model is a local interactive user.
