# Formatting Standards - Security Audit Report

## Severity Colors (RGB 0-1 scale)

| Severity    | Red   | Green | Blue  | Hex       |
|-------------|-------|-------|-------|-----------|
| Critical    | 0.820 | 0.157 | 0.157 | #D12828   |
| High        | 0.918 | 0.545 | 0.196 | #EA8B32   |
| Medium      | 0.965 | 0.761 | 0.259 | #F6C242   |
| Low         | 0.278 | 0.651 | 0.455 | #47A674   |
| Unmitigated | 0.918 | 0.545 | 0.196 | same as High |

## Typography

| Element         | Font       | Size  | Style       | Color              |
|----------------|------------|-------|-------------|---------------------|
| Finding heading | Roboto     | -     | HEADING_1   | Red `#e06666` `(0.439, 0.188, 0.627)` |
| Body labels     | -          | -     | Bold        | (same as severity)  |
| Inline code     | Courier New| -     | Bold        | Red `#e06666` `(0.447, 0.353, 0.675)` |
| Code background | -          | -     | -           | Gray `#EDEDED` `(0.929, 0.929, 0.929)` |

## Finding Structure (per finding)

```
[HEADING_1 red bold]  X-NN: Title

Severity:   [severity color bold]  Critical / High / Medium / Low
Status:     [orange if Unmitigated, else normal]  Unmitigated / Pending Retest / Mitigated

Code:
  [hyperlink to GitHub]  repo/path/to/file.ts#L10-L20

Description:
  [body text, 1.5× line spacing]

Attack Flow:
  [body text]

Recommendations:
  [bullet list]
```

## Summary Table Columns

| # | Column      | Notes                                           |
|---|-------------|--------------------------------------------------|
| 0 | Finding     | Full title, hyperlinked to heading anchor        |
| 1 | Repo        | shieldflow-website / shieldflow-core / shieldflow-asp |
| 2 | Component   | e.g. Relayer Proxy API, SDK, CI/CD, AWS IAM      |
| 3 | Risk Level  | Severity color applied to cell text             |
| 4 | Status      | Unmitigated = High orange; others = normal       |

Table line spacing: 1.15×

## Finding ID Scheme

Per-severity sequential reset: `C-01..C-NN`, `H-01..H-NN`, `M-01..M-NN`, `L-01..L-NN`

Order in doc: Criticals → Highs → Mediums → Lows

## Bullet Style

Use Google Docs native list bullets (`BULLET_DISC_CIRCLE_SQUARE`), never plain `- ` dashes.
18pt left indent for bullet paragraphs.

## Code Block (multi-line)

Consecutive code-line paragraphs should have:
- `updateParagraphStyle.shading.backgroundColor` = `#EDEDED`
- `spaceAbove` = `spaceBelow` = 0 PT
- All text runs: Courier New bold, red `#e06666`, bg `#EDEDED`

## keepWithNext

Apply `keepWithNext: true` to label paragraphs (Description:, Attack Flow:, Recommendations:, Code:)
so they don't orphan at the bottom of a page.
