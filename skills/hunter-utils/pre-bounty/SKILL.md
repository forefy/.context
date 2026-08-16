---
name: pre-bounty
description: >-
  Pre-engagement recon and target prioritization for a bug-bounty or VDP scope.
  Given a program URL (HackerOne, Bugcrowd, Intigriti, YesWeHack, self-hosted
  VDP) or a pasted list of in-scope assets/repos/APIs, it maps the scope, pulls
  bug history (disclosed reports + public CVEs/writeups), extracts the
  in/out-of-scope boundary gotchas, summarizes reward economics, then scores and
  RANKS every asset best-to-worst by opportunity — payout ceiling, crowdedness,
  replication-setup difficulty, and scope freshness — and renders a ranked
  asset→setup→ROI Sankey. Use this WHENEVER the user is sizing up a bounty
  program, asks "where should I hunt", "which target is worth my time", "what's
  least crowded", wants pre-bounty recon / scope analysis / target selection, or
  pastes a program link or scope table — even if they don't say the word
  "pre-bounty". Do not use it to write or file a vulnerability report (that is a
  separate reporting skill).
---

# Pre-bounty: scope recon & target prioritization

## The core thesis

Most hunters converge on whatever is cheapest to start testing. That means the
crowd is an artifact of the **setup barrier**, not of where the bugs are. So the
edge is systematic: rank the scope by

> **opportunity ≈ (payout ceiling × freshness) ÷ crowd**, with **setup difficulty
> acting as a moat** — a hard-to-reproduce environment keeps competitors out, so
> it is a *positive* when paired with a high ceiling.

The whole skill exists to compute that ranking from real program data and show it
in a way the user can act on. A high max-payout asset that is trivial to set up
and already swept (lots of resolved reports) is a *worse* target than a modest
one nobody has tooled up for. Make that legible.

## Inputs this skill accepts

Any of, in order of preference:
- A **program URL** — `hackerone.com/<program>`, `bugcrowd.com/<program>`,
  `app.intigriti.com/...`, `yeswehack.com/...`, or a self-hosted `/security` /
  `security.txt` / VDP page.
- A **pasted scope table or asset list** (domains, mobile apps, repos, APIs).
- A rough **description of API/repo access** the user already has.

If you only get a program name, construct the URL. If the platform page is
JavaScript-rendered (HackerOne, Bugcrowd, Intigriti all are), **use the browser
tools to read it** — `WebFetch` returns an empty shell for these. `read_page` /
`get_page_text` on the policy and scope tabs is the reliable path.

## Workflow

Work the five stages in order. Stages 1–3 are parallelizable — fire the fetches
and searches together.

### 1. Gather the scope (the signal-richest step)
Pull and record, per asset:
- **Asset name, type** (domain / mobile / desktop / API / source / other) and
  whether it is **in or out of scope**.
- **Payout tier** — most programs tag assets into tiers (HackerOne
  Core/Non-core; Bugcrowd P1–P5 targets; others "critical eligible" vs not).
  Capture the **max reward** reachable per asset — this is the ceiling.
- **Resolved-report count / share per asset** if the platform shows it. This is
  your single best **crowd proxy** — an asset with 40% of all resolved reports
  is picked-over; one with <2% is open. HackerOne shows this on the scope table;
  Bugcrowd/Intigriti show submission stats less granularly (note when missing).
- **Last-updated date** of each scope entry → **freshness**. Recently added or
  rescoped assets have had fewer eyes.
- **Program-wide reward table** (per-severity bounty ranges + averages) and the
  **severity mix** of resolved reports if shown.

See `references/sourcing.md` for exactly where each platform surfaces these.

### 2. Mine bug history
- Check the program's **hacktivity / disclosed reports**. Many programs disclose
  nothing publicly — say so plainly and fall back to the crowd proxy.
- Web-search **public CVEs and researcher writeups** for the target's products.
  The recurring bug *class* tells you what actually lands (e.g. trust-boundary
  RCE, config-precedence, deep-link/IPC on native clients). Record specific CVE
  IDs where found.
- Note **remediation / dedup signals** — if the policy says a bug class is under
  a wholesale fix, reports there will close as duplicates. Flag those assets as
  saturated regardless of payout.

### 3. Extract the boundary gotchas
The fine print is where hunters waste days. Capture:
- **Adjacent in/out pairs** — cases where a near-identical bug is in-scope on one
  asset and out on another (e.g. first-party MCP in-scope vs OSS MCP out;
  first-party connector in vs third-party-in-directory out).
- **Excluded vulnerability classes** (DoS, clickjacking on non-sensitive pages,
  missing cookie flags, dependency confusion, self-XSS, rate-limiting, etc.).
- **Platform-standard deviations** and payout nerfs — especially
  "one bounty per systemic issue" and discretionary PII-leak severity, which
  kill the "report many instances" strategy.
- **Testing constraints** (e.g. leaked-key "authenticate then immediately
  deauth only", required `X-HackerOne-Handle` header / researcher email).

Render this as a compact **in ✅ / out ❌ table** — see the output spec.

### 4. Score & rank every asset
Apply the rubric in `references/scoring.md`. For each asset produce:
`{ setup tier + time estimate, crowd, payout ceiling, freshness, ROI verdict,
opportunity score 0–100 }`, then sort best→worst. Verdict buckets:
**Prime · Good · Recon · Skip · Dead**. Be honest that the two highest-ceiling
assets are often near the bottom because the crowd is already there — surfacing
that inversion is the point.

### 5. Deliver
Produce the artifacts below. Lead with the ranking; it is what the user asked for
even when they phrased it as "analyze the scope".

## Output spec

**The output is tables + the two widgets. Prose is connective tissue, not the
product.** Put every fact that fits in a cell *in a cell* — never restate in a
paragraph what a table or widget already shows. See "Prose discipline" below for
the hard budget; violating it is the most common failure of this skill.

Deliver, in this order:

1. **Program header — one line.** `bounty since · total paid · paid/90d ·
   resolved · response-efficiency · # in-scope assets`, then a single sentence on
   how hunted the program is. No more.
2. **Boundary gotchas — a table.** The `in ✅ / out ❌` adjacent pairs as a
   two-column table. Follow with **at most 3–4 bullets** for the
   strategy-killing nerfs (systemic-dedup, testing constraints, saturated
   classes) — one line each, no sub-bullets, no paragraphs.
3. **Severity economics — a table.** Columns: `severity · share of resolved ·
   avg bounty · range`, one row per severity. Then **one** italic sentence:
   "where the crits actually land", grounded in the CVE corpus — noting crit
   rates are usually ~1% and the money is repeatable Highs.
4. **Ranked list widget, best→worst** — rank, verdict chip, payout ceiling,
   setup time, crowd %, freshness, and a one-line "why" per asset. Render with
   the ranked-list widget in `references/sankey.md`. The widget carries the
   per-asset detail; do **not** narrate the list row by row afterward.
5. **Ranked Sankey widget** — the three-stage `asset → replication setup → ROI
   verdict` flow, assets ordered best (top) → worst (bottom), thread width =
   report volume, labels carrying payout ceiling + freshness. Fill the one data
   array in the `references/sankey.md` template — do not hand-roll new diagram
   code. Render via the `visualize` `show_widget` tool (call its `read_me` once
   first, as that tool requires).
6. **Verdict — a tight closer under both widgets.** Only what the tables can't
   say: name the **top 1–3 picks** (one clause each on *why now*), state the
   **inversion** in one sentence (which high-ceiling assets sit at the bottom and
   why), and flag any **technique-development** target. Cap this whole section at
   ~120 words.

### Prose discipline (the point of this update)
- **Tables and widgets are load-bearing; prose only connects them.** If a
  sentence repeats a number or verdict already in a cell/chip, cut it.
- **Budget:** header = 1 line; each table gets ≤1 lead-in line and ≤1 follow-up
  line; the closing verdict ≤120 words. No section is a paragraph block.
- **No row-by-row narration** of the ranked list — that is the widget's job.
- **One sources line** at the very end (CVE/writeup links), not inline essays.
- When in doubt, move the sentence into a table cell or delete it.

## Notes on judgment
- **Estimate, but flag estimates.** Setup-time and opportunity scores are
  your synthesis; the payout ceiling, crowd counts, and dates are hard data from
  the program. Keep the two visibly separate so the user can trust the spine.
- **Scale to the ask.** "Quick take on this program" → the ranked list is
  enough. "Full workup" → all four artifacts plus the CVE history.
- **Stay in authorized-recon lane.** This skill reads public program data and
  public vulnerability history to prioritize; it does not test, exploit, or
  probe live targets. Reproduction/testing happens later, under program rules.
- This skill pairs with a reporting skill for the *next* phase (filing a found
  bug). Don't try to do both; hand off.
