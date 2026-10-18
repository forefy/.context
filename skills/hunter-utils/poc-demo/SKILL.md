---
name: poc-demo
description: Produces a short screen-recorded demo that proves an exploit against a real, running target or project. Real tool captures and real output, framed by a clear threat-model attack flow and assembled with HyperFrames into a moving walkthrough, never a slideshow of stills or reconstructed scenes.
compatibility: Needs the live target or project reachable, whatever tool actually proves the finding (such as Foundry, an intercepting proxy, a browser console or network recorder, or a terminal), and HyperFrames (https://github.com/heygen-com/hyperframes, Node >= 22, run with npx hyperframes) for assembly
---

You produce a demo a reviewer would trust: every frame is a real tool showing real output from the live target, framed so it is obvious who the attacker is, what they can do, how far they reach, and exactly what they walk away with. No staged terminals, no mocked responses, no dramatized scenes, and no slideshow of static screenshots.

## The one rule

Real over fake, always. Shots come from the actual tool run against the live target, and the numbers, records, status codes or balances are the ones it produced. When you cannot get a real capture, change the shot, not the truth.

## Show more than you say

A viewer reads little and understands a picture fast, so let the visuals carry the meaning. The attack-flow diagram, the mark on each frame, the zoom and the real motion should make the point on their own, with words added only where the picture cannot. Lean on icons, colour, arrows and the live action, and keep on-screen text short and sparse, so a viewer follows the attack from the visuals alone.

## Workflow

1. Verify the exploit end to end against the live target before filming. Run it yourself and watch the real output. If the intended bug does not fire, such as a patched sink or a degraded environment, pivot to one that does rather than fake it.
2. Pick the tools that prove this finding: a Foundry test for a smart contract, an intercepting proxy for an HTTP bug, the browser console or network tab for client-side behaviour, a terminal for a scripted exploit, and so on. Most real chains span more than one surface, such as a browser and the proxy behind it.
3. Map the threat model as an attack flow. Build a clear diagram, an SVG is ideal, of the players: the attacker and the privilege they start with, the victim or system, and the trust boundary they cross. Name the asset they target and the impact they gain. Keep it visual, with icons, arrows and minimal labels, so a viewer sees at a glance who can do what and how far it goes. Open the video with this map and return to it at the end against what was actually proven.
4. Capture the interaction, not just the end result. Record short clips of the real actions so the cursor move, the click, the typing and the drag are visible on screen. Capture every surface an action touches, so you have both the browser doing it and the proxy or console that saw it.
5. Prefer driving the tool for reproducible capture, for example calling a proxy over its API to send a request and screenshot its UI. When you cannot drive it that way, either give the user concise click-by-click steps, or use computer-use screen automation to perform and record the clicks and drags yourself.
6. Show the whole chain, not one step: the probe, the control holding (the attack blocked, or a tampered request rejected), the bypass (the same step now succeeding), and the data or funds it unlocks. The negative control is what makes the success credible.
7. End on the proof of what was gained. The final frames show the concrete asset the attacker now holds: the admin session, the drained balance, the exfiltrated records, matched back to the impact named in the attack flow. Show the actual asset on screen so the impact is seen, not asserted. Redact secrets in the frame while the data stays real.
8. Mark every real frame. Any shot of a live surface, a browser view, a proxy request or response, a terminal, a test run, carries a visible marker on the exact line or section that matters: a box, an underline or an arrow. Anchor the mark to the thing it points at, on the same layer you zoom, so it tracks the zoom instead of drifting off the target. A real surface on screen with nothing marked leaves the viewer hunting for the point, so there are no bare screenshots.
9. Make every beat move. Assemble with HyperFrames (https://github.com/heygen-com/hyperframes, run with npx hyperframes: init, check, preview, render) and keep motion in each shot: play the real click or drag, follow the cursor to where it acts, punch in onto the marked proof, and pan across a request and its response. Keep zooms proportionate, in far enough to read the proof and no further, so the shot never loses context. Make the zoom one continuous eased move on a single wrapper, long enough to read smoothly; overlapping tweens on the same transform, or a move too fast for its distance, cause the stutter. A row of static screenshots with captions reads as a slideshow, so keep each beat alive. Open the Studio preview (npx hyperframes preview) to watch it back and tune the motion, timing and zoom in HyperFrames Studio, and render only once it moves right.
10. Correlate across surfaces. When a step spans more than one tool, show them in the same beat, side by side or cut between them, so the browser action and the proxy or console that captured it read as cause and effect rather than two unrelated images.
11. Caption sparingly. Add a short line only where the mark, the motion and the diagram cannot make the point on their own, and let the picture do the rest. When you do write one, keep it plain and brief, start it with a capital, use no em-dashes, no negative parallelism such as "not X but Y" or "no X, no Y", and no formula scaffolds. State what happened, do not sell it.

## Self-questioning

- Is every frame a real capture from the live target, or did something get staged?
- Does every real surface shown carry a marker on the key line or section, with nothing left bare?
- Could a viewer follow the whole attack from the visuals alone, with the captions hidden?
- Does the video open with a clear map of the players, what each can do, the asset at stake, and the impact, and close by proving it?
- At the end, can the viewer see the exact asset the attacker gained, matched to the claimed impact?
- Did I run the full chain and watch it produce the output shown?
- Does each beat move with a real click, drag, cursor track, zoom or pan, or did it become a slideshow of stills?
- Are the zooms proportionate and smooth, readable without losing context or stutter, with the mark tracking the zoom?
- When an action spans two surfaces, does the video show both in the same beat and connect them?
- Is the negative control in the video, so success is proven and not just claimed?
- Can a viewer actually read each step, or is it too fast?
- Are real secrets redacted in the frame while the data stays convincingly real?
- Do the captions read like a person wrote them, with no AI tells?
