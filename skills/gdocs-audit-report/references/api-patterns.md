# Google Docs API Patterns — Audit Report

## Table of Contents

- [Auth](#auth)
- [Index Drift — The Golden Rule](#index-drift--the-golden-rule)
- [Common Op Templates](#common-op-templates)
  - [Style a text range](#style-a-text-range)
  - [Delete a range](#delete-a-range)
  - [Insert text](#insert-text)
  - [Replace table cell content](#replace-table-cell-content)
  - [Apply hyperlink](#apply-hyperlink)
  - [Create paragraph bullets](#create-paragraph-bullets)
  - [Full-width paragraph background (code blocks)](#full-width-paragraph-background-code-blocks)
- [Heading Anchor URLs](#heading-anchor-urls)
- [Inline Code Styling (multi-pass approach)](#inline-code-styling-multi-pass-approach)
- [Removing Backtick-Wrapped Code](#removing-backtick-wrapped-code)
- [Cross-Reference Hyperlinks](#cross-reference-hyperlinks)

---

## Auth

Service account key (JSON) → RS256 JWT → OAuth2 Bearer token.
Always use `ssl._create_unverified_context()`. Token expires in 1h.
See `scripts/gdocs_auth.py` for the reusable helper.

```python
from gdocs_auth import make_token, get_doc, do_batch
# Don't blindly run, ask the user for the actual service account file path
TOKEN = make_token("/path/to/service-account-key.json")
doc   = get_doc(DOC_ID, TOKEN)
```

---

## Index Drift — The Golden Rule

**Every insert or delete shifts all indices above it.**

- Always call `get_doc()` fresh before building ops.
- Sort all ops **highest index first** before sending.
- Never reuse stale indices after any mutation.
- Combine independent same-direction ops into one batch when safe.

---

## Common Op Templates

### Style a text range

```python
{"updateTextStyle": {
    "range": {"startIndex": si, "endIndex": ei},
    "textStyle": { ... },
    "fields": "bold,weightedFontFamily,foregroundColor,backgroundColor"
}}
```

### Delete a range

```python
{"deleteContentRange": {"range": {"startIndex": si, "endIndex": ei}}}
```

### Insert text

```python
{"insertText": {"location": {"index": si}, "text": "new text"}}
```

### Replace table cell content

```python
# 1. Get cell content range:
first_el = cell["content"][0]["paragraph"]["elements"][0]
last_el  = cell["content"][-1]["paragraph"]["elements"][-1]
text_si  = first_el["startIndex"]
text_ei  = last_el["endIndex"] - 1   # -1 preserves required trailing \n

# 2. Delete then insert (high→low: delete first since it's higher if appending)
ops = [
    {"deleteContentRange": {"range": {"startIndex": text_si, "endIndex": text_ei}}},
    {"insertText": {"location": {"index": text_si}, "text": "new value"}},
]
```

### Apply hyperlink

```python
{"updateTextStyle": {
    "range": {"startIndex": si, "endIndex": ei},
    "textStyle": {"link": {"url": url}},
    "fields": "link"
}}
```

### Create paragraph bullets

```python
{"createParagraphBullets": {
    "range": {"startIndex": si, "endIndex": ei - 1},
    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
}}
# Then delete leading "- " (2 chars) from each converted paragraph, high→low
```

### Full-width paragraph background (code blocks)

```python
{"updateParagraphStyle": {
    "range": {"startIndex": si, "endIndex": ei},
    "paragraphStyle": {
        "shading": {"backgroundColor": {"color": {"rgbColor": LIGHT_GRAY}}},
        "spaceAbove": {"magnitude": 0, "unit": "PT"},
        "spaceBelow": {"magnitude": 0, "unit": "PT"},
    },
    "fields": "shading,spaceAbove,spaceBelow"
}}
```

> **Note:** `updateTextStyle.backgroundColor` only highlights text characters (not full line width).
> Use `updateParagraphStyle.shading` for full-width code block backgrounds.

---

## Heading Anchor URLs

`headingId` in `paragraphStyle` **already includes the `h.` prefix**.

```python
heading_id = para["paragraphStyle"]["headingId"]  # e.g. "h.vbzwjo2n54rj"
url = f"https://docs.google.com/document/d/{DOC_ID}/edit#heading={heading_id}"
# NOT: #heading=h.{heading_id}  ← double-prefix bug
```

---

## Inline Code Styling (multi-pass approach)

**Problem:** After styling a sub-range in a run, the run splits. Re-scanning finds new unstyled runs.

**Solution:** Always do at least 2 passes:

1. First pass — style all known terms using `updateTextStyle` on specific ranges
2. Second pass — re-scan doc for any remaining plain runs containing missed terms

**Term matching:** Sort terms **longest first** to avoid partial overlaps.

```python
CODE_TERMS = sorted([...], key=len, reverse=True)
```

**Word boundary check:** Skip for terms containing `.()[]{}/:'"#@* ` — only check boundaries for plain identifiers.

---

## Removing Backtick-Wrapped Code

Process each `` `inner` `` segment high→low within one batch:

1. `deleteContentRange` closing backtick (highest index)
2. `updateTextStyle` inner text
3. `deleteContentRange` opening backtick (lowest index)

---

## Cross-Reference Hyperlinks

Find `X-NN` patterns in any run that is **not already a hyperlink** (regardless of font):

```python
import re
XREF_RE = re.compile(r'\b[A-Z]-\d{2}\b')
# Map headingId -> title by scanning HEADING_1 paragraphs first
# Only skip runs where ts.get('link') is already set
# Do NOT restrict to plain/non-Courier runs — the ref can appear in any styled text
# Apply updateTextStyle: link + bold to each match
```

> **Common mistake:** Filtering out Courier New runs causes misses when a finding ID appears
> inside a code-styled sentence (e.g. "path confirmed in C-03").
