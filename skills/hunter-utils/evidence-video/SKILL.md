---
name: evidence-video
description: Turn a user story or a bug reproduction into a short, evidence-backed walkthrough video where every scene is a real capture, hash-chained so nothing can be faked, and the ending discusses insight, impact and risk with a blast-radius map. Use when a reported bug, an auth or access flow, or a feature walkthrough needs a reproducible video a reader can trust, not a screen recording or a hand-drawn diagram.
---

# Evidence video

Make a short video that proves a reproduction, walks a reviewer through an auth or access flow, or tells a user story end to end, and that a reader trusts because every piece of evidence in it is a real capture.

Two layers, kept separate. The **evidence** is real and tamper-evident: real captures, hash-chained in a manifest, re-checkable with `verify`. The **visualization** is yours to compose: design it for this subject with HyperFrames and the guidelines below, do not stamp it from a fixed template.

These rules are the guardrails; inside them, use judgment and craft:

- **No scene without a real capture.** Every step is a screenshot the tool took, hashed into a manifest. Never hand-draw a UI, never fabricate a frame, never claim a step you did not capture.
- **Never fabricate on-screen content.** Every URL, path, status code, number, label, and request or response line shown on the video must come from a real capture or a real source file. If you do not have the real value, leave it out. Do not invent a plausible URL, a round-number timing, a status, an endpoint, or a label to fill a gap. One made-up detail turns the whole thing from evidence into a mockup, and the hash chain cannot catch a fabricated caption, only a swapped frame, so this discipline is yours. When in doubt, show less.
- **Keep the hash chain off the video.** It is the integrity mechanism, not viewer content: the chain lives in the manifest and `verify`, never as an on-screen scene or a hash printed on a frame. The video's job is the story and its meaning.
- **Always end with insight, impact and risk.** It is the point of the video: who is affected, what is at stake, what to verify, and the blast radius. A video that stops at the walkthrough is unfinished.

## Compose for the subject, do not fill a template

The scaffold produces the same handful of boxes for every story; a good evidence video does not look like that. Design the composition for what this one is actually about.

- **Let the subject pick the form.** A race condition wants a timeline; a privilege jump wants two lanes that cross; a data leak wants the record pulled into view; an auth flow wants the wire step foregrounded. Reach for the shape that explains this mechanism, not the shape you used last time.
- **Use the full toolbox.** HyperFrames does real motion, keyframed camera moves, diagrams, data-viz, registry effects and sub-compositions. Load the `/hyperframes` skills and compose with them; the captured frames are your material, not a slideshow to click through.
- **Make it beautiful and legible.** One accent, deliberate pacing, a designed open and close, captions only where the image needs them. The craft is what makes a reviewer watch to the end.

## Dependencies

- HyperFrames for rendering: `npx hyperframes` (Node 22+). `check` validates, `render` writes the MP4.
- A capture source. Any one of:
  - Burp proxy history over the `reburp` REST API (`http://127.0.0.1:9090`) for the real HTTP request and response behind a step. See the `burp-interaction` usage if present.
  - A browser you can drive and screenshot (Claude in Chrome, or the built-in browser pane) for the UI frames and live network list.
  - Terminal screenshots for a CLI or a Foundry or `forge test` reproduction, where each step is a command and its real output.
  - Github code paths

## Setup and pitfalls

Hard-won, in the order they bite:

- Explicitly use HyperFrames and use their studio
- Use Claude in Chrome or the built-in browser pane for the UI frames, because you can navigate and screenshot them.
- Mark what to look at on the image -  A capture holds many details; say which one matters by boxing and labelling it on the pixels, not beside them. Use `focus` for the one region that also earns a zoom punch-in, or an `--annotate` overlay for several callouts on a dense screen, especially a Burp request or response. Then do not restate a marked detail as separate text: the side panel carries the checkable artifacts the image does not show (frame hash, captured time, the requests that fired), never a second copy of what a mark already points at. When a step is marked, the generator drops its side-panel prose for exactly this reason. Marked on the image beats isolated in text, and doing both is noise.
- Capture each thing from the tool that owns it - HTTP from Burp (Repeater or Proxy), never a raw request or response pasted into a browser tab; app behaviour from the browser; code from the editor or a rendered snippet, not a photo of a terminal; a command from the terminal; on-chain state from the explorer or a Foundry trace. The owning tool carries the detail a makeshift capture loses (headers, timing, a diff), and showing it the wrong way reads as amateur. If the right tool is open, use it.
- Correlate surfaces across scenes - To show Burp, the browser, and a code snippet together, chain one capture per scene in order (wire scene, then the browser step, then the code). Each stays a real, hashable capture.
- link to the live source whether its proof in code, in burp, in browser in a specific moment from the user story etc


## Other guidelines
- **Redact before you capture HTTP.** When a step's payload carries a credential, cookie, token or PII, redact it before it enters any file. Record the original request's hash, not its secrets. The build shows `[redacted]` and the hash, which is what a reader checks.
-- **Replay and critique before you ship.** prove the composition is valid, not that it reads well. Play the rendered video back, or snapshot every scene across its span (`npx hyperframes snapshot --frames 4`), and review it as a viewer would. Confirm: no focus box or highlight is mistimed, lands on the wrong element, or covers the text it should point at; every zoom punch settles on its target and leaves captions legible; nothing overlaps or runs off-frame; each scene holds long enough to read and not so long it drags; the markings appear in step with what they explain. Fix what feels off and re-render. Ship only once the replay feels right, not merely once it validates.
