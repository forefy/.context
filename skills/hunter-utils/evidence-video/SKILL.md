---
name: evidence-video
description: Turn a user story or a bug reproduction into a short, evidence-backed walkthrough video where every scene is a real capture, hash-chained so nothing can be faked, and the ending discusses insight, impact and risk with a blast-radius map. Use when a reported bug, an auth or access flow, or a feature walkthrough needs a reproducible video a reader can trust, not a screen recording or a hand-drawn diagram.
---

# Evidence video

Build a narrated-by-structure video from real captures only. The generator refuses to emit a scene without a real frame behind it, each step hashes the one before it, and the closer explains what the flow means. This is for proving a reproduction, walking a reviewer through an auth or access flow, or showing a user story end to end.

Two hard rules the tool enforces, and you must not work around:

- **No scene without a real capture.** Every step is a screenshot the tool took, hashed into a manifest. Never hand-draw a UI, never fabricate a frame, never claim a step you did not capture.
- **Always end with insight, impact and risk.** The hash chain proves the frames are real; it is not the point. The last beats say who is affected, what is at stake, and what to verify, and visualize the blast radius. A video that stops at "the frames are real" is unfinished.

## Dependencies

- `python3` (standard library only) for `assets/evidence.py`.
- HyperFrames for rendering: `npx hyperframes` (Node 22+). `check` validates, `render` writes the MP4.
- A capture source. Any one of:
  - Burp proxy history over the `reburp` REST API (`http://127.0.0.1:9090`) for the real HTTP request and response behind a step. See the `burp-interaction` usage if present.
  - A browser you can drive and screenshot (Claude in Chrome, or the built-in browser pane) for the UI frames and live network list.
  - Terminal screenshots for a CLI or a Foundry or `forge test` reproduction, where each step is a command and its real output.

## Workflow

1. **Write the steps first, then prove them.** Decide the ordered steps of the story up front. The tool executes nothing; you capture each step for real, and the tool only chains and renders what you captured. If a step has no capture, the build aborts on that step.

2. **Init the manifest.**
   ```
   python3 assets/evidence.py init --manifest evidence/manifest.json \
     --story "As a <role>, I <do X> so that <Y>." \
     --subject "<host or target>" --tool "<how frames were captured>"
   ```

3. **Capture each step and add it.** Take the screenshot with your capture source, then:
   ```
   python3 assets/evidence.py add --manifest evidence/manifest.json \
     --title "Login page" --action "Open the app, redirected to /login" \
     --url "https://target/login" --frame evidence/frames/01.png \
     --focus '{"x":545,"y":262,"w":260,"h":82}' --network net-01.json
   ```
   `--focus` is an optional region in frame pixels that gets a punch-in and a highlight box. `--network` is an optional JSON array of `{method, path, status}` rows observed on that step. Run `verify` any time to confirm the chain:
   ```
   python3 assets/evidence.py verify --manifest evidence/manifest.json
   ```

4. **Redact before you capture HTTP.** When a step's payload carries a credential, cookie, token or PII, redact it before it enters any file. Record the original request's hash, not its secrets. The build shows `[redacted]` and the hash, which is what a reader checks.

5. **Write the wire scene (optional) and the closer (required).**
   - `--http <json>`: one real request and response to feature as its own scene (`after_step`, `eyebrow`, `title`, `lines`, `highlight`, `meta`). Pull it from Burp history and redact it.
   - `--insight <json>`: the required closer. `severity` (critical|high|medium|low|info), `headline`, `insight`, `impact`, `risk`, and `verify` (a list). Add `impact_map` to draw the blast radius: `center`, `hub`, and `nodes` (each `{kind, label, sub}`, kinds routine|connector|session|project|data). Every claim must be grounded in what the captures show; never invent a risk.

6. **Build, check, render.**
   ```
   python3 assets/evidence.py build --manifest evidence/manifest.json --project <hf-project> \
     --http http.json --insight insight.json
   cd <hf-project> && npx hyperframes check && npx hyperframes render -o story.mp4
   ```
   The build writes one HyperFrames sub-composition per scene. `check` must pass with zero findings before you render. Snapshot a scene midpoint with `npx hyperframes snapshot --at <s>` and eyeball it before rendering the whole thing.

## Scene order

title -> one scene per captured step (with an optional wire scene after a chosen step) -> hash chain -> insight/impact/risk -> blast-radius map. The chain is the trust mechanism; insight and the map are the payoff.

## Manifest and data shapes

See `references/manifest-format.md` for the manifest entry, the `--http`, `--insight` and `impact_map` JSON, and how the hash chain is computed and verified.
