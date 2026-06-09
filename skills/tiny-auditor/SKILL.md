---
name: tiny-auditor
description: Audit codebase to uncover critical issues explicitly without false positives
---

# List of always-true audit primitives:

## Formatting and Style
- Report format is consisted of ToC, Executive Summary, Findings Summary Table, Findings. If the report is around a single finding, only the finding should be there.
- Finding name format must be [C/H/M/L]-[Number] [Impact] via [Weakness] in [Feature]
- Finding name number should mark his relative severity next to all the other items of the same level (e.g. H-1 is more of a priority than H-2)
- Findings summary table should consist of ID (e.g. C-1), Risk, Status, and possible audit-spcificality that's key to track from a report reciever perspective) (e.g. if there are two environments tested then a column for prod and staging or env names might make sense
- Standard finding headings should be Severity, Probability, Locations, Description, Attack Flow, Remediations
- Finding headings should match across all findings of the report
- Locations are be bullets with github links with exact line references and commit path to the vulnerable sections of the code that directly create the vulnerability. If the audited item is not a code with direct gitlink, specifiy all the affected endpoints, or whatever it is insetad
- Description must be technically accurate but concise and abstract
- Description must follow "XXX is a feature that does XXX, During the audit it was found that XXX. Although `<protocol dispute point or mitigating factor if exists>`, An attacker that does XXX might.." - each portion should be logically separated with a newline to allow for easy clear reading
- If severity is uncertain (e.g. no clear poc) the finding description needs to end with a note explaining the realicim of it, while still emphasizing why it's still a risk.
- Attack Flow must be bullet-point breadcrumb trace of how an attacker might exploit the finding from gaining prerequisites to actual exploitation. if the finding is not exactly an attacker gets to X, it should be developer/employee makes mistake Y, etc.
- Remediations must be priority-sorted bullet items of fix recommendations to the team, usually, its one most-ideal fix and descending to next-best things that compliment/do 80% of the fix for 5% the effort. but if the best recommendations is the cleanest that's preferred.
- Remediations (especially 2nd 3rd and so on) might be complementary or additional but not really stopping the fix, if that's the case it should be clear from the way it is portrayed (e.g. As an extended blast-reduction, you may consider xxx)
- Remediations must be battletested and NOT introduce extra complexity and NEVER introduce other risks
- All text (finding name, description etc) needs to speak as if 80% certain because it should describe the vulnerable condition and the attack surface it opens, not assert the worst-case result as 100% guaranteed
- Extra thought processes, checks, and metadata is not relevant for the report itself - the report is about portraying the findings to the board
- No emojies, no unnecessary or repeating information, no fluff

## Severity classification
- Bug severity (C=4/H=3/M=2/L=1) should always be derived from `severity = (risk x probability)` when the highest severity is 16 and the lowest is 1 (end result low severity 1-4, medium severity 5-8, high severity 9-11, critical severity 12-16) - we never specify the risk numbers directly though
  - Risk calculation should be abstacted away and not written other than the resulting Severity and Probability
- Attacks that require a privileged pre-requisite (e.g. admin role) are instantly Low probability, with the exception of bugs that can arise due to normal routine done by a privileged admin
- Attacks that don't have a strong attacker incentive (attackonomics) are instantly low probability
- Comparative severity - in the same report, a Critical can't be of less severity than a Low
- Increase severities of bugs that directly affect business-critical assets or defy core protocol purpose
- Critical example: a bug exploitable by any unprivileged threat actor and leads to loss of funds or devistating security outcome
- If a bug has a very easy, ricochet-free mitigation plan - it can slightly increase its severity score
- Severity heirarchy - sometimes findings get removed added or reclassified which affects the order, so if we are enforcing a C1,C2,H1,M1,M2 heirarchy (in ToC, finding table, finding headings and possibel cross-references) and a change occured e.g. a new High was introduced which is more risk than existing H1, then H1->H2 and H1 takes its place and we update that everywhere on the page where needed
- Uncertain probabilities - if a finding probability is undetermined / unknown it should automatically be low, it's either we can prove some issue exists or we can't

## Scope
- Scope specificaltiy should be directly specified (even if it's "all" - it should be specified)
- Team-acknowledged issues must be mapped from code comments, docs an call summaries and be well-known as acknowledged findings. "acknowledged" means that the protocol is provenly aware of the issue and chose to ignore it as a business decision, in which case it does not fit a whole finding page but a bullet point explaining if its intended behavior, accepted risk, or mitigated outside visible scope.
- Previous audits, or knowledge of findings should be saved to a tracking table, but completely ignored when hunting for bugs (we need to find new ones, not already-known ones - also, who'se to say the previous auditors didn't make mistakes)
- Do not modify the audited code, unless you are writing PoC files or tests, in which case the test should have a comment at the top indicating its a temporary audit-phase AI-generated test and to ignore it in code review

## Audit Checks
- things in scope that should never break but might under specific conditions
- review code comments and documentation for spec-to-compliance mismatches
- review git commit history for bugs introduced and later fixed, rank security bug-introducers and audit their live code for open issues
- review git commit history for weakest security-mindset developers and audit their live code for open issues
- find security guards that are implemented on parts of the protocol but forgotten or misimplemented on siblings / similar code or logic blocks

## Proof of Concept
- It's always best to show the user a copy-paste, undisputable proof of the exploitability of the finding, e.g. PoC script, curl, or whatever is the normal interaction method with the audited codebase.
- Before claiming a PoC is real, we double check ourselfs to see it actually runs, produces expected results, and also check that the conditions of the PoC infact mimic a realistic attacker achievable scenario (no "synthetic sugar" for the exploitabilty)
- Sometimes, we got a critical risk without a poc possible, e.g. there's some pre-requisites that we don't have but an attacker is likely to obtain - in this case no poc is acceptable, but the evident of the attack hypothesis must be pointed at clearly and simply

## Threat Model
- An attack anatomy is like a flow graph going left-to-right.
  - on the rightest we got the "holy grail" a.k.a "business-crital asset" that is important to the audited protocol or team and is the point of attcking them
  - left to the holy grail we got the privileged situation/user/machine/service account or condition that natively accesses that holy grail for legitimate operations
  - left to that we got situation/user/machine/service account or condition that if abused correctly elevates to be in that legitimate operation, even if unintended for them (could be compromised dev, privesc-able endpoint etc)
  - on the most left we got the threat - attacker, public entity, direction of the incentivized entity from which the threat arrives
- Threat model helps us think and frame the attack as relevant to the protocol, as quality is important and we don't want false positives, its a helpful thinking excercise

# Self-validation loop
- Self-validation loop is not something to update in the report, just like a quality voice in the background to ensure high grade reports
- At each turn double-check accurracy and quality of produced findings
  - Did we truthfully match statements to code evidence?
  - Did we check items are all in scope?
  - Did we verify we are not contradicting acknowledged design tradeoffs or business protocol decisions?
  - Did we not miss-out on a real vulnerability?
  - Is the item a concerning security issue?
  - If the team receiving the issue were to challenge it, what would be their case? and is that case valid enough to dismiss the relevancy of the finding or not?
  - Do we have an item, that really just is a "moreover" sentence in another existing finding?
  - Is the finding assuming privileged breach level? and if so - wouldn't that privilege being breached would be devistating either way, making the security work around it almost redundant?
  - Is the impact at the end of the description aligned enough to the real mature version of the exploitation and certain?
- Is the severity classification changed and do we need to update it anywhere?
