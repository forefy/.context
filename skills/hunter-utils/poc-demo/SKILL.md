---
name: poc-demo
description: Produces a short screen-recorded demo that proves an exploit against a real, running target or project. Real tool captures and real output assembled with HyperFrames into a moving, narrated walkthrough, never a slideshow of stills or reconstructed scenes.
compatibility: Needs the live target or project reachable, whatever tool actually proves the finding (such as Foundry, an intercepting proxy, a browser console or network recorder, or a terminal), and HyperFrames (https://github.com/heygen-com/hyperframes, Node >= 22, run with npx hyperframes) for assembly
---

You produce a demo a reviewer would trust: every frame is a real tool showing real output from the live target, and every beat moves the way a person driving the tools would move. No staged terminals, no mocked responses, no dramatized scenes, and no slideshow of static screenshots.

## The one rule

Real over fake, always. Shots come from the actual tool run against the live target, and the numbers, records, status codes or balances are the ones it produced. When you cannot get a real capture, change the shot, not the truth.

## Workflow

1. Verify the exploit end to end against the live target before filming. Run it yourself and watch the real output. If the intended bug does not fire, such as a patched sink or a degraded environment, pivot to one that does rather than fake it.
2. Pick the tools that prove this finding: a Foundry test for a smart contract, an intercepting proxy for an HTTP bug, the browser console or network tab for client-side behaviour, a terminal for a scripted exploit, and so on. Most real chains span more than one surface, such as a browser and the proxy behind it.
3. Capture the interaction, not just the end result. Record short clips of the real actions so the cursor move, the click, the typing and the drag are visible on screen. Capture every surface an action touches, so you have both the browser doing it and the proxy or console that saw it.
4. Prefer driving the tool for reproducible capture, for example calling a proxy over its API to send a request and screenshot its UI. When you cannot drive it that way, either give the user concise click-by-click steps, or use computer-use screen automation to perform and record the clicks and drags yourself.
5. Show the whole chain, not one step: the probe, the control holding (the attack blocked, or a tampered request rejected), the bypass (the same step now succeeding), and the data or funds it unlocks. The negative control is what makes the success credible.
6. Show the payoff. The response size, a real record, the drained balance, the enumerated accounts, so the viewer sees what was taken. Redact secrets in the frame while the data stays real.
7. Make every beat move. Assemble with HyperFrames (https://github.com/heygen-com/hyperframes, run with npx hyperframes: init, check, preview, render) and keep motion in each shot: play the real click or drag, follow the cursor to where it acts, punch in and zoom onto the exact proof text, and pan across a request and its response. A row of static screenshots with captions reads as a slideshow, so keep each beat alive. Open the Studio preview (npx hyperframes preview) to watch it back and tune the motion, timing and captions in HyperFrames Studio, and render only once it moves right.
8. Correlate across surfaces. When a step spans more than one tool, show them in the same beat, side by side or cut between them, so the browser action and the proxy or console that captured it read as cause and effect rather than two unrelated images.
9. Caption in plain language, the way a person writes. Full sentences that start with a capital. No em-dashes. No negative parallelism such as "not X but Y", "no X, no Y", or "it is not about X, it is Y". No problem/solution colon pairs or other formula scaffolds. State what happened, do not sell it.

## Self-questioning

- Is every frame a real capture from the live target, or did something get staged?
- Did I run the full chain and watch it produce the output shown?
- Does each beat move with a real click, drag, cursor track, zoom or pan, or did it become a slideshow of stills?
- When an action spans two surfaces, does the video show both in the same beat and connect them?
- Is the negative control in the video, so success is proven and not just claimed?
- Can a viewer actually read each step, or is it too fast?
- Are real secrets redacted in the frame while the data stays convincingly real?
- Do the captions read like a person wrote them, with no AI tells?
