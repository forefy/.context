#!/usr/bin/env python3
"""
Build an App -> loaded-dylib -> hijackable/not report from a scan.

Reads the findings JSON produced by scan.py to learn which binaries are
affected, then RE-PARSES each affected host to enumerate its full ordered import
list, classifying every loaded dylib:

  hijackable  -- attacker-plantable slot, library validation off   (HIGH)
  protected   -- plantable slot, but library validation blocks it   (LOW)
  ok          -- resolves safely (system path / first rpath / no writable slot)

Emits a structured report JSON (grouped by app bundle) and, with --html, a
self-contained report page.
"""

import argparse
import html
import json
import os
import sys


def filter_report(report, matches):
    """Keep only apps whose container path or any binary path contains one of the
    (case-insensitive) match substrings. Recompute scope-local counts/totals."""
    ms = [m.lower() for m in matches]

    def keep(app):
        if any(m in app["container"].lower() for m in ms):
            return True
        return any(any(m in b["path"].lower() for m in ms) for b in app["binaries"])

    apps = [a for a in report["apps"] if keep(a)]
    counts = {"info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    nb = 0
    for a in apps:
        nb += a["n_binaries"]
        for b in a["binaries"]:
            for r in b["imports"]:
                s = r.get("severity")
                if s in counts:
                    counts[s] += 1
    out = dict(report)
    out.update(apps=apps, counts=counts, n_apps=len(apps), n_binaries=nb,
               scope=", ".join(matches))
    return out


def app_container(path):
    if ".app/" in path:
        return path.split(".app/")[0] + ".app"

    parts = path.split("/")
    if "Cellar" in parts:
        i = parts.index("Cellar")
        return "/".join(parts[:i + 3])
    return os.path.dirname(path)


def build(scan_json):
    """Consume the full inventory emitted by scan.py (every analyzable host with
    its classified imports) and group it into a complete per-app report."""
    data = json.load(open(scan_json))
    inv = data.get("inventory")
    if inv is None:
        raise SystemExit("This scan JSON has no 'inventory'. Re-run scan.py "
                         "(it now always emits the full inventory).")

    apps = {}
    for h in inv:
        recs = h["imports"]
        nc = sum(1 for r in recs if r.get("severity") == "critical")
        nh = sum(1 for r in recs if r.get("severity") == "high")
        nl = sum(1 for r in recs if r.get("severity") == "low")
        ne = sum(1 for r in recs if r.get("elevation"))
        cont = app_container(h["host"])
        e = apps.setdefault(cont, {"container": cont, "binaries": [], "lv_known": False,
                                   "library_validation": None, "team_id": None,
                                   "signed": None, "hardened_runtime": None,
                                   "root_reason": None})


        if not e["lv_known"] and h.get("library_validation") is not None:
            e["lv_known"] = True
            e["library_validation"] = h["library_validation"]
            e["team_id"] = h["team_id"]
            e["signed"] = h["signed"]
            e["hardened_runtime"] = h["hardened_runtime"]
        if e["root_reason"] is None and h.get("runs_as_root"):
            e["root_reason"] = h.get("root_reason")
        e["binaries"].append({
            "path": h["host"],
            "rel": h["host"][len(cont):].lstrip("/") or os.path.basename(h["host"]),
            "imports": recs,
            "runs_as_root": h.get("runs_as_root", False),
            "root_reason": h.get("root_reason"),
            "n_critical": nc,
            "n_elevation": ne,
            "n_hijackable_high": nh,
            "n_hijackable_low": nl,
        })

    report = []
    for cont, e in apps.items():
        e["n_critical"] = sum(b["n_critical"] for b in e["binaries"])
        e["n_elevation"] = sum(b["n_elevation"] for b in e["binaries"])
        e["n_high"] = sum(b["n_hijackable_high"] for b in e["binaries"])
        e["n_low"] = sum(b["n_hijackable_low"] for b in e["binaries"])
        e["n_binaries"] = len(e["binaries"])
        e["verdict"] = ("critical" if e["n_critical"] else "hijackable" if e["n_high"]
                        else "protected" if e["n_low"] else "ok")
        e["binaries"].sort(key=lambda b: (-b["n_critical"], -b["n_elevation"],
                                          -b["n_hijackable_high"], -b["n_hijackable_low"], b["rel"]))
        report.append(e)
    report.sort(key=lambda e: (-e["n_critical"], -e["n_elevation"], -e["n_high"],
                               -e["n_low"], e["container"].lower()))
    n_root = sum(1 for h in inv if h.get("runs_as_root"))
    n_elev = sum(e["n_elevation"] for e in report)
    return {"stats": data.get("stats"), "counts": data.get("counts"),
            "elapsed_seconds": data.get("elapsed_seconds"),
            "n_apps": len(report), "n_binaries": len(inv), "n_root": n_root,
            "n_elev": n_elev, "apps": report}


VERDICT_BADGE = {
    "critical": ("PRIVESC - ROOT", "crit"),
    "hijackable": ("HIJACKABLE", "high"),
    "protected": ("PROTECTED", "low"),
    "ok": ("CLEAN", "ok"),
}

WRITER_LABEL = {
    "world": "any user",
    "anylocal": "any local user",
    "admin": "admins",
    "user": "one user",
    "root": "root only",
    "none": "-",
}


def esc(s):
    return html.escape(str(s), quote=True)


def imp_sort_key(r):
    """Critical first, then hijackable (high), then protected (low), then rest."""
    return {"critical": 0, "high": 1, "low": 2}.get(r["severity"], 3)


def row_class(r):
    if r["severity"] in ("critical", "high", "low"):
        return "crit" if r["severity"] == "critical" else r["severity"]
    if r["verdict"] == "missing":
        return "missing"
    return "ok"


def render_html(report):
    apps = report["apps"]
    st = report["stats"] or {}
    counts = report["counts"] or {}
    n_critical = sum(1 for a in apps if a["verdict"] == "critical")
    n_hijackable = sum(1 for a in apps if a["verdict"] == "hijackable")
    n_protected = sum(1 for a in apps if a["verdict"] == "protected")

    out = []
    out.append("<title>Dylib Hijack Report</title>")
    out.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    out.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    out.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
               'family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">')
    out.append(STYLE)
    out.append('<div class="wrap">')
    scope = report.get("scope")
    eyebrow = (f'macOS &middot; Mach-O audit &middot; scope: {esc(scope)}' if scope
               else "macOS &middot; Mach-O audit")
    out.append(f'<div class="mast"><span class="eyebrow">{eyebrow}</span>'
               '<h1>Dylib Hijack Report</h1></div>')
    if scope:
        out.append(f'<p class="sub">Scoped to <b>{esc(scope)}</b>: '
                   f'{format(report.get("n_binaries", 0), ",")} Mach-O binaries across '
                   f'{format(report.get("n_apps", 0), ",")} matching apps &amp; locations, '
                   f'with the dylibs each loads and whether they are hijackable.</p>')
    else:
        out.append(f'<p class="sub">Full inventory: every one of the '
                   f'{format(report.get("n_binaries", 0), ",")} loadable Mach-O binaries on the '
                   f'system, across {format(report.get("n_apps", 0), ",")} apps &amp; locations, '
                   f'with the dylibs each loads and whether they are hijackable.</p>')


    out.append('<div class="tiles">')
    out.append(tile(report.get("n_elev", 0), "ELEVATION slots (privesc)", "crit"))
    out.append(tile(counts.get("critical", 0), "of those: any-user -> root", "crit"))
    out.append(tile(counts.get("high", 0), "hijackable, user-context", "high"))
    out.append(tile(counts.get("low", 0), "protected (LV blocks)", "low"))
    out.append("</div>")

    out.append('<p class="legend"><b>How to read this:</b> the <b>who-can-plant</b> column '
               'names the least-privileged principal who can write each slot (from the '
               'directory&rsquo;s permission bits <i>and any ACL</i>, not from who ran the scan). '
               '<span class="chip crit">PRIVESC -> root</span> = that writer is less privileged '
               'than the process that loads it, and the loader is <b>root</b> &mdash; a true '
               'elevation. <span class="chip high">HIJACKABLE</span> = plantable + library '
               'validation off, but loaded in the writer&rsquo;s own context (no privilege gain). '
               '<span class="chip low">PROTECTED</span> = library validation blocks a foreign '
               'dylib. Tick <b>Elevation only</b> to show just the boundary-crossing cases. '
               '<span class="chip ok">clean</span> binaries are listed at each app&rsquo;s foot.</p>')

    out.append('<div class="toolbar">'
               '<input type="search" id="q" placeholder="Filter apps, binaries, dylibs..." '
               'autocomplete="off" spellcheck="false" aria-label="Filter report">'
               '<label class="elevtoggle"><input type="checkbox" id="elev"> '
               'Elevation (privesc) only</label>'
               '<button type="button" id="ex">Expand all</button>'
               '<button type="button" id="co">Collapse all</button>'
               '<span class="count" id="count"></span></div>')

    for a in apps:
        label, cls = VERDICT_BADGE[a["verdict"]]
        if a["lv_known"]:
            lv = "library validation ON" if a["library_validation"] else "library validation OFF"
            gap = ("unsigned" if not a["signed"] else
                   ("no hardened runtime" if not a["hardened_runtime"] else
                    "disable-library-validation entitlement"))
            gap_txt = "" if a["library_validation"] else f' &middot; gap: {esc(gap)}'
            lv_txt = f' &middot; {esc(lv)}{gap_txt}'
        else:
            lv_txt = ""


        hj, seen = [], set()
        for sev in ("critical", "high"):
            for b in a["binaries"]:
                for r in b["imports"]:
                    if r.get("severity") == sev:
                        bn = os.path.basename(r["import"])
                        if bn not in seen:
                            seen.add(bn); hj.append(bn)
        hj_line = ""
        if hj:
            shown = ", ".join(hj[:6]) + (f" +{len(hj) - 6} more" if len(hj) > 6 else "")
            hj_line = f'<span class="hjnames">{esc(shown)}</span>'

        root_line = ""
        if a["n_critical"] and a.get("root_reason"):
            root_line = f'<span class="rootnote">runs as root &middot; {esc(a["root_reason"])}</span>'

        crit_txt = f'{a["n_critical"]} privesc &middot; ' if a["n_critical"] else ""
        elev_attr = ' data-elev="1"' if a["n_elevation"] else ""
        out.append(f'<details class="app {cls}"{elev_attr}>')
        out.append(f'<summary class="apphead {cls}"><span class="caret"></span>'
                   f'<span class="badge {cls}">{label}</span>'
                   f'<span class="apppath">{esc(collapse_home(a["container"]))}</span>'
                   f'<span class="appmeta">{a["n_binaries"]} binaries &middot; '
                   f'{crit_txt}{a["n_high"]} hijackable &middot; {a["n_low"]} protected{lv_txt}</span>'
                   f'{root_line}{hj_line}</summary>')
        out.append('<div class="appbody">')

        flagged = [b for b in a["binaries"]
                   if b["n_critical"] or b["n_hijackable_high"] or b["n_hijackable_low"]]
        clean = [b for b in a["binaries"]
                 if not (b["n_critical"] or b["n_hijackable_high"] or b["n_hijackable_low"])]

        for b in flagged:
            nc, nh, nl = b["n_critical"], b["n_hijackable_high"], b["n_hijackable_low"]
            if nc:
                bchip = f'<span class="chip crit">{nc} privesc (root)</span>'
            elif nh:
                bchip = f'<span class="chip high">{nh} hijackable</span>'
            else:
                bchip = f'<span class="chip low">{nl} protected</span>'
            rootnote = (f' <span class="rootnote">root &middot; {esc(b["root_reason"])}</span>'
                        if b.get("runs_as_root") and b.get("root_reason") else "")
            belev = ' data-elev="1"' if b["n_elevation"] else ""
            out.append(f'<details class="bin"{belev}>')
            out.append(f'<summary class="binsum"><span class="caret"></span>{bchip}'
                       f'<span class="binname">{esc(b["rel"])}</span>{rootnote}</summary>')
            out.append('<div class="tscroll"><table><thead><tr><th>loaded dylib</th><th>link</th>'
                       '<th>who can plant</th><th>verdict</th><th>detail</th></tr></thead><tbody>')
            for r in sorted(b["imports"], key=imp_sort_key):
                rc = row_class(r)
                if r["verdict"] == "hijackable":
                    v = {"critical": ("PRIVESC -> root", "crit"),
                         "high": ("HIJACKABLE", "high")}.get(r["severity"], ("protected", "low"))
                elif r["verdict"] == "missing":
                    v = ("missing", "missing")
                else:
                    v = ("ok", "ok")
                weak = "weak" if r["weak"] else "strong"
                writer = WRITER_LABEL.get(r.get("writer"), "-") if r["verdict"] == "hijackable" else "-"
                elev_tag = ""
                if r.get("elevation"):
                    elev_tag = f' <span class="elevtag">{esc(r.get("elevation_kind", "privesc"))}</span>'
                relev = ' data-elev="1"' if r.get("elevation") else ""
                detail = r["slot"] if r["slot"] else (r["reason"] or "")
                out.append(f'<tr class="{rc}"{relev}><td class="mono">{esc(r["import"])}</td>'
                           f'<td>{weak}</td><td class="writer">{esc(writer)}</td>'
                           f'<td><span class="chip {v[1]}">{v[0]}</span>{elev_tag}</td>'
                           f'<td class="mono detail">{esc(collapse_home(detail))}</td></tr>')
            out.append("</tbody></table></div></details>")


        if clean:
            out.append('<details class="bin cleanwrap">')
            out.append(f'<summary class="binsum"><span class="caret"></span>'
                       f'<span class="chip ok">clean</span><span class="binname">'
                       f'{len(clean)} clean {"binary" if len(clean)==1 else "binaries"} '
                       f'&middot; no hijackable dylibs</span></summary>')
            out.append('<div class="cleanlist">')
            for b in clean:
                names = " &middot; ".join(esc(os.path.basename(r["import"]))
                                          for r in b["imports"]) or "&mdash;"
                out.append(f'<div class="cbin"><span class="cbinname">{esc(b["rel"])}</span>'
                           f'<span class="cdl">{names}</span></div>')
            out.append("</div></details>")
        out.append("</div></details>")

    out.append(SCRIPT)

    n_root = report.get("n_root", 0)
    root_verdict = ("none of them has a hijackable slot &mdash; no privilege-escalation "
                    "path found" if counts.get("critical", 0) == 0
                    else f'{counts.get("critical", 0)} carry a hijackable slot &mdash; PRIVESC')
    out.append(
        f'<p class="foot"><b>Root-execution context:</b> {format(n_root, ",")} binaries run '
        f'as root (LaunchDaemons, setuid, or privileged helpers); {root_verdict}.<br>'
        f'<b>Full inventory:</b> all '
        f'{format(report.get("n_binaries", 0), ",")} loadable Mach-O binaries (executables, '
        f'dylibs, bundles) found on the volume are listed above, grouped into '
        f'{format(report.get("n_apps", 0), ",")} apps &amp; locations. Clean binaries show their '
        f'loaded dylibs by basename; expand a flagged binary for full paths and slot detail.<br>'
        f'<b>Blind spots:</b> {format(st.get("unreadable_dirs", 0), ",")} directories and '
        f'{format(st.get("unreadable_files", 0), ",")} files were unreadable without elevation; '
        f'system dylibs in the dyld shared cache are not on-disk files (Apple-signed, '
        f'library-validated, out of scope). Scan wall-time {report.get("elapsed_seconds", 0):.0f}s.</p>')
    out.append("</div>")
    return "\n".join(out)


def collapse_home(p):
    home = os.path.expanduser("~")
    return p.replace(home, "~") if isinstance(p, str) else p


def tile(n, label, cls):
    return (f'<div class="tile {cls}"><div class="num">{format(n, ",")}</div>'
            f'<div class="lbl">{esc(label)}</div></div>')


STYLE = """<style>
/* light palette (also the un-stamped default via bare :root) --------------- */
:root{
  --bg:#eef1f4; --card:#ffffff; --panel:#f7f9fb;
  --ink:#12161c; --mut:#5b6672; --faint:#8b96a3; --line:#dde3ea;
  --accent:#2f6f8f;                         /* cool slate-teal, tooling accent */
  --crit:#8f1710; --critbg:#fbe4e1; --critedge:#dd9a92; --critsolid:#9a1a12;
  --high:#b3312a; --highbg:#fbeceb; --highedge:#e7b3ae;
  --low:#8a6410; --lowbg:#fbf3df; --lowedge:#e7d3a0;
  --ok:#2c7a52;  --okbg:#eaf4ee;  --okedge:#bcdcc9;
}
/* system-dark: only prefers-color-scheme, no explicit stamp ----------------- */
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0d0f12; --card:#161a1f; --panel:#12151a;
  --ink:#e6eaef; --mut:#9aa5b1; --faint:#6b7885; --line:#262c34;
  --accent:#6fb3cf;
  --crit:#ff8a7a; --critbg:#3f1512; --critedge:#7a2c23; --critsolid:#c0392b;
  --high:#ff7a6d; --highbg:#341917; --highedge:#5a2620;
  --low:#e6b653; --lowbg:#2f2711; --lowedge:#4d3f19;
  --ok:#6bd39a; --okbg:#122619; --okedge:#20402d;
}}
/* explicit toggles win in both directions ---------------------------------- */
:root[data-theme="dark"]{
  --bg:#0d0f12; --card:#161a1f; --panel:#12151a;
  --ink:#e6eaef; --mut:#9aa5b1; --faint:#6b7885; --line:#262c34;
  --accent:#6fb3cf;
  --crit:#ff8a7a; --critbg:#3f1512; --critedge:#7a2c23; --critsolid:#c0392b;
  --high:#ff7a6d; --highbg:#341917; --highedge:#5a2620;
  --low:#e6b653; --lowbg:#2f2711; --lowedge:#4d3f19;
  --ok:#6bd39a; --okbg:#122619; --okedge:#20402d;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);margin:0;
  font-family:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:1040px;margin:0 auto;padding:40px 22px 72px}
.mast{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
  border-bottom:2px solid var(--ink);padding-bottom:14px;margin-bottom:6px}
h1{font-size:23px;font-weight:700;letter-spacing:-.01em;margin:0;text-wrap:balance}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:11px;font-weight:500;
  text-transform:uppercase;letter-spacing:.14em;color:var(--accent)}
.sub{color:var(--mut);margin:10px 0 26px;font-size:14px}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:22px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 16px 14px;position:relative}
.tile::before{content:"";position:absolute;left:0;top:12px;bottom:12px;width:3px;border-radius:2px;background:var(--faint)}
.tile.high::before{background:var(--high)} .tile.low::before{background:var(--low)}
.tile .num{font-family:"IBM Plex Mono",monospace;font-size:29px;font-weight:600;
  font-variant-numeric:tabular-nums;line-height:1;padding-left:8px}
.tile.crit::before{background:var(--critsolid)} .tile.crit .num{color:var(--crit)}
.tile.high .num{color:var(--high)} .tile.low .num{color:var(--low)}
.tile .lbl{color:var(--mut);font-size:12.5px;padding-left:8px;margin-top:6px}
.legend{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:12px 15px;font-size:13px;color:var(--mut);line-height:1.6}
.chip{display:inline-block;padding:1px 8px;border-radius:4px;font-family:"IBM Plex Mono",monospace;
  font-size:10.5px;font-weight:600;letter-spacing:.03em;vertical-align:middle;
  border:1px solid transparent}
.chip.crit{background:var(--critsolid);color:#fff;border-color:var(--critsolid)}
.chip.high{background:var(--highbg);color:var(--high);border-color:var(--highedge)}
.chip.low{background:var(--lowbg);color:var(--low);border-color:var(--lowedge)}
.chip.ok{background:var(--okbg);color:var(--ok);border-color:var(--okedge)}
.chip.missing{background:transparent;color:var(--faint);border-color:var(--line)}
.toolbar{display:flex;gap:8px;margin-bottom:4px;align-items:center;flex-wrap:wrap;
  position:sticky;top:0;z-index:5;background:var(--bg);padding:8px 0}
#q{flex:1;min-width:200px;font-family:"IBM Plex Sans",sans-serif;font-size:13px;color:var(--ink);
  background:var(--card);border:1px solid var(--line);border-radius:6px;padding:7px 11px}
#q::placeholder{color:var(--faint)}
#q:focus{outline:none;border-color:var(--accent)}
.toolbar button{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--mut);
  background:var(--card);border:1px solid var(--line);border-radius:6px;padding:6px 11px;cursor:pointer}
.toolbar button:hover{color:var(--ink);border-color:var(--faint)}
.toolbar button:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.count{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--mut)}
.elevtoggle{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--mut);
  font-family:"IBM Plex Mono",monospace;cursor:pointer;white-space:nowrap}
.elevtoggle input{accent-color:var(--critsolid)}
.writer{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--mut);white-space:nowrap}
.elevtag{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:10px;font-weight:600;
  color:var(--crit);white-space:nowrap;margin-left:4px}
details.app{background:var(--card);border:1px solid var(--line);border-radius:10px;margin-top:12px;overflow:hidden}
summary{list-style:none;cursor:pointer}
summary::-webkit-details-marker{display:none}
summary:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.caret{display:inline-block;width:0;height:0;border-left:5px solid var(--faint);
  border-top:4px solid transparent;border-bottom:4px solid transparent;
  margin-right:2px;transition:transform .15s ease;flex:none}
details[open]>summary .caret{transform:rotate(90deg)}
.apphead{padding:14px 16px 14px 16px;border-left:4px solid var(--faint);
  display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.apphead:hover{background:var(--panel)}
.apphead.crit{border-left-color:var(--critsolid)}
.apphead.high{border-left-color:var(--high)}
.apphead.low{border-left-color:var(--low)}
.apphead.ok{border-left-color:var(--ok)}
.hjnames{width:100%;font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--high);word-break:break-all}
.rootnote{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--crit);font-weight:600}
.apphead .rootnote{width:100%}
.appbody{border-top:1px solid var(--line)}
details.bin{border-bottom:1px solid var(--line)}
details.bin:last-child{border-bottom:none}
.binsum{display:flex;align-items:center;gap:9px;padding:9px 16px;font-family:"IBM Plex Mono",monospace;font-size:12px}
.binsum:hover{background:var(--panel)}
.binsum .binname{color:var(--ink);font-weight:500;word-break:break-all}
.cleanwrap>summary .binname{color:var(--mut)}
.cleanlist{padding:2px 16px 12px 34px}
.cbin{padding:5px 0;border-top:1px solid var(--line);display:flex;flex-wrap:wrap;gap:2px 12px}
.cbin:first-child{border-top:none}
.cbinname{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--ink);font-weight:500;word-break:break-all}
.cdl{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--faint);word-break:break-all}
@media(prefers-reduced-motion:reduce){.caret{transition:none}}
.badge{font-family:"IBM Plex Mono",monospace;font-size:10.5px;font-weight:600;
  padding:3px 9px;border-radius:5px;letter-spacing:.04em;border:1px solid transparent}
.badge.crit{background:var(--critsolid);color:#fff;border-color:var(--critsolid)}
.badge.high{background:var(--highbg);color:var(--high);border-color:var(--highedge)}
.badge.low{background:var(--lowbg);color:var(--low);border-color:var(--lowedge)}
.badge.ok{background:var(--okbg);color:var(--ok);border-color:var(--okedge)}
.apppath{font-weight:600;font-size:14px;word-break:break-all}
.appmeta{color:var(--mut);font-size:12px;width:100%;font-family:"IBM Plex Mono",monospace}
.tscroll{overflow-x:auto;border-top:1px solid var(--line)}
table{width:100%;border-collapse:collapse;font-size:12.5px;min-width:640px}
thead th{text-align:left;color:var(--faint);font-weight:600;padding:6px 16px;
  border-bottom:1px solid var(--line);font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;
  font-family:"IBM Plex Mono",monospace}
tbody td{padding:7px 16px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:none}
tr.crit{background:var(--critbg)} tr.high{background:var(--highbg)} tr.low{background:var(--lowbg)}
.mono{font-family:"IBM Plex Mono",monospace;font-size:11.5px;word-break:break-all}
.detail{color:var(--mut);max-width:380px}
.foot{color:var(--faint);font-size:12px;margin-top:26px;border-top:1px solid var(--line);
  padding-top:14px;line-height:1.6}
@media(max-width:640px){.tiles{grid-template-columns:repeat(2,1fr)}.detail{max-width:none}}
</style>"""


SCRIPT = """<script>
(function(){
  var q=document.getElementById('q'), count=document.getElementById('count'),
      elev=document.getElementById('elev');
  var apps=[].slice.call(document.querySelectorAll('details.app'));
  for(var b of [['ex',true],['co',false]]){
    document.getElementById(b[0]).addEventListener('click',(function(v){return function(){
      for(var d of document.querySelectorAll('details'))d.open=v;};})(b[1]));
  }
  function norm(s){return s.toLowerCase();}
  function filter(){
    var term=norm(q.value.trim()), eo=elev.checked;
    var shownApps=0, shownRows=0;
    apps.forEach(function(app){
      var header=norm(app.querySelector('summary.apphead').textContent);
      var appVis=false;
      app.querySelectorAll('details.bin').forEach(function(bin){
        var bsum=norm(bin.querySelector('summary.binsum').textContent);
        var rows=bin.querySelectorAll('tbody tr');
        var binVis=false;
        rows.forEach(function(tr){
          var matchOK=!term||header.indexOf(term)>=0||bsum.indexOf(term)>=0||norm(tr.textContent).indexOf(term)>=0;
          var elevOK=!eo||tr.getAttribute('data-elev')==='1';
          var show=matchOK&&elevOK;
          tr.style.display=show?'':'none';
          if(show){binVis=true; shownRows++;}
        });
        var isClean=rows.length===0, bshow;
        if(eo){bshow=binVis;}
        else if(isClean){bshow=!term||bsum.indexOf(term)>=0||header.indexOf(term)>=0;}
        else{bshow=binVis||bsum.indexOf(term)>=0||header.indexOf(term)>=0;}
        bin.style.display=bshow?'':'none';
        bin.open=(term||eo)?bshow:false;
        if(bshow)appVis=true;
      });
      var ashow=eo?appVis:(appVis||header.indexOf(term)>=0);
      app.style.display=ashow?'':'none';
      app.open=(term||eo)?ashow:false;
      if(ashow)shownApps++;
    });
    count.textContent=(term||eo)?(shownApps+' apps, '+shownRows+' dylibs'):'';
  }
  q.addEventListener('input',filter);
  elev.addEventListener('change',filter);
  q.addEventListener('keydown',function(e){if(e.key==='Escape'){q.value='';filter();}});
})();
</script>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("findings_json")
    ap.add_argument("--json", help="write structured report JSON here")
    ap.add_argument("--html", help="write HTML report here")
    ap.add_argument("--match", action="append", metavar="SUBSTR",
                    help="Only include apps/binaries whose path contains SUBSTR "
                         "(case-insensitive; repeatable). E.g. --match claude.")
    args = ap.parse_args()
    report = build(args.findings_json)
    if args.match:
        report = filter_report(report, args.match)
        print(f"scoped to {args.match}: {report['n_apps']} apps, "
              f"{report['n_binaries']} binaries")
    if args.json:
        json.dump(report, open(args.json, "w"), indent=2)
        print("report JSON:", args.json)
    if args.html:
        open(args.html, "w").write(render_html(report))
        print("report HTML:", args.html)
    if not args.json and not args.html:
        json.dump(report, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
