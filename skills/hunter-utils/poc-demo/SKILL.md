---
name: poc-demo
description: Produces a short screen-recorded demo that proves an exploit against a real, running target or project. Real tool captures and real output assembled with HyperFrames, never reconstructed or dramatized scenes.
compatibility: Needs the live target or project reachable, whatever tool actually proves the finding (such as Foundry, an intercepting proxy, a browser console or network recorder, or a terminal), and HyperFrames (https://github.com/heygen-com/hyperframes, Node >= 22, run with npx hyperframes) for assembly
---

You produce a demo a reviewer would trust: every frame is a real tool showing real output from the live target. No staged terminals, no mocked responses, no dramatized scenes. If a step cannot be captured for real, it does not go in the video.

## The one rule

Real over fake, always. Shots come from the actual tool run against the live target, and the numbers, records, status codes or balances are the ones it produced. When you cannot get a real capture, change the shot, not the truth.

## Workflow

1. Verify the exploit end to end against the live target before filming. Run it yourself and watch the real output. If the intended bug does not fire, such as a patched sink or a degraded environment, pivot to one that does rather than fake it.
2. Pick the tool that actually proves this finding: a Foundry test for a smart contract, an intercepting proxy for an HTTP bug, the browser console or network tab for client-side behaviour, a terminal for a scripted exploit, and so on. One video can mix several.
3. Capture real evidence from that tool for each step. Prefer driving it so the shots are reproducible and need no manual clicking, for example calling a proxy over its API. When you cannot drive it that way, either give the user concise click-by-click steps to capture the shot, or use computer-use screen automation to do it yourself.
4. Show the whole chain, not one step: the probe, the control holding (the attack blocked, or a tampered request rejected), the bypass (the same step now succeeding), and the data or funds it unlocks. The negative control is what makes the success credible.
5. Show the payoff. The response size, a real record, the drained balance, the enumerated accounts, so the viewer sees what was taken. Redact secrets in the frame while the data stays real.
6. Assemble with HyperFrames (https://github.com/heygen-com/hyperframes, run with npx hyperframes: init, check, render). Punch in on the exact proof text, add captions that point at what to look at, and hold every beat long enough to read.
7. Caption in plain language, the way a person writes. Full sentences that start with a capital. No em-dashes. No negative parallelism such as "not X but Y", "no X, no Y", or "it is not about X, it is Y". No problem/solution colon pairs or other formula scaffolds. State what happened, do not sell it.

## Self-questioning

- Is every frame a real capture from the live target, or did something get staged?
- Did I run the full chain and watch it produce the output shown?
- Is the negative control in the video, so success is proven and not just claimed?
- Can a viewer actually read each step, or is it too fast?
- Are real secrets redacted in the frame while the data stays convincingly real?
- Do the captions read like a person wrote them, with no AI tells?
