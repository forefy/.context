<h1 align="center">.context</h1>

<p align="center">
  <img src="static/logo.svg" alt="pocer" width="180">
</p>

<p align="center">
 <b>An optimized collection of AI agent skills, loops and workflows for security auditing</b>
</p>
<p align="center">
  <a href="https://github.com/forefy/.context/issues/new/choose"><img alt="Issues" title="Issues" src="https://img.shields.io/github/issues-raw/forefy/.context"></a>
  <img alt=".context GitHub repo size" title=".context GitHub repo size" src="https://img.shields.io/github/languages/code-size/forefy/.context">
  <img alt=".context GitHub commit activity" title=".context GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/forefy/.context">
  <img alt="GitHub last commit" title="GitHub last commit" src="https://img.shields.io/github/last-commit/forefy/.context">
  <a href="https://twitter.com/forefy"><img alt="Forefy Twitter" title="Forefy Twitter" src="https://img.shields.io/twitter/follow/forefy.svg?logo=twitter"></a>
  <a href="https://github.com/forefy/.context/actions/workflows/warden.yml"><img alt="skill-warden" title="skill-warden" src="https://github.com/forefy/.context/actions/workflows/warden.yml/badge.svg"></a>
</p>

<p align="center">
  <img src="https://claude.com/images/claude_app_icon.png" width="16" height="16" alt="">&nbsp;Claude Code &nbsp;·&nbsp; <img src="https://github.githubassets.com/images/modules/site/copilot/copilot.png" width="16" height="16" alt="">&nbsp;Copilot &nbsp;·&nbsp; <img src="https://avatars.githubusercontent.com/u/161781182?s=48&v=4" width="16" height="16" alt="">&nbsp;Gemini &nbsp;·&nbsp; <img src="https://avatars.githubusercontent.com/u/14957082?s=48&v=4" width="16" height="16" alt="">&nbsp;Codex
</p>

<p align="center">
 <a href="https://t.me/forefy_t" title="forefy Telegram">Telegram DM</a>
</p>


# Installation

## Agents:
Paste in your chat:
```
Run the AI Security Registry installation wizard https://github.com/forefy/.context/blob/main/install.md
```

## Manual
1. Data maintained in this repo is also listed on https://forefy.com/aisecurity
2. Search and download from there via easy installation button

<br>

# What is this?

Security auditing skills for AI agents, adhering to the [Agent Skills Format](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

`.context` is one of the oldest efforts by security researchers to share auditing knowledge directly to your AI agent, and is built gradually over time. at the most simple form, you type "audit this contract" and end up with a multi-agent triaged AI report.

<br>

# About the Skills

## Comprehensive audit

Optimized for protocol developers to use pre-audit, or for auditors expirementing with AI skills.

- `smart-contract-security-audit` - Full smart contract audit framework with multi-expert analysis for Solidity, Anchor, Vyper, TON (FunC/Tact), and Sui (Move). Includes language-specific checks and vulnerability pattern references.

- `infrastructure-security-audit` - Infrastructure security audit framework for IaC, Docker, Kubernetes, and cloud configurations. audits generate numbered folders in `.context/outputs/` for tracking and reports

<br>

## Daily-use security skills

Daily skills are designed to be picked up naturally as you travel through a codebase in your auditing process, and strategically fill context into a specific task.

- `auditor-quiz` - Quick skill to get yourself engaged with the codebase from a security auditor perspective (but also from protocol dev perspective) and test how well you memorized it by quizing yourself.

- `tiny-auditor` - context window optimized audit skill - think caveman for audits. 

- `foundry-poc` - context window optimized skill to generate a foundry proof of concept for a discussed finding.

- `sandboxed-audit-runner` - wraps the entire agent session inside the Anthropic Sandbox Runtime before starting any audit on untrusted code. Protects the host from prompt injection attacks embedded in the codebase - malicious comments, filenames, or configs designed to make the agent exfiltrate keys or make unauthorized network calls.

- `agent-onboarding` - agents are pre-instructed to get familiar with the code before anything, but also tracka. shared TODO.md - when you are in focus mode in your auditing you should have at least 4 concurrent AI terminals running. To sync their work, as well as keep quality coverage tracking of your audit, you can onboard agents to the team with a purpose (e.g. "Onboard to team to look for issues in recent commits only")

- `gdocs-audit-report` - expert skill for creating, formatting, and maintaining security audit reports in Google Docs via the Docs API. Covers finding formatting, summary tables, inline code styling, severity color schemes, index-drift safety, and all common Docs API pitfalls.

- `blockchain-forensics` - Trace stolen funds, attribute attacker wallets, using only public on-chain data. Also useful during audits for checking deployer history, validating privileged roles, and understanding how past exploits on similar protocols played out on-chain.

- `safe-hunt` - Sweeps DeFi protocol Safe multisig wallets for governance misconfigurations and security weaknesses. Given a protocol name, Safe address, or "sweep all", fetches live config and tx history from the Safe Transaction Service API, scores each Safe against a finding pattern library, and produces an audit-ready ranked report.

- `git-commit` - before letting the agent blind-commiting your code, it pre-runs tests, security reviews changed code, strips dead code and sensitive data it finds, enforces clean commit messages and validates the change won't break deployments.

- `context-window-to-skill` - converts a completed agent conversation into a reusable skill. extracts the pitfalls, tweaks, and lessons from the session so the next run gets it right from the start.

<br>

# Quality

Skills, workflows and loops are following industry best practice and guidance (e.g. we read the docs):
- [Agent Skills open standard](https://github.com/agentskills/agentskills)
- [Claude Code Dynamic Workflows](https://code.claude.com/docs/en/workflows)

And are CI-validated by in-repo, versioned json-schema files:
- [https://github.com/forefy/.context/schemas](https://github.com/forefy/.context/blob/main/schemas)

.context skills are CI-level security-audited via `skill-warden`, skills, loops and workflows are validated on the AI Security Registry.

<br>


# Contributions

<table>
<tr>
    <td align="center">
        <a href="https://github.com/forefy">
            <img src="https://avatars.githubusercontent.com/u/166978930?v=4" width="100;" alt="forefy"/>
            <br />
            <sub><b>forefy</b></sub>
        </a>
    </td>
</tr>
</table>

Your research knowledge is the only skill required to contribute, whether its a methodology, specific knowledge on a protocol or language or even corrections - everything's highly welcome! help secure and improve the community!

