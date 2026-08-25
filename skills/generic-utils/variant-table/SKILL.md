---
name: variant-table
description: >-
  Render any draft copy as a comparison table - one row per logical unit (paragraph, line, bullet, cell, section), with 3 genuinely distinct rewrite variations per row plus a final "top pick" column. Use whenever the user is iterating on wording and wants options laid out side by side to compare and choose: LinkedIn/X posts, taglines, headlines, email lines, ad copy, bios, CTAs, product blurbs, doc sentences, commit messages, error strings, UI microcopy. Triggers on "give me variations", "show me options in a table", "compare rewrites", "3 versions of each line", "table with a pick column", or any request to optimize copy unit by unit.
---

# Variant Table

Turn a piece of draft copy into a side-by-side comparison table so the user can compare wording options per unit and pick.

## When to use

Any time the user is refining wording and would benefit from seeing distinct options laid out rather than a single rewrite. Works for any content type: social posts, headlines, taglines, email lines, bios, CTAs, microcopy, doc sentences, spec bullets, commit messages. Content-agnostic - never assume it is a LinkedIn post.

## Output format

A markdown table. One row per logical unit of the source. Columns:

| # | Current | A - <angle> | B - <angle> | C - <angle> | My pick |

- **#** - unit index plus a 1-2 word role label in parens, e.g. `1 (hook)`, `4 (CTA)`, `2 (bullet)`. The label names the unit's job, inferred from the content.
- **Current** - the user's existing text for that unit, verbatim. If the user gave no existing draft, leave a short placeholder or omit this column.
- **A / B / C** - three rewrites. See the distinctness rule below. Rename the angle after the dash per row to whatever actually differs (e.g. `A - blunt`, `B - contrarian`, `C - technical`).
- **My pick** - one recommendation for that row, in **bold**. It may be one of A/B/C, the current text ("keep"), or a fresh hybrid. Add a terse parenthetical reason only when it aids the choice.

## The distinctness rule (most important)

The three variations must differ in **approach**, not just word swaps. Before writing a row, pick three different axes and commit one variation to each. Draw from axes like:

- tone: blunt / playful / formal / contrarian
- structure: statement / question / fragment / story-fragment
- angle: pain-first / benefit-first / curiosity-gap / social-proof / technical-precision
- length: terse vs flowing

If two variations could be swapped without a reader noticing a shift in strategy, they are too similar - rewrite one. Label each column with the axis it took so the contrast is legible.

## How to segment

Split the source into the units the user is actually deciding on:
- prose → paragraphs (or sentences if they're iterating sentence-level)
- list → bullets
- headline + subhead → separate rows
- table/form → cells or fields

When unsure of granularity, match whatever unit the user referenced last, or ask if it's ambiguous.

## Style

- Match the user's established preferences (terse, no em dashes in the copy itself, etc.). The `-` in column headers is a label separator, fine to keep, but keep it out of the generated copy if the user dislikes it.
- Keep every cell tight. A variant is a candidate line, not a paragraph of explanation.
- Do not pad to three if the unit is trivial (e.g. a URL); mark it "keep".
- After the table, offer to stitch the picks (or a chosen column) into a clean final draft.

## Example shape

| # | Current | A - blunt | B - contrarian | C - curiosity | My pick |
|---|---------|-----------|----------------|---------------|-----------|
| 1 (hook) | We help teams ship faster. | Ship faster. Full stop. | Most "ship faster" tools slow you down. | What if your slowest step wasn't code? | **Most "ship faster" tools slow you down.** |

Then: "Say the word and I'll stitch the pick column into a final draft."
