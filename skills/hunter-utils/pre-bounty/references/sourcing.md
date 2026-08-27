# Sourcing scope & signals per platform

Goal: fill, for every asset, `{name, type, in_scope, payout_ceiling_tier,
resolved_report_share, last_updated, testing_constraints}` plus the program-wide
`{reward_table, severity_mix, disclosure_policy, exclusions}`.

The platform policy/scope pages are JS-rendered SPAs. `WebFetch` returns an empty
shell - **use the browser** (`preview_start` → `navigate` → `get_page_text` /
`read_page`). Read both the **policy/overview** tab and the **scope** tab; they
carry different data.

## HackerOne - `hackerone.com/<program>`
- **Scope table** (`/policy_scopes` or the Scope tab): each asset row has
  Asset name, Type, Coverage (in/out), **Max severity**, **Bounty eligibility**,
  **Last update** date, and a **Resolved Reports** count + percent. That percent
  is the crowd proxy - record it verbatim.
- **Core vs Non-core** appears as a `[Core]` / `[Non-core]` tag in the asset
  description. Core = the high reward band (top ceiling). Map Core→top ceiling,
  Non-core→~half.
- **Overview / Rewards summary**: per-severity average bounty + "% submissions",
  and the Low/Medium/High/Critical reward ranges for Core and Non-core.
- **Program stats block**: total bounties paid, reports resolved, response
  efficiency, avg time-to-bounty/resolution.
- **Hacktivity** tab: publicly disclosed reports if any (often empty → note it).
- **Policy body**: program rules, out-of-scope classes, platform-standard
  deviations, required researcher email / `X-HackerOne-Handle` header,
  research-preview/beta downgrades, remediation-project dedup notes.

## Bugcrowd - `bugcrowd.com/<program>` (or `/engagements/...`)
- Scope is grouped by target; reward is driven by the **VRT (Vulnerability
  Rating Taxonomy)** and a **P1–P5** payout table. Capture the max payout per
  target as the ceiling; targets are often flagged as in-scope vs out.
- Per-asset resolved-count is usually **not** exposed - record crowd as unknown
  and lean harder on freshness + CVE history.
- Read the brief's "Focus areas", "Out of scope", and reward-range sections.

## Intigriti - `app.intigriti.com/programs/<org>/<program>`
- Tiered severity bounty table (Exceptional/Critical/High/Medium/Low). Domains
  and endpoints listed with in/out tags and tier caps.
- Public submission stats are limited; treat crowd as coarse.

## YesWeHack / self-hosted VDP / `security.txt`
- Read the program page or `/.well-known/security.txt`. Self-hosted VDPs often
  have **no bounty** (reputation only) and **no crowd data** - the ranking then
  leans on payout=none (deprioritize vs paid), freshness, and setup moat.

## Bug-history search patterns
Run these web searches (adapt product nouns to the target):
- `<product> CVE <year> writeup` and `<product> vulnerability disclosed report`
- `<product> <component> RCE OR auth bypass OR IDOR OR SSRF writeup`
- `<program> hackerone disclosed` (surfaces third-party writeups even when the
  program's own hacktivity is private)
- vendor advisory pages / GitHub Security Advisories for the in-scope repos.

Extract: specific **CVE IDs**, the recurring **bug class**, and whether a fix /
remediation project makes that class a **dedup risk**.

## What to do when data is missing
- No per-asset crowd count → say so, and proxy crowd from asset *accessibility*
  (a browser-only web app attracts more hunters than a jailbreak-gated mobile
  app) plus total program report volume.
- No reward table → rank on freshness + setup moat + bug-class value only, and
  state that payouts are unconfirmed.
Never silently invent numbers - a labeled estimate beats a fake data point.
