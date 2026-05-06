---
name: tiny-auditor
description: Audit codebase to uncover critical issues explicitly and certainly leading to loss of funds without false positives
---

List of always-true audit primitives:

## Formatting
- Finding name format must be [C/H/M/L]-[Number] [Impact] via [Weakness] in [Feature]

## Severity classification
- Bug severity (C=4/H=3/M=2/L=1) should always be derived from `severity = (risk x probability)` when the highest severity is 16 and the lowest is 1 (end result low severity 1-4, medium severity 5-8, high severity 9-11, critical severity 12-16)
  - Risl calculation should be abstacted away and not written other than the resulting Severity and Probability
  - Attacks that require a privileged pre-requisite (e.g. admin role) are instantly Low probability
  - Attacks that don't have a strong attacker incentive (attackonomics) are instantly low probability
  - Comparative severity - in a single report, a Critical can't be of less severity than a Low
  - Critical example: a bug exploitable by any unprivileged threat actor and leads to loss of funds

## Scope
- Scope specificaltiy should be directly specified (even if it's "all" - it should be specified)
- Team-acknowledged issues must be mapped from code comments, docs an call summaries and be well-known as acknowledged findings. "acknowledged" means that the protocol is provenly aware of the issue and chose to ignore it as a business decision, in which case it does not fit a whole finding page but a bullet point explaining if its intended behavior, accepted risk, or mitigated outside visible scope.
- Previous audits, or knowledge of findings should be saved to a tracking table, but completely ignored when hunting for bugs (we need to find new ones, not already-known ones - also, who'se to say the previous auditors didn't make mistakes)
