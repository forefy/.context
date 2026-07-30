---
kind: loop
schema: goal.v3
name: k8-bugbounty
description: Land one critical, reproducible bug on hackerone.com/kubernetes.
end_state:
  - A critical finding whose PoC reproduces from a clean cluster via a repeatable script
  - A short report naming the affected component, what the attacker gains, and the fix
proof:
  - Re-run the PoC from a clean cluster every turn — it reproduces exactly, or it isn't a finding
guardrail:
  invariants:
    - Nothing out of scope; reproduce on a cluster you own
  allowed_paths:
    - notes/**
    - pocs/**
termination:
  stop_on:
    - the PoC reproduces from a clean cluster and the report is written
    - scope is exhausted with no critical candidate left
    - three turns pass with no new lead
---

`/goal Reach A critical finding whose PoC reproduces from a clean cluster via a repeatable script, plus A short report naming the affected component, what the attacker gains, and the fix. Re-run the PoC from a clean cluster every turn — it reproduces exactly, or it isn't a finding. Nothing out of scope; reproduce on a cluster you own — touch only notes/** and pocs/**. Stop when the PoC reproduces from a clean cluster and the report is written, when scope is exhausted with no critical candidate left, or when three turns pass with no new lead.`
