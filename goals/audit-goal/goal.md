---
kind: goal
schema: goal.v1
name: audit-goal
description: Hunt criticals on the highest-value attack surface until they stop paying for their tokens.
end_state:
  - Every critical found is proven with a PoC that runs under realistic attacker conditions
  - High-value paths to a business-critical asset hunted until new criticals stop surfacing per unit of budget
  - Every 'no critical here' on high-value surface refuted, not assumed
proof:
  - Each critical's PoC runs under attacker-achievable conditions with no synthetic sugar, or it isn't a finding
  - Each 'clean' verdict on high-value surface survives a refute pass, or that surface re-opens
guardrail:
  invariants:
    - Authorized scope only; reproduce only on assets you own
    - Hunt the highest expected-value surface first, ranked by incentive x reachability
    - Low-value surface that gets de-scoped is logged with its reason, never dropped silently
  allowed_paths:
    - notes/**
    - pocs/**
termination:
  stop_on:
    - new criticals per unit of budget fall below the diminishing-returns floor and every found critical is proven with a running PoC
    - every high-value surface is either exhausted or consciously de-scoped with a logged reason, and every high-value 'no critical here' has been refuted
    - budget is spent
---
