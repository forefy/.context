---
name: evidence-capture
description: Enforce reproduction bug evidence in either image or video formats to be ready to submit
---

Evidence capture skills assists in the image and/or video evidence that go to prove reproducible bugs.

# Must-have rules

- Reproductions usually are made of steps. each step needs to be thought of what we want to present it could be insight or outcome that is tailored to the sentence in the reproduction example
- Captures are only visuals, added text must be minimal if even at all
- OCR-adding markings of the exact point-in-image that the evidence speaks to, for example, if we are showing BurpSuite raw Request/Response pair - a marker signaling the lines exactly on where to look is crucial (other than staring at a wall of info) - the marking should fit the evidence
- Image type captures must go with a 1 line title describing the step (e.g. Attached image demonstrates browser view of when the user interacts with x)
- Capture each thing from the tool that owns it - HTTP from Burp (Repeater or Proxy), never a raw request or response pasted into a browser tab; app behaviour from the browser; code from the editor or a rendered snippet, not a photo of a terminal; a command from the terminal; on-chain state from the explorer or a Foundry trace. The owning tool carries the detail a makeshift capture loses (headers, timing, a diff), and showing it the wrong way reads as amateur. If the right tool is open, use it.
- Correlate surfaces across scenes - To show Burp, the browser, and a code snippet together, chain one capture per scene in order (wire scene, then the browser step, then the code). Each stays a real, hashable capture.
- link to the live source whether its proof in code, in burp, in browser in a specific moment from the user story etc
- Don't fabricate data only use real data and real captures no workarounds find the best way to get proper evidence
- When done, critique the result with actual OCR or visual analysis and wonder if you missed any guidelines in this skill checklist or you did something off (e.g. if you marked a part in the image too much to the right of where the text actually is)

# Extended rules
- **No scene without a real capture.** Every step is a screenshot the tool took, hashed into a manifest. Never hand-draw a UI, never fabricate a frame, never claim a step you did not capture.
- **Always end with insight, impact and risk.** It is the point of the video: who is affected, what is at stake, what to verify, and the blast radius. A video that stops at the walkthrough is unfinished.
- **Let the subject pick the form.** A race condition wants a timeline; a privilege jump wants two lanes that cross; a data leak wants the record pulled into view; an auth flow wants the wire step foregrounded. Reach for the shape that explains this mechanism, not the shape you used last time.
- **Make it beautiful and legible.** One accent, deliberate pacing, a designed open and close, captions only where the image needs them. The craft is what makes a reviewer watch to the end.
- **Redact before you capture HTTP.** When a step's payload carries a credential, cookie, token or PII, redact it before it enters any file. Record the original request's hash, not its secrets. The build shows `[redacted]` and the hash, which is what a reader checks.

# Dependencies
- For videos Explicitly use HyperFrames and their studio app locally (https://github.com/heygen-com/hyperframes)
- A capture source. Any one of:
  - A browser you can drive and screenshot (Claude in Chrome, or the built-in browser pane) for the UI frames and live network list.
  - Burp proxy history over the `reburp` REST API (`http://127.0.0.1:9090`) for the real HTTP request and response behind a step. See the `burp-interaction` usage if present.
  - Terminal screenshots for a CLI or a programming language common default e.g. `forge test` reproduction, where each step is a command and its real output.
  - Github code paths
