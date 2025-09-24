# AI Agent Instructions for Smart Contract Auditing

<p align="center">
<a href="https://github.com/forefy/.context/edit/main/agents/github_copilot/copilot-instructions-smart-contracts-generic.md"><img alt="Contribute" title="Contribute to copilot-instructions.md" src="https://img.shields.io/badge/Contribute-copilot--instructions.md-blue?logo=github"></a>
<img alt="GitHub last commit" title="GitHub last commit" src="https://img.shields.io/github/last-commit/forefy/.context">
<a href="https://twitter.com/forefy"><img alt="Forefy Twitter" title="Forefy Twitter" src="https://img.shields.io/twitter/follow/forefy.svg?logo=twitter"></a>

</p>

## What is this?

A collection of prompts and agent instructions to be used by security auditors, aimed to maximize context window efficiency to the needs of a security audit, when using a general purpose coding agent like copilot.

<p align="center">
<img src="static/example-1.png" alt="Before: .context reop setup" width="600">
<br><br>
<span style="font-size: 24px;">↓</span>
<br><br>
<img src="static/example-2.png" alt="After: Starting security analysis" width="300">
</p>

Benefits of this approach over a vertical auditing agent:
* Faster way to incorporate your audit methodologies within an AI agent (text instead of code)
* Ability to turn a top-tier benchmarked coding agent (like copilot) to your vertical auditing agent
* Ability to share prompts across audit team members that prefer different agents
* If you use github copilot, a pricing model of monthly payments, instead of API pay-per-usage billing


## How to use?

1. Follow one of the instruction installations from below to clone this repo (`.context`) to the root of the audited workspace, and get the agent of your choice to be contextually tuned.
2. On "Human in the Loop" scenarios, continue chatting normally or use the `prompts` folder to prompt in a way optimized to the built context.

## Installation options

### <img src="https://github.githubassets.com/images/modules/site/copilot/copilot.png" width="16" height="16" alt="GitHub Copilot"> GitHub Copilot (Generic Smart Contract Audit)

```bash
git clone https://github.com/forefy/.context > /dev/null 2>&1 && mkdir -p .github/ && cp .context/agents/github_copilot/copilot-instructions-smart-contracts-generic.md .github/copilot-instructions.md && echo "\\n [ .context ] Custom copilot instructions copied to workspace."
```

### <img src="https://github.githubassets.com/images/modules/site/copilot/copilot.png" width="16" height="16" alt="GitHub Copilot"> GitHub Copilot (Generic Infrastructure as Code Audit)

```bash
git clone https://github.com/forefy/.context > /dev/null 2>&1 && mkdir -p .github/ && cp .context/agents/github_copilot/copilot-instructions-iac.md .github/copilot-instructions.md && echo "\\n [ .context ] Custom copilot instructions copied to workspace."
```

### <img src="https://claude.ai/favicon.ico" width="16" height="16" alt="Claude"> Claude Code (Solidity Audit)

```bash
git clone https://github.com/forefy/.context > /dev/null 2>&1 && mkdir -p .claude/commands/ && cp .context/agents/claude_code/security-review-solidity.md .claude/commands/security-review.md && echo "\\n [ .context ] Custom Solidity auditing security-review instructions copied to workspace."

claude security-review
```

### <img src="https://claude.ai/favicon.ico" width="16" height="16" alt="Claude"> Claude Code (Anchor/Solana Audit)

```bash
git clone https://github.com/forefy/.context > /dev/null 2>&1 && mkdir -p .claude/commands/ && cp .context/agents/claude_code/security-review-anchor.md .claude/commands/security-review.md && echo "\\n [ .context ] Custom Anchor/Rust auditing security-review instructions copied to workspace."

claude security-review
```

## Prompts

Files under the `prompts/` folder provide a quick way to ask the instructions-loaded agent to work for you in different ways. These are usually small simple requests that take in account that the major instructions are already picked up through the regular instruction files in this repo.

### Prompt Structure

Each prompt follows a structured YAML format:

```yaml
- expected_inputs:
    [List of inputs the agent should expect]
    [File types, data sources, context requirements]

- expected_actions:
    - action_type:
        [Specific tasks to perform]
        [Analysis requirements]
        [Output specifications]
```

### Available Prompts Example

- **`generate_audit_report_generic.md`** - Generates comprehensive audit documentation including visual threat models, protocol analysis, and detailed audit reports from codebase scope
- **`consolidate_audit_reports.md`** - Consolidates multiple audit reports from the `.context/outputs` directory into a single report containing only validated findings that appear consistently across runs
- **`triage_audit_findings_generic.md`** - Reviews and validates audit findings by removing false positives, adjusting severity levels, and keeping only accurate vulnerabilities

## Vulnerabilities Knowledgebases

The `knowledgebases/` directory contains a collection of vulnerability patterns and security issues of a specific domain. The instructions are configured to selectively use those vulnerability patterns as part of the assessment.

## Audit Output and Logging

When agents perform security assessments using these instructions, they automatically generate comprehensive audit trails:

### Output Structure
- **`.context/outputs/1/`, `.context/outputs/2/`, etc.** - Numbered folders containing complete audit runs
- **`audit-report.md`** - Final security assessment with findings and recommendations  
- **`audit-context.md`** - Key assumptions, scope boundaries, and finding summaries
- **`audit-debug.md`** - Detailed technical log of agent analysis performed

## Contributing

Contributions are welcome. Focus on improvements that benefit the entire auditing community while keeping your proprietary techniques private.
