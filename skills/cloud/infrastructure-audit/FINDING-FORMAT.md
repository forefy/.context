### 5.1 Conservative Severity Calibration Framework

**MANDATORY SEVERITY CALCULATION - ALWAYS PREFER LOWER SEVERITY:**
When uncertain between two severity levels, ALWAYS choose the lower one. This conservative approach prevents overestimation of risk and maintains credibility.

```markdown
SEVERITY FORMULA: Impact × Likelihood × Exploitability = Base Score
Then apply CONSERVATIVE ADJUSTMENT: If Base Score is borderline, round DOWN

CRITICAL (9.0-10.0): Reserved for immediate system compromise with high business impact
HIGH (7.0-8.9): Significant security compromise with clear business impact  
MEDIUM (4.0-6.9): Security vulnerabilities requiring attention but with limited immediate impact
LOW (1.0-3.9): Security improvements and defensive measures

IMPACT SCORING (Conservative):
- High Impact (3): Complete system compromise, all data exposed, full service outage
- Medium Impact (2): Partial compromise, sensitive data exposed, major feature disruption  
- Low Impact (1): Limited access, non-sensitive data, minor service impact

LIKELIHOOD SCORING (Conservative):
- High Likelihood (3): Vulnerability is easily discoverable and exploitable by script kiddies
- Medium Likelihood (2): Requires moderate skill and effort to discover and exploit
- Low Likelihood (1): Requires advanced skills, specific conditions, or insider knowledge

EXPLOITABILITY SCORING (Conservative):  
- High Exploitability (3): One-click exploit, publicly available tools, no authentication required
- Medium Exploitability (2): Requires some technical skill, multi-step process, or authentication
- Low Exploitability (1): Requires advanced expertise, perfect timing, or multiple prerequisites
```

**FINDING FORMAT:**
Ensure findings created follow this format very strictly:

```markdown
## [C/H/M/L]-[Number] [Impact] via [Weakness] in [Feature]

### Core Information
**Severity:** [Critical/High/Medium/Low - conservative assessment]

**Probability:** [High/Medium/Low - conservative assessment]

**Confidence:** [High/Medium/Low - based on verification depth]

**Component:** [Exact infrastructure component name]

**Configuration:** [Specific configuration file or setting]

**Location:** [File path and line numbers]

### User Impact Analysis
**Innocent User Story:**
```mermaid
graph LR
    A[User] --> B[Normal Action: [User performs intended infrastructure interaction]]
    B --> C[Expected Outcome: [User receives expected service access]]
```
*Note: Use proper mermaid syntax with valid node IDs (A, B, C, etc.) and avoid special characters in labels. Ensure all arrows use correct syntax (-->) and labels are enclosed in square brackets.*

**Attack Flow:**
```mermaid
graph LR
    A[Attacker] --> B[Attack Step 1: [Attacker performs initial reconnaissance]]
    B --> C[Attack Step 2: [Attacker exploits infrastructure weakness]]
    C --> D[Attack Step 3: [Attacker achieves unauthorized access]]
    D --> E[Final Outcome: [Attacker compromises infrastructure]]
```
*Note: Create clear, linear attack flows with descriptive but concise labels. Each step should logically follow the previous one. Avoid complex branching unless necessary for clarity.*

### Technical Details
**Locations:** 
- [../../../path/to/config-file.yaml:LXX-LYY](../../../path/to/config-file.yaml#LXX-LYY)
- [../../../path/to/another-config.json:LXX-LYY](../../../path/to/another-config.json#LXX-LYY)

**Description:** 
[Technical explanation of the security misconfiguration or vulnerability. Include:
- TL;DR summary of what was located during assessment
- How an attacker might abuse this vulnerability
- What is the impact on infrastructure and business operations
- Approximately half a page of detailed technical context]

### Business Impact
**Exploitation:** 
[Real-world exploitation scenario with business context and infrastructure-specific impact.
Include:
- Realistic attack timeline and prerequisites
- Business operations affected
- Customer/user impact
- Financial and reputational consequences
- Regulatory/compliance implications]

### Verification & Testing
**Verify Options:** 
[Manual checks needed to confirm this finding:
- Specific commands to run
- Configuration files to check
- Tests to perform]

**PoC Verification Prompt:** 
[LLM prompt that you would write to real-life test this vulnerability to 100% prove it's not a false positive:
- Exact steps to reproduce
- Expected vs actual results
- Success criteria for exploitation]

### Remediation
**Recommendations:** 
[Actionable practical recommendations for remediation:
- Primary fix with exact configuration changes
- Alternative solutions if applicable
- Best practice implementation guidance
- Verification steps to confirm fix]

### References
**KB/Reference:** 
- [Relevant security standards, frameworks, or documentation]
- [Knowledge base references if applicable: `.context/knowledgebases/...`]

### Expert Attribution

**Discovery Status:** [Found by Expert 1 only / Found by Expert 2 only / Found by both experts]

**Expert Oversight Analysis:** [If only found by one expert, the other expert should analyze why they missed it - e.g., "Expert 2 acknowledges missing this due to focusing on different security layers", "Expert 1 doesn't consider this a valid vulnerability because...", "Expert 2 overlooked this configuration during systematic review"]


### Triager Note
[VALID/QUESTIONABLE/DISMISSED/OVERCLASSIFIED] - [Contextual bounty assessment based on security budget analysis from Step 2.

**Bounty Assessment:** 
- VALID findings: Provide specific bounty amount ($X,XXX) based on exploitability evidence, business impact, and realistic attack scenarios in current environment
- QUESTIONABLE findings: Explain additional proof needed - no bounty recommended until validation
- DISMISSED findings: Technical reasons why not exploitable in practice
- OVERCLASSIFIED findings: Valid vulnerability but severity was exaggerated - suggest correct severity level and adjusted bounty

**Reality Check Factors:** Consider privileged-only access, existing mitigations, business impact scale, and practical vs theoretical exploitability. Low severity findings merit small bounties ($50-$200) for infrastructure best practice improvements even if somewhat theoretical, as they fit the severity level appropriately.]
```
