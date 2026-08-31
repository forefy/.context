---
kind: goal
schema: goal.v1
name: error-handling-passive
description: Against a live application's public surface (given its domains or endpoints), flush out error-handling defects observable from the outside - leaked internals, wrong status semantics, server faults on benign input, framework-default error pages - using only unauthenticated, non-mutating, polite requests that observe how the app responds, never exploit it, until the reachable surface is exhausted.
end_state:
  - A concise list of error-revealing responses on the target, each linking the exact request that triggers it to the revealing excerpt - a stack trace, an internal path or hostname, a framework or language and version, a database or query error, a config value or secret, or PII surfaced in an error body or header
  - The list is the whole deliverable - no coverage report, no route inventory, no catalog of correctly-handled or trivial responses; if nothing non-trivial is revealed, that is the entire result, stated in one line
  - Nothing trivial or already-public is listed - a bare platform request-id, a generic not-found string, a server-name header, or a version already shown on the homepage is not a finding; only disclosures that hand an attacker non-public internal detail
proof:
  - Each listed item carries the full request and raw response captured this run - the request line, response status and headers, and the verbatim response body in a fenced code block (trimmed only where a long body just repeats) - reproducible by re-issuing the same benign request, never inferred from behavior elsewhere
  - Anything not clearly disclosing non-public internals is dropped, never listed as a maybe or padded into the output
guardrail:
  invariants:
    - Authorized scope is the given domains or endpoints only; only the target's own public surface is touched, never a third-party dependency it calls
    - Passive and non-intrusive - unauthenticated, benign, read-only requests that do not mutate state, place no meaningful load, and never exploit; probes vary inputs to observe error handling, they never attack
    - No state-changing or destructive methods against real data - no writes, deletes, submits, or purchases; a form or mutating endpoint is described as a gap to observe safely, never fired with live effect
    - Rate stays polite - a handful of targeted edge requests per route, never flooding, volume fuzzing, or automated brute force
    - Every listed item is evidence-backed by a response observed this run; a suspected disclosure with no captured response is dropped, never asserted
  allowed_paths:
    - notes/**
    - findings/**
termination:
  stop_on:
    - benign edge inputs across the reachable surface stop surfacing any new error-revealing response
    - every listed item is a captured, reproducible disclosure of non-public internals, and every trivial or unverified candidate has been dropped from the output
---
