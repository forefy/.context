# Scoring & ranking rubric

Turn the gathered signals into one **opportunity score (0–100)** and a **verdict
bucket** per asset, then sort best→worst. The score is a synthesis - label it as
such - but it is driven by the hard signals below.

## The four axes

### 1. Payout ceiling (the dominant sort key)
The max reward reachable on the asset. Normalize across the program's own tiers:
- Top tier (HackerOne Core / Bugcrowd P1 full payout / "critical eligible"): **high**.
- Half tier (Non-core / reduced): **medium**.
- Reputation-only / no bounty: **low**.
Ceiling does most of the ranking - but never on its own (see the inversion).

### 2. Crowd (inverse - less is better)
Best signal: resolved-report **share** for the asset. Rough bands:
- ≥15% of program reports → **swept** (heavy penalty)
- 5–15% → **busy**
- 1–5% → **open**
- <1% with a live payout → **wide open** (bonus)
When per-asset counts are missing, proxy from accessibility: browser-only > CLI >
desktop app > mobile app > jailbreak/root-gated, in descending crowd.

### 3. Setup / replication difficulty (a MOAT, not a cost)
How hard it is to stand up a faithful test/repro environment. This is the axis
the skill exists to weaponize: a hard rig **thins the field**, so it *raises*
opportunity when the ceiling is high. Tier it with a time estimate:
- **Trivial · <15 min** - open a browser, `npm i`, clone a public repo.
- **Moderate · 2–4 hrs** - reverse a browser extension, stand up an SDK against a
  staging host, recon tooling, read a codebase deeply.
- **Hard · 1–2 days** - mobile RE (rooted Android + Frida/objection; jailbroken
  or repackaged iOS), desktop/Electron internals (`app.asar` unpack, IPC audit),
  local MCP/connector/extension harnesses, custom protocol emulation.
Map asset types to tiers by what a faithful repro actually requires, not by the
product's surface familiarity.

### 4. Freshness
Last scope-update / addition date. Newer = fewer eyes. Anything rescoped within
the last few months is a freshness **bonus**; year-plus-stale is neutral-to-mild
penalty (more prior trampling).

## Penalties (apply after the axes)
- **Dedup graveyard** - asset's dominant bug class is under a remediation project
  or is the program's most-reported class → heavy penalty even at high ceiling.
- **Informative-only surface** - scope note says common findings are
  working-as-intended / Informative → near-zero.
- **Testing constraints** so tight the asset is barely actionable (e.g.
  authenticate-then-deauth-only) → mild penalty.
- **No/low payout** on a self-hosted VDP → deprioritize vs paid peers.

## Composing the score
There is no magic formula - reason it through, but keep this shape:
`score ≈ ceiling_weight·ceiling + freshness − crowd + moat_bonus(if ceiling high)
− penalties`. Anchor with these reference points so runs stay consistent:
- **90+** Prime: high ceiling, open/wide-open, fresh, real setup moat.
- **70–89** Good: high ceiling but easier setup (so more reachable), or a strong
  moat capped by a lower ceiling.
- **45–69** Recon: skill-gated (recon/code-review) lanes, mid ceiling, mid crowd.
- **20–44** Skip: high ceiling but swept/dedup - the classic inversion.
- **<20** Dead: informative-only, static, or zero-report abandoned surface.

## Verdict buckets → colors (keep consistent with the Sankey)
`Prime #639922 (green) · Good #378ADD (blue) · Recon #BA7517 (amber) ·
Skip #E24B4A (red) · Dead #9A9A90 (gray)`.

## The inversion to always surface
Sort by score and you will usually find the **two highest-ceiling assets near the
bottom** because they are trivial to start and already swept. Name this explicitly
- "ceiling ≠ opportunity" - because it is the non-obvious insight the whole
exercise produces. Likewise call out any asset that is prime-difficulty but
sub-top ceiling as a **technique-development** target: prove the bug class there
cheaply, then pivot the same technique to a top-ceiling asset where it
recategorizes upward.
