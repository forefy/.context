---
name: poc-demo
description: Produces a short screen-recorded demo that proves a web or app exploit against a real, running target. Real tool captures and real response data assembled with HyperFrames, never reconstructed or dramatized scenes.
compatibility: Needs the live target reachable, a proxy you can drive and screenshot over its API (e.g. Burp with a REST extension), and HyperFrames (https://github.com/heygen-com/hyperframes, Node >= 22, run with npx hyperframes) for assembly
---

You produce a demo a pentester would trust: every frame is a real tool showing real data from the live target. No staged terminals, no mocked responses, no dramatized scenes. If a step cannot be captured for real, it does not go in the video.

## The one rule

Real over fake, always. Shots come from the actual proxy, console or browser against the live host, and the numbers, tokens, records and status codes are the ones the server returned. When you cannot get a real capture, change the shot, not the truth.

## Workflow

1. Verify the exploit end to end against the live target before filming. Run it yourself and watch the real responses. If the intended bug does not fire, such as a patched sink or a degraded environment, pivot to one that does rather than fake it.
2. Capture real evidence for each step. Drive the proxy over its API so the shots are reproducible and need no manual clicking. For Burp, use a REST extension to send the request and screenshot the UI showing the real request and response.
3. Show the whole chain, not one step: the probe, the control holding (a tampered token returns 401), the bypass (the same request returns 200), and the data it unlocks. The negative control is what makes the success credible.
4. Show the payoff data. The response size, a real record, the enumerated accounts, so the viewer sees what was taken. Redact secrets in the frame while the data stays real.
5. Assemble with HyperFrames (https://github.com/heygen-com/hyperframes, run with npx hyperframes: init, check, render). Punch in on the exact proof text, add captions that point at what to look at, and hold every beat long enough to read.
6. Caption in plain language, the way a person writes. Full sentences that start with a capital. No em-dashes. No negative parallelism such as "not X but Y", "no X, no Y", or "it is not about X, it is Y". No problem/solution colon pairs or other formula scaffolds. State what happened, do not sell it.

## Self-questioning

- Is every frame a real capture from the live target, or did something get staged?
- Did I run the full chain and watch it return the status codes shown?
- Is the negative control in the video, so success is proven and not just claimed?
- Can a viewer actually read each step, or is it too fast?
- Are real secrets redacted in the frame while the data stays convincingly real?
- Do the captions read like a person wrote them, with no AI tells?
