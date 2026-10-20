---
name: evidence-video
description: Turn a user story or a bug reproduction into a short, evidence-backed walkthrough video where every scene is a real capture, hash-chained so nothing can be faked, and the ending discusses insight, impact and risk with a blast-radius map. Use when a reported bug, an auth or access flow, or a feature walkthrough needs a reproducible video a reader can trust, not a screen recording or a hand-drawn diagram.
---

# Evidence video

Build a narrated-by-structure video from real captures only. The generator refuses to emit a scene without a real frame behind it, each step hashes the one before it, and the closer explains what the flow means. This is for proving a reproduction, walking a reviewer through an auth or access flow, or showing a user story end to end.

Two hard rules the tool enforces, and you must not work around:

- **No scene without a real capture.** Every step is a screenshot the tool took, hashed into a manifest. Never hand-draw a UI, never fabricate a frame, never claim a step you did not capture.
- **Never fabricate on-screen content.** Every URL, path, status code, number, label, and request or response line shown on the video must come from a real capture or a real source file. If you do not have the real value, leave it out. Do not invent a plausible URL, a round-number timing, a status, an endpoint, or a label to fill a gap. One made-up detail turns the whole thing from evidence into a mockup, and the hash chain cannot catch a fabricated caption, only a swapped frame, so this discipline is yours. When in doubt, show less.
- **Keep the hash chain off the video.** It is the integrity mechanism, not viewer content: the chain lives in the manifest and `verify`, never as an on-screen scene or a hash printed on a frame. The video's job is the story and its meaning.
- **Always end with insight, impact and risk.** It is the point of the video: who is affected, what is at stake, what to verify, and the blast radius. A video that stops at the walkthrough is unfinished.

## Dependencies

- `python3` (standard library only) for `assets/evidence.py`.
- HyperFrames for rendering: `npx hyperframes` (Node 22+). `check` validates, `render` writes the MP4.
- A capture source. Any one of:
  - Burp proxy history over the `reburp` REST API (`http://127.0.0.1:9090`) for the real HTTP request and response behind a step. See the `burp-interaction` usage if present.
  - A browser you can drive and screenshot (Claude in Chrome, or the built-in browser pane) for the UI frames and live network list.
  - Terminal screenshots for a CLI or a Foundry or `forge test` reproduction, where each step is a command and its real output.

## Setup and pitfalls

Hard-won, in the order they bite:

- **Node 22+ or nothing.** HyperFrames hard-errors on older Node. Run `node -v`, and `nvm use 22` (or equivalent) before any `hyperframes` command, including inside scripts.
- **Drive a browser you control; read Burp.** Use Claude in Chrome or the built-in browser pane for the UI frames, because you can navigate and screenshot them. Burp's own browser is read-only to automation and its DevTools port is locked, so use Burp only to read HTTP history, not to click through the flow.
- **Do not copy a browser profile to reuse a login.** Session cookies are encrypted to the origin browser and will not decrypt in a copy; it opens logged out. Sign in in the browser you can drive instead.
- **Start network tracking before you navigate.** The request reader only captures from its first call onward. Call it once to clear, then navigate, then read, or the page's own load requests are missed and you get an empty list.
- **Redact at capture time, never later.** No secret enters a frame or an `--http` file. Record the original request's hash and show `[redacted]`. A browser or proxy capture can hold cookies and tokens in view, so crop or blank them before the frame is saved.
- **The generator emits one sub-composition per scene on purpose.** `lint` rejects a top-level timed section that nests elements (`nested_structure_needs_subcomposition`), so each scene is its own file. If you hand-edit scenes, keep that shape.
- **`check` must be zero findings before you render.** Common fixes: mark deliberate overflow (a glow, a zoom crop) with `data-layout-allow-overflow`; give any looping tween a finite `repeat` count, never `repeat: -1`, under a finite duration; keep small colored text at AA contrast; never pair a CSS `transform` with a GSAP tween on the same property.
- **Render is `-o <path>`, not `--out`.** And the composition `index.html` must be served over HTTP (`npx hyperframes preview`); opening it as `file://` blocks the sub-scene fetches and shows nothing. The deliverable is the rendered `.mp4`, which opens anywhere on disk; the HTML is source, never the thing you hand over.
- **Mark what to look at on the image, once.** A capture holds many details; say which one matters by boxing and labelling it on the pixels, not beside them. Use `focus` for the one region that also earns a zoom punch-in, or an `--annotate` overlay for several callouts on a dense screen, especially a Burp request or response. Then do not restate a marked detail as separate text: the side panel carries the checkable artifacts the image does not show (frame hash, captured time, the requests that fired), never a second copy of what a mark already points at. When a step is marked, the generator drops its side-panel prose for exactly this reason. Marked on the image beats isolated in text, and doing both is noise.
- **Capture each thing from the tool that owns it.** HTTP from Burp (Repeater or Proxy), never a raw request or response pasted into a browser tab; app behaviour from the browser; code from the editor or a rendered snippet, not a photo of a terminal; a command from the terminal; on-chain state from the explorer or a Foundry trace. The owning tool carries the detail a makeshift capture loses (headers, timing, a diff), and showing it the wrong way reads as amateur. If the right tool is open, use it.
- **Correlate surfaces across scenes.** To show Burp, the browser, and a code snippet together, chain one capture per scene in order (wire scene, then the browser step, then the code). Each stays a real, hashable capture.
- **Demonstrating code: link to the live source.** When a step shows code and that file exists in a local checkout, carry a `vscode://file/<absolute-path>:<line>` reference in the step (put it in the caption or `action`, and record it in the manifest) so a reviewer can open the exact line in VSCode, not just read the still. Render the snippet for the video and keep the deep link beside it. Only emit the link when the file resolves locally; a `vscode://` that opens nothing is worse than none.

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
   `--focus` is an optional region in frame pixels (`{x, y, w, h, label}`) that gets a punch-in and a labelled box drawn on the image. For several callouts on one dense capture, pass `--annotate <file>` to `build`: a JSON map of step number to a list of `{x, y, w, h, label}` boxes, each drawn and labelled on that step's frame. Marks are a presentation overlay, not part of the hashed chain, so you can reposition them without re-capturing; the frame stays the evidence. `--network` is an optional JSON array of `{method, path, status}` rows observed on that step. Run `verify` any time to confirm the chain:
   ```
   python3 assets/evidence.py verify --manifest evidence/manifest.json
   ```

4. **Redact before you capture HTTP.** When a step's payload carries a credential, cookie, token or PII, redact it before it enters any file. Record the original request's hash, not its secrets. The build shows `[redacted]` and the hash, which is what a reader checks.

5. **Write the wire scene (optional) and the closer (required).**
   - `--http <json>`: one real request and response to feature as its own scene (`after_step`, `eyebrow`, `title`, `lines`, `highlight`, `meta`). Pull it from Burp history and redact it.
   - `--insight <json>`: the required closer. `severity` (critical|high|medium|low|info), `headline`, `insight`, `impact`, `risk`, and `verify` (a list). Add `impact_map` to draw the blast radius: `center`, `hub`, and `nodes` (each `{kind, label, sub}`, kinds routine|connector|session|project|data). Every claim must be grounded in what the captures show; never invent a risk.
   - **State the impact, then prove it.** There is the impact you argue and the impact you actually demonstrated. Whenever you obtained real proof of the gain, attach it on the same impact page: the exfiltrated record, the executed action's response, the balance that changed, the data a lower-privileged session should not have read. Capture it as a real frame like any step, redact secrets in-frame, and point the `impact` line at it. Argued impact tells the reader what is at stake; attached proof removes the argument. A severity with proof outranks the same severity without it.
   - **Add `divergence` to show the user story against the attacker story.** This drives the fork scene (the beat between the steps and the closer). `intended` (`label`, `sub`, `steps`) is the normal use of the feature; `attacker` (`label`, `sub`, `steps`, `divert_at`) is where it gets diverted. Line the two up step for step so the fork reads at a glance, and set `divert_at` to the index of the step where normal use becomes abuse. Ground both paths in the real flow you captured, not a generic attack. Without a `divergence` block this beat is simply omitted; it never falls back to showing hashes.

6. **Build, check, render.**
   ```
   python3 assets/evidence.py build --manifest evidence/manifest.json --project <hf-project> \
     --http http.json --insight insight.json
   cd <hf-project> && npx hyperframes check && npx hyperframes render -o story.mp4
   ```
   The build writes one HyperFrames sub-composition per scene. `check` must pass with zero findings before you render. Snapshot a scene midpoint with `npx hyperframes snapshot --at <s>` and eyeball it before rendering the whole thing.

7. **Replay and critique before you ship.** `check` proves the composition is valid, not that it reads well. Play the rendered video back, or snapshot every scene across its span (`npx hyperframes snapshot --frames 4`), and review it as a viewer would. Confirm: no focus box or highlight is mistimed, lands on the wrong element, or covers the text it should point at; every zoom punch settles on its target and leaves captions legible; nothing overlaps or runs off-frame; each scene holds long enough to read and not so long it drags; the markings appear in step with what they explain. Fix what feels off and re-render. Ship only once the replay feels right, not merely once it validates.

## Scene order

title -> one scene per captured step (with an optional wire scene after a chosen step) -> user story vs attacker story (only when a `divergence` block is given, else omitted) -> insight/impact/risk -> blast-radius map. The manifest still hashes and verifies every frame, but no hash is shown on the video. Insight and the map are the payoff.

## Manifest and data shapes

See `references/manifest-format.md` for the manifest entry, the `--http`, `--insight`, `impact_map` and `divergence` JSON, and how the hash chain is computed and verified (in the manifest, never on the video).
