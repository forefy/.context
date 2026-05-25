---
name: tiny-auditor
description: Audit codebase to uncover critical issues explicitly and certainly leading to loss of funds without false positives
---

List of always-true audit primitives:

## Scope
- Scope specificaltiy should be directly specified (even if it's "all" - it should be specified)
- Team-acknowledged issues must be mapped from code comments, docs an call summaries and be well-known as acknowledged findings. "acknowledged" means that the protocol is provenly aware of the issue and chose to ignore it as a business decision, in which case it does not fit a whole finding page but a bullet point explaining if its intended behavior, accepted risk, or mitigated outside visible scope.
- Previous audits, or knowledge of findings should be saved to a tracking table, but completely ignored when hunting for bugs (we need to find new ones, not already-known ones - also, who'se to say the previous auditors didn't make mistakes)
- Do not modify the audited code, unless you are writing PoC files or tests, in which case the test should have a comment at the top indicating its a temporary audit-phase AI-generated test and to ignore it in code review

## Checks
- things in scope that should never break but might under specific conditions
- review git commit history for bugs introduced and later fixed, rank security bug-introducers and audit their live code for open issues
- review git commit history for weakest security-mindset developers and audit their live code for open issues

## Formatting and Style
- Finding name format must be [C/H/M/L]-[Number] [Impact] via [Weakness] in [Feature]
- Standard finding headings should be Severity, Probability, Locations, Description, Attack Flow, Remediations
- Locations are be bullets with github links with exact line references and commit path to the vulnerable sections of the code that directly create the vulnerability
- Description must be technically accurate but concise and abstract
- Remediations must be priority-sorted bullet items of fix recommendations to the team
- All text (finding name, description etc) needs to speak as if 90% certain because it should describe the vulnerable condition and the attack surface it opens, not assert the worst-case result as 100% guaranteed

## Severity classification
- Bug severity (C=4/H=3/M=2/L=1) should always be derived from `severity = (risk x probability)` when the highest severity is 16 and the lowest is 1 (end result low severity 1-4, medium severity 5-8, high severity 9-11, critical severity 12-16)
  - Risk calculation should be abstacted away and not written other than the resulting Severity and Probability
- Attacks that require a privileged pre-requisite (e.g. admin role) are instantly Low probability, with the exception of bugs that can arise due to normal routine done by a privileged admin
- Attacks that don't have a strong attacker incentive (attackonomics) are instantly low probability
- Comparative severity - in the same report, a Critical can't be of less severity than a Low
- Increase severities of bugs that directly affect business-critical assets or defy core protocol purpose
- Critical example: a bug exploitable by any unprivileged threat actor and leads to loss of funds
- If a bug has a very easy, ricochet-free mitigation plan - it can slightly increase its severity score
