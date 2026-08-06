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


def split_frontmatter(text):
    text = text.lstrip("﻿")
    if not text.startswith("---"):
        return None, ""
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None, ""
    return yaml.safe_load(parts[1]) or {}, parts[2]


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


def recurrence_check(path, fm):
    # A recurring cadence (interval/cron/self-paced) that only bounds a single run (max_turns)
    # would restart forever - it must also be bounded across runs.
    cadence = fm.get("cadence") or {}
    trigger = cadence.get("trigger")
    if trigger not in ("interval", "cron", "self-paced"):
        return
    term = fm.get("termination") or {}
    stop_on = term.get("stop_on") or []
    if term.get("max_runs") is None and not term.get("max_duration") and not stop_on:
        add(path, f"cadence.trigger '{trigger}' is recurring but termination has no cross-run bound "
                  f"(set max_runs, max_duration, or stop_on; max_turns only bounds one run)")


def extract_meta(js):
    start = js.find("export const meta")
    if start == -1:
        start = js.find("const meta")
    if start == -1:
        return None
    brace = js.find("{", start)
    if brace == -1:
        return None
    depth = 0
    end = brace
    for i in range(brace, len(js)):
        if js[i] == "{":
            depth += 1
        elif js[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    obj = js[brace:end + 1]
    meta = {}
    for key in ("name", "description"):
        match = re.search(r"\b" + key + r"\s*:\s*['\"`]([^'\"`]*)['\"`]", obj, re.DOTALL)
        if match:
            meta[key] = match.group(1)
    phases = []
    pi = obj.find("phases")
    if pi != -1:
        for match in re.finditer(r"title\s*:\s*['\"`]([^'\"`]*)['\"`]", obj[pi:]):
            phases.append({"title": match.group(1)})
    meta["phases"] = phases
    return meta


for path in ROOT.rglob("SKILL.md"):
    counts["skill"] += 1
    fm, _ = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
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
    if fm is None:
        add(path, "missing YAML frontmatter")
        continue
    if report(path, LOOP, fm):
        drift_check(path, fm, body)
        recurrence_check(path, fm)

for path in ROOT.rglob("*.js"):
    if path.name.lower().endswith(".min.js"):
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if "const meta" not in text:
        continue
    counts["workflow"] += 1
    meta = extract_meta(text)
    if meta is None:
        add(path, "meta block present but could not be parsed")
        continue
    report(path, WORKFLOW, meta)

summary = f"skills={counts['skill']} loops={counts['loop']} workflows={counts['workflow']}"
if errors:
    print(f"schema check FAILED ({summary})")
    for line in errors:
        print(f"  {line}")
    sys.exit(1)
print(f"schema check OK ({summary})")
