#!/usr/bin/env python3
"""Validate in-document markdown anchor links against GitHub's heading slugs.

A file containing `<!-- anchor-check: ignore ... -->` is skipped, for templates whose
table of contents is an illustration rather than a live set of links.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

# github-slugger's punctuation class: strips control characters and ASCII
# punctuation while preserving hyphen and underscore, then spaces become hyphens.
PUNCT = re.compile(
    "[\u0000-\u001f!-,\\./:-@\\[-\\^`{- ¡§«¶·"
    "»¿;·՚-՟]"
)
HEADING = re.compile(r"^#{1,6}\s+(.*\S)\s*$")
LINK = re.compile(r"\]\(#([^)]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
IGNORE = "<!-- anchor-check: ignore"


def slug(text):
    return PUNCT.sub("", text.lower().strip()).replace(" ", "-")


def anchors(lines):
    seen, valid = {}, set()
    in_fence = False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if not match:
            continue
        base = slug(match.group(1))
        count = seen.get(base, 0)
        seen[base] = count + 1
        valid.add(f"{base}-{count}" if count else base)
    return valid


errors = []
checked = files = 0

for path in sorted(ROOT.rglob("*.md")):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if IGNORE in text:
        continue
    files += 1
    valid = anchors(text.splitlines())
    for line_no, line in enumerate(text.splitlines(), 1):
        for match in LINK.finditer(line):
            checked += 1
            if match.group(1) not in valid:
                near = [v for v in valid if re.sub("-+", "-", v) == re.sub("-+", "-", match.group(1))]
                hint = f" (did you mean #{near[0]}?)" if len(near) == 1 else ""
                errors.append(f"{path.relative_to(ROOT).as_posix()}:{line_no} broken anchor #{match.group(1)}{hint}")

summary = f"files={files} anchors={checked}"
if errors:
    print(f"anchor check FAILED ({summary})")
    for line in errors:
        print(f"  {line}")
    sys.exit(1)
print(f"anchor check OK ({summary})")
