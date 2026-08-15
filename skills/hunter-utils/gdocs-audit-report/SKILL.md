---
name: gdocs-audit-report
description: Expert skill for creating, formatting, and maintaining security audit reports in Google Docs via the Docs API. Use when asked to write, update, style, or fix an audit report document - including finding formatting, summary tables, inline code styling, bullet conversion, cross-reference hyperlinks, and severity color schemes. Covers auth, index-drift safety, and all common formatting pitfalls.
---

# Google Docs Security Audit Report

## Overview

This skill provides patterns, constants, and gotcha-avoidance for building and maintaining security audit reports in Google Docs using the Docs API (service account auth). It encodes hard-won lessons around index drift, code styling multi-pass, paragraph vs text backgrounds, heading anchor URLs, and cross-reference linking.

Always read `references/api-patterns.md` and `references/formatting-standards.md` before writing any script.

## Workflow

```
1. Auth          → make_token() from scripts/gdocs_auth.py
2. get_doc()     → fresh snapshot before EVERY batch of edits
3. Build ops     → sort ALL ops highest-index-first
4. do_batch()    → send in chunks of ≤50
5. Verify        → get_doc() again and spot-check changed ranges
```

## Critical Gotchas (read these first)

### 1. Index drift
Any insert/delete shifts every index above it. **Always sort ops high→low. Always get_doc() fresh.**

### 2. Text bg ≠ paragraph bg
`updateTextStyle.backgroundColor` only covers character width - leaves white gaps between lines in code blocks. Use `updateParagraphStyle.shading.backgroundColor` + `spaceAbove/Below: 0` for full-width code block backgrounds.

### 3. headingId already has `h.` prefix
Anchor URL = `#heading={headingId}` - **not** `#heading=h.{headingId}`.

### 4. Code styling needs multiple passes
After `updateTextStyle` splits a run, new unstyled sub-runs appear. Always do a second full-doc re-scan after the first styling pass.

### 5. Sort code terms longest-first
Prevents `maxRelayFeeBPS` matching before `assetConfig.maxRelayFeeBPS` and leaving a partial un-styled prefix.

### 6. Backtick removal order (per segment, high→low)
Delete closing backtick → style inner → delete opening backtick - all in one batch.

### 7. Bullet conversion
`createParagraphBullets` does not change indices. Then `deleteContentRange` the `- ` prefix high→low in a second batch.

### 8. Cross-reference links: skip only already-linked runs
Scan ALL runs for `X-NN` regex - **only skip** runs where `textStyle.link` is already set. Do NOT also filter by font (Courier runs can contain xrefs too).

### 9. Table cell content replace
Delete to `elements[-1].endIndex - 1` (keep the required trailing `\n`), then insert. Sort delete (higher) before insert (lower) in same batch.

### 10. replaceAllText for bulk renames
Use `replaceAllText` for ID renames (e.g. renumbering findings). Same-length replacements are index-safe. Do in one batch, longest/most-specific strings first.

## Formatting Standards

See `references/formatting-standards.md` for:
- Severity RGB colors (Critical, High, Medium, Low, Unmitigated)
- Heading purple, code purple, code bg gray
- Finding structure template
- Summary table column definitions
- Finding ID scheme (`C-01`, `H-01`, etc.)

## API Patterns

See `references/api-patterns.md` for:
- Auth boilerplate
- All common op templates (style, delete, insert, hyperlink, bullets, paragraph shading)
- Heading anchor URL construction
- Cross-reference linking pattern
- Inline code multi-pass approach

## Resources

- `scripts/gdocs_auth.py` - reusable auth + get_doc + do_batch helpers
- `references/api-patterns.md` - op templates and patterns
- `references/formatting-standards.md` - colors, typography, structure constants
- `references/how-to-create-google-service-account.md` - one-time setup: instruct the user to create a service account, advise the user to restrict it to the AI-only Drive folder/file (via google share feature), and provide the JSON key path
