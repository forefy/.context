#!/usr/bin/env python3
import json
import pathlib
import re
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SCHEMAS = pathlib.Path(__file__).resolve().parent.parent / "schemas"

errors = []
counts = {"skill": 0, "loop": 0, "workflow": 0}


def load(name):
    return Draft202012Validator(json.loads((SCHEMAS / name).read_text()))


SKILL = load("skill.schema.json")
LOOP = load("loop.schema.json")
WORKFLOW = load("workflow.schema.json")


def rel(path):
    return path.relative_to(ROOT).as_posix()


def add(path, message):
    errors.append(f"{rel(path)}: {message}")


class FrontmatterError(str):
    """Sentinel returned in place of parsed frontmatter when the YAML is invalid.

    Carries the (single-line) parser message so the caller can report it.
    """


def _yaml_message(exc):
    parts = []
    if getattr(exc, "problem", None):
        parts.append(exc.problem.strip())
    mark = getattr(exc, "problem_mark", None)
    if mark is not None:
        parts.append(f"(line {mark.line + 1}, column {mark.column + 1})")
    return " ".join(parts) or " ".join(str(exc).split())


def split_frontmatter(text):
    text = text.lstrip("﻿")
    if not text.startswith("---"):
        return None, ""
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None, ""
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        return FrontmatterError(_yaml_message(exc)), parts[2]
    return data or {}, parts[2]


def report(path, validator, data):
    ok = True
    for err in validator.iter_errors(data):
        location = "/".join(str(p) for p in err.path) or "(root)"
        add(path, f"{location}: {err.message}")
        ok = False
    return ok


def condition_of(fm, body):
    condition = (fm.get("condition") or "").strip()
    if condition:
        return condition
    marker = body.find("/goal")
    if marker == -1:
        return ""
    line = body[marker + len("/goal"):].splitlines()
    return line[0].strip().strip("`").strip() if line else ""


def drift_check(path, fm, body):
    guardrail = fm.get("guardrail") or {}
    allowed = [p.strip() for p in (guardrail.get("allowed_paths") or []) if p and p.strip()]
    if not allowed:
        return
    condition = condition_of(fm, body)
    if not condition:
        return
    missing = [p for p in allowed if p not in condition]
    if missing:
        add(path, f"guardrail allowed_paths {missing} absent from the /goal condition (drift)")


class MetaError(str):
    """Sentinel returned by extract_meta when a `meta` block is present but unparseable.

    Carries a human message (with a line/column position where useful).
    """


def _line_col(text, index):
    """1-based (line, column) of offset `index` in `text`."""
    prefix = text[:index]
    return prefix.count("\n") + 1, index - (prefix.rfind("\n") + 1) + 1


def _match_brace(text, open_idx):
    """Index of the `}` matching the `{` at open_idx, skipping braces inside
    '...' / "..." / `...` string literals (honoring backslash escapes). None if unbalanced.

    A plain depth counter miscounts a brace that appears inside a description string and
    slices the object at the wrong place; this mirrors di3's match_bracket so both agree.
    """
    depth = 0
    quote = None
    i = open_idx
    while i < len(text):
        c = text[i]
        if quote is not None:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "'\"`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def _read_quoted_value(text, start, quote):
    """Unescape a JS string literal from offset `start` (first char after the opening
    quote) up to the matching unescaped `quote`. `\\n`/`\\t`/`\\r` become their control
    chars; any other escaped char passes through as its literal.

    The old `['\"`]([^'\"`]*)['\"`]` regex stopped at the first quote byte, so an escaped
    quote inside a value (e.g. `keeps tiny-auditor\\'s judgment`) silently truncated it.
    """
    out = []
    i = start
    while i < len(text):
        c = text[i]
        if c == "\\":
            nxt = text[i + 1] if i + 1 < len(text) else ""
            out.append({"n": "\n", "t": "\t", "r": "\r"}.get(nxt, nxt))
            i += 2
            continue
        if c == quote:
            break
        out.append(c)
        i += 1
    return "".join(out)


def _read_quoted_field(obj, key):
    """Value of `key: '...'` in obj with escape handling, or None if absent."""
    match = re.search(r"\b" + re.escape(key) + r"\s*:\s*(['\"`])", obj, re.DOTALL)
    if not match:
        return None
    return _read_quoted_value(obj, match.end(), match.group(1))


META_DECL = re.compile(r"\b(?:export\s+)?const meta\b")


def extract_meta(js):
    block = META_DECL.search(js)
    if block is None:
        return None
    start = block.start()
    brace = js.find("{", start)
    if brace == -1:
        return MetaError("meta block has no opening brace")
    end = _match_brace(js, brace)
    if end is None:
        line, col = _line_col(js, brace)
        return MetaError(f"meta block has unbalanced braces (opens at line {line}, column {col})")
    obj = js[brace:end + 1]
    name = _read_quoted_field(obj, "name")
    if name is None:
        line, col = _line_col(js, brace)
        return MetaError(f"meta.name missing or not a quoted string (meta block at line {line}, column {col})")
    meta = {"name": name}
    description = _read_quoted_field(obj, "description")
    if description is not None:
        meta["description"] = description
    phases = []
    pi = obj.find("phases")
    if pi != -1:
        tail = obj[pi:]
        for match in re.finditer(r"\btitle\s*:\s*(['\"`])", tail, re.DOTALL):
            phases.append({"title": _read_quoted_value(tail, match.end(), match.group(1))})
    meta["phases"] = phases
    return meta


for path in ROOT.rglob("SKILL.md"):
    counts["skill"] += 1
    fm, _ = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    if isinstance(fm, FrontmatterError):
        add(path, f"invalid YAML frontmatter: {fm}. Wrap any value containing ':' or other YAML-special characters in double quotes.")
        continue
    if fm is None:
        add(path, "missing YAML frontmatter")
        continue
    report(path, SKILL, fm)

for path in ROOT.rglob("*.md"):
    name = path.name.lower()
    if not (name == "loop.md" or name.endswith(".loop.md")):
        continue
    counts["loop"] += 1
    fm, body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    if isinstance(fm, FrontmatterError):
        add(path, f"invalid YAML frontmatter: {fm}. Wrap any value containing ':' or other YAML-special characters in double quotes.")
        continue
    if fm is None:
        add(path, "missing YAML frontmatter")
        continue
    if report(path, LOOP, fm):
        drift_check(path, fm, body)

for path in ROOT.rglob("*.js"):
    if path.name.lower().endswith(".min.js"):
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if not META_DECL.search(text):
        continue
    counts["workflow"] += 1
    meta = extract_meta(text)
    if isinstance(meta, MetaError):
        add(path, f"invalid workflow meta: {meta}. Check the quoting and braces of the `export const meta` block.")
        continue
    if meta is None:
        # No `meta` block after all - not a workflow. The outer guard already required the
        # "const meta" substring, so this is a defensive no-op rather than a parse failure.
        counts["workflow"] -= 1
        continue
    report(path, WORKFLOW, meta)

summary = f"skills={counts['skill']} loops={counts['loop']} workflows={counts['workflow']}"
if errors:
    print(f"schema check FAILED ({summary})")
    for line in errors:
        print(f"  {line}")
    sys.exit(1)
print(f"schema check OK ({summary})")
