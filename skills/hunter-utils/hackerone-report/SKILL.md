---
name: hackerone-report
description: Draft and file a HackerOne report in the browser, with a proof-of-concept package and demo-video notes. Use to submit or prepare a bug-bounty report.
---

# Filing a HackerOne report

Drive a HackerOne vulnerability submission end to end: verify it's worth filing, write it up concisely, build a reproducible PoC with a video-ready README, fill the submission form in the browser, and hand the irreversible steps back to the user.

## Non-negotiable safety rules

These are hard stops. They protect the user's account and their Signal.

1. **Never enter credentials or 2FA codes.** When the form gates on login, take a screenshot, tell the user to sign in themselves, and wait. Suggest they tick "Remember me for 2 weeks" (HackerOne sessions drop mid-flow otherwise).
2. **Never click the final "Submit Report".** It is an irreversible publish and it spends one of the user's reports. Fill everything, then hand off: the user reviews and submits. State this explicitly up front.
3. **Never attach files the user didn't ask you to**, and don't fabricate PoC output. The in-app browser can't drive the native file picker anyway — the user attaches the zip and the video.
4. **Filing is per-user consent.** Draft freely; the act of submitting is the user's.

## Phase 0 — Dedup pre-flight (do this FIRST, every time)

The most expensive mistake is re-filing a finding the program already closed. It wastes a report and dents Signal. Before drafting anything:

- **Search the local findings tree** for prior work on the same root cause / sinks / code paths. Look especially in any `duplicates/` folder and for filenames encoding a resolution: `Informative-*`, `Duplicate-*`, `NA-*`, `Resolved-*`. A file named `Informative-1-<x>.md` means the program already closed `<x>` as Informative.
- **Compare code locations, not just titles.** Grep both the candidate writeup and prior reports for the exact files/functions/sinks cited. If they overlap, it's the same finding regardless of new framing. (A "new vector" that strengthens the *entry* but reaches the *same sink the program already judged* is still a duplicate.)
- **Offer to check the live program state:** open HackerOne → *My Reports*, search a keyword from the finding, read the actual close reason/comment.
- If it's a dup: **say so plainly and recommend not filing.** Options: don't file; comment/appeal on the *existing* report instead of opening a new one; hold reports for something novel. Only proceed on the user's explicit go-ahead.
- Also surface program constraints visible on the submit page: **"Trial Reports Remaining: N"** and any **Signal Requirement** — a low Signal can block future submissions, so accuracy matters more than volume.

## Phase 1 — Write the report (concise)

Use `references/report-template.md`. House style:

- **Plain, direct, first person** ("we found this field is forgeable"), not marketing prose.
- **State each fact once.** The same "new vector / defeated mitigation" point tends to sprawl across Summary, Component, Steps, and Impact — keep it in Summary + the Steps variant, and don't re-litigate it in Impact.
- **No em dashes** if the user prefers plain hyphens; use spaced hyphens ` - ` and split run-ons into sentences.
- Sections: Summary → Version/Affected → Component (vulnerable code paths) → Steps To Reproduce → Supporting Material → Impact → Suggested Fix.
- **Title** goes in its own field (max ~150 chars): `<vuln type> via <mechanism> (<feature/component>, <version/context>)`. Don't repeat the title as the first line of the Description body.

## Phase 2 — PoC package + video-ready README

Goal: a self-contained folder the triager can run and the user can film. Use `references/poc-readme-template.md`.

- **One command per step, copy-paste, in order:** prerequisites check → environment setup → baseline (the thing that is denied) → exploit → the money-shot success → a control that proves the mechanism → teardown.
- **The money shot** is a before/after: the *same* request denied, then succeeding, with only the exploited variable changed. That's what the video should capture.
- **Actually run the exact README blocks on a clean environment before shipping.** Repro commands that work in your head often fail copy-paste (auth/credential precedence, working-directory resets, tool flags that don't override config). Fix them until a fresh run reproduces.
- Prefer a few transparent commands over a big opaque `.sh`. If shared shell state is the only reason for a script, capture it in a tiny helper function inside the README instead.
- Ship: `README.md` (the walkthrough), the exploit inputs, an annotated pointer to the vulnerable source lines, a non-interactive runner, and any plumbing clearly labeled "not part of the vulnerability". Zip it; reference it in the report as `poc.zip`. The user records `poc.mov` and attaches both.

## Phase 3 — Browser: reach the submission form

Use the in-app Browser (`mcp__Claude_Browser__*`) or Claude-in-Chrome. Gotchas learned:

- Navigate to `hackerone.com/<program>`. The submit entry is **"Submit without Report Assistant"** (full manual form). Its href looks like `/<program>/reports/new?type=team&report_type=vulnerability`.
- **Do NOT deep-link that URL** — it's a client-side SPA route and returns "Page not found" on direct navigation. **Click the link on the program page instead.**
- Expect a **login/2FA gate** → hand off to the user (safety rule 1). After they sign in, the program page may need a reload.
- Sessions expire mid-flow; if the form empties or bounces to sign-in, have the user re-auth with "Remember me".

## Phase 4 — Fill the form

The manual form is a numbered flow. Prefer `read_page` refs over pixel coordinates (the pane rescales screenshots and raw-coordinate clicks miss). Use `form_input` for text fields — it's reliable.

| # | Field | How |
|---|---|---|
| 1 | **Asset** | Type in the asset search box to filter, then click the match. For a source-code asset, search its repo slug (e.g. an `<org>/<repo>` GitHub asset tagged "Eligible for bounty") and pick the exact program-listed entry — don't assume a specific project. If the inline list stays open and eats scroll, clear the search text / press Escape to collapse it. |
| 2 | **Weakness (CWE)** | Type a keyword (e.g. `authorization`) to filter, pick the CWE (e.g. Improper Authorization CWE-285). Then set the **cluster/subcategory** dropdown next to it (e.g. *Access Control*). Selecting the CWE is preserved even if the list then filters empty. |
| 3 | **Severity (CVSS)** | "Submit report with severity" → CVSS 3.0 calculator. Set each metric button by ref. Set the clearly-correct metrics yourself; **leave a genuinely judgment-call metric (usually Scope) for the user**, and show them both resulting scores (e.g. Scope:Unchanged→High vs Scope:Changed→Critical). Read the live "Score" readout back to them. |
| 4 | **Title** | `form_input` the title string (≤150 chars). |
| 4 | **Description** | `form_input` the report body (Summary → … → Suggested Fix), Markdown. Drop the leading `# Title` line — the Title field holds it. |
| 4 | **Impact** | Separate required field. `form_input` the Impact paragraph only. |
| 4 | **Attachments** | User drags in `poc.zip` + `poc.mov` (you can't drive the native picker). Optionally suggest renaming the zip to match what the report references. |

After filling, offer to click **Preview** on the Markdown fields so the user can eyeball rendering. Verify the "Review and Submit" panel shows the right Title/Asset.

## Phase 5 — Hand off

Summarize the filled state as a table (Asset / Weakness / Severity / Title / Description / Impact = done). List what remains and that it's the user's: attach zip, record+attach video, decide any judgment-call CVSS metric, review, **click Submit**. Re-state that you won't click Submit and won't loop on the blocked login.

## References

- `references/report-template.md` — the concise finding writeup skeleton with all section headings.
- `references/poc-readme-template.md` — the video-ready copy-paste reproduction README pattern.
