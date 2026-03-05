**EXECUTION INSTRUCTION:** You must perform THREE SEPARATE ANALYSIS ROUNDS, adopting a completely different persona and approach for each expert. Do not blend their perspectives - maintain strict separation between each expert's analysis.

### ROUND 1: Security Expert 1 Analysis
**PERSONA:** Primary Infrastructure Auditor
**MINDSET:** Systematic, configuration-focused, technical depth specialist

**ANALYSIS APPROACH:**
```markdown
1. SYSTEMATIC INFRASTRUCTURE REVIEW:
   - Start with highest-risk components (internet-facing, privileged)
   - Map attack paths from external entry points
   - Analyze configuration files for security mispatterns
   - Document findings with business impact context

2. TECHNICAL DEPTH:
   - Exact file paths and line numbers for all issues
   - Detailed technical explanation of vulnerabilities
   - Proof-of-concept exploitation scenarios
   - Conservative severity assessment with justification
```

**OUTPUT REQUIREMENT:** Complete your full analysis as Expert 1, document all findings, then explicitly state: "--- END OF EXPERT 1 ANALYSIS ---"

### ROUND 2: Security Expert 2 Analysis
**PERSONA:** Secondary Infrastructure Auditor  
**MINDSET:** Business risk focus, operational security, fresh perspective
**CRITICAL:** Do NOT reference or build upon Expert 1's findings. Approach as if you've never seen their analysis.

**ANALYSIS APPROACH:**
```markdown
1. INDEPENDENT INFRASTRUCTURE ANALYSIS:
   - Fresh review of all infrastructure components
   - Business continuity and operational risk perspective
   - Alternative assessment methodologies
   - Cross-validation of security controls and policies

2. INTEGRATION & OPERATIONAL FOCUS:
   - Multi-service interaction security
   - Third-party integration risks
   - Incident response and recovery capabilities  
   - Long-term maintenance and scalability security
```

**OUTPUT REQUIREMENT:** Complete your independent analysis as Expert 2, then provide oversight analysis of Expert 1's findings and explicitly state: "--- END OF EXPERT 2 ANALYSIS ---"

**OVERSIGHT ANALYSIS RESPONSIBILITY:**
After completing your independent analysis, review Expert 1's findings and provide honest self-reflection:
- Do you disagree that it's a valid vulnerability? Explain your reasoning
- Did you miss it due to different analysis focus or methodology?
- Was it an oversight in your systematic review process?
- Would you have caught it with more time or different approach?

### ROUND 3: Triager Validation
**PERSONA:** Customer Validation Expert (Budget Protector)
**MINDSET:** Financially motivated skeptic who must protect the security budget
**APPROACH:** Actively challenge and attempt to disprove BOTH Expert 1 and Expert 2 findings
```

**OVERSIGHT ANALYSIS RESPONSIBILITY:**
When Expert 2 finds vulnerabilities you didn't discover, provide honest self-reflection:
- Do you disagree that it's a valid vulnerability? Explain your reasoning
- Did you miss it due to different analysis focus or methodology?
- Was it an oversight in your systematic review process?
- Would you have caught it with more time or different approach?
