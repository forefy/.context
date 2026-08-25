---
name: training-guide
description: >-
  Build an interactive, click-through VISUAL training course as a self-contained HTML page
  (published as an artifact and saved locally) that teaches a subject gradually - one idea per
  screen, each with a hand-built diagram, a plain-language "reveal the intuition" analogy, and
  occasional trick-question quizzes. The subject is inferred from the current conversation: a
  report you just wrote, a codebase or system you explored, a paper, a protocol, a concept the
  user is learning. Use this skill whenever the user wants to TEACH or EXPLAIN something visually
  and step by step - phrases like "turn this into a visual guide / training / primer / walkthrough
  / explainer / course", "teach me X visually", "explain this gradually with diagrams", "make an
  onboarding for this", "help me understand this piece by piece", or "build a lesson from what we
  just did". Prefer it over a static write-up or a single diagram any time the goal is guided
  understanding that builds up term by term. Not for slide decks (use pptx), spreadsheets, or a
  one-off single diagram with no progression.
---

# Training Guide - interactive visual primer

Turn a subject into a self-paced, click-through course: a full-bleed two-column page where a
hand-built diagram sits on the left and one idea's explanation sits on the right, advanced with
Next / Back / arrow keys. It teaches the way a good tutor does - build the machine one piece at a
time, name each term the first time it appears, drop in a trick question to check understanding,
and reveal an analogy on demand.

The engine (design system, stepper, diagram helpers, quiz mechanics) already exists in
`assets/template.html`. **Your whole job is content**: infer the subject, design the teaching
order, and write the `steps` array plus one small diagram function per screen. Do not rebuild the
engine.

## Workflow

1. **Pin the subject and the audience.** Pull it from the conversation - the report, code, or
   topic in play. If genuinely ambiguous, ask one sentence's worth of clarification (subject +
   who's learning + how deep). Otherwise infer and proceed; the user can redirect.

2. **Design the concept ladder before writing any code.** This is the craft. List the ideas in
   dependency order and check the golden rule: **every term a later screen uses must be taught on
   an earlier screen.** If a "gotcha" or finding screen will say `DeploymentVerifier` or `ECDH`,
   there must be an earlier plain screen that introduces it. A good arc is usually:
   *mechanics* (the core moving parts) → *the build* (what it's for / the features) →
   *the machinery* (supporting infrastructure the gotchas will reference) → *where it gets tricky*
   (pitfalls, findings, edge cases). Put a quiz after each act.

3. **Copy the template and fill it in.** Copy `assets/template.html` to a working file (the user's
   Desktop or the scratchpad). Then:
   - Set `CONFIG` (brand, title, legend meanings).
   - Optionally reskin the palette: change the ONE accent colour (`--accent`/`--accent-ink`/
     `--accent-soft`) and the neutrals in the CSS `:root` blocks to suit the subject's world. Keep
     `--warn` and `--danger` semantic-only. Design both light and dark.
   - Replace the example diagram functions with one per concept, built from the `box / wire / lbl /
     seal / svg` helpers (640×300 viewBox). Reuse `dQuiz()` for quiz screens.
   - Replace the `steps` array with your ladder.
   Read `references/authoring.md` for the full helper API, the screen-object schema, layout math,
   and worked examples - read it before writing diagrams so they don't overlap.

4. **Verify before publishing - never ship a lesson you haven't watched run.** Serve the file
   locally (`python3 -m http.server` in its directory) and open it in the browser tool. Check the
   console has no errors, then click through: the first screen, a couple of diagram screens
   (confirm no overlapping labels), a quiz (answer it - correct flags teal, wrong flags red), and
   the last screen. Fix anything, re-verify. Then stop the server.

5. **Publish and hand off.** Publish with the Artifact tool for a shareable URL, and also leave the
   standalone `.html` on the user's Desktop so they have an offline, dependency-free copy. Give
   them the link and a short map of the acts.

## What makes these good (the bar)

- **One idea per screen.** If a screen needs two diagrams to explain, it's two screens.
- **Terms are earned, never dropped cold.** The single most common failure is a later screen using
  vocabulary the course never introduced. Walk the ladder and fix every unexplained term.
- **The reveal is for intuition, not more facts.** The body states the mechanic; the `aha` reveal
  gives the everyday analogy or the "so what". Keep them distinct.
- **Quizzes are traps that teach.** The tempting answer should be the intuitive-but-wrong one; the
  explanation is where the real lesson lands. 2–4 options, exactly one correct.
- **Diagrams show one relationship.** Boxes are things, wires are flow, teal = the good/verified
  path, danger = where it breaks, warn = caution. Don't rainbow it.
- **Length matches the subject.** A tight concept is ~8 screens; a full system with findings is
  ~15–22. Self-paced, so thoroughness is fine - but every screen must earn its place.

## Design system (fixed, so every course feels like one product)

Two-column full-bleed card; diagram left, reading right, controls pinned bottom. Mono for labels
and eyebrows (the "technical ledger" voice), sans for reading. One accent colour carries
highlight/verified; `warn` and `danger` are semantic only. Theme-aware (light/dark) and responsive
(stacks below 900px). All of this is already wired in the template - keep it; reskin only the
accent + neutrals when the subject calls for a different mood.


## What if content has mistakes

If you are certain the content you're tutoring about has some mistake, consult with the user before stamping it into the guide, data correctness is important.
