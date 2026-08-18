---
kind: goal
schema: goal.v1
name: bounty
description: Land one critical, reproducible bug on a bounty program's in-scope target.
end_state:
  - A critical finding whose PoC reproduces from a clean environment via a repeatable script
  - A short report naming the affected component, what the attacker gains, and the fix
proof:
  - Re-run the PoC from a clean environment every turn - it reproduces exactly, or it isn't a finding
guardrail:
  invariants:
    - Nothing out of scope; read the program policy first and reproduce only on assets you own
  allowed_paths:
    - notes/**
    - pocs/**
termination:
  stop_on:
    - the PoC reproduces from a clean environment and the report is written
    - scope is exhausted with no critical candidate left
    - three turns pass with no new lead
---

`/goal Reach A critical finding whose PoC reproduces from a clean environment via a repeatable script, plus A short report naming the affected component, what the attacker gains, and the fix. Re-run the PoC from a clean environment every turn - it reproduces exactly, or it isn't a finding. Nothing out of scope; read the program policy first and reproduce only on assets you own - touch only notes/** and pocs/**. Stop when the PoC reproduces from a clean environment and the report is written, when scope is exhausted with no critical candidate left, or when three turns pass with no new lead.`
