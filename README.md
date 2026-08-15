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

Skills are grouped into category folders under `skills/`. Discovery is flat, so the folders are for organization only; each skill still lives at `skills/<category>/<name>/SKILL.md`.

## Applicative pentest

`skills/applicative-pentest/` - portable, tool-agnostic web-app testing methodologies (curl/python3, no scanner required), each with runnable snippets and the wordlists/regexes/thresholds inline or in `references/`.

- `ssrf-oob` - active out-of-band SSRF probe; injects an OAST/collaborator callback into request-forwarding params and client-IP headers, then watches for the DNS/HTTP interaction that proves a blind server-side request.
- `http-request-smuggling` - active HTTP desync detection for CL.TE and TE.CL via raw socket requests, using timing probes plus differential-response confirmation with the exact payloads.
- `jwt-attacks` - forges and re-signs captured JWTs to test signature validation (alg:none, signature stripping, kid traversal, jwk/jku injection, RS256/HS256 confusion) plus offline HMAC secret cracking.
- `broken-access-control` - active authorization and IDOR testing by replaying captured requests with swapped identities and incremented object-ids, carrying the response-diff thresholds that decide a finding.
- `webapp-probe` - assesses what a web app exposes or leaks, passively from captured traffic (headers, cookies, secrets, error pages, tech fingerprints, RCE-prone params) and actively (exposed files, vulnerable software on open ports, Wayback endpoints, dependency confusion).
- `cdn-peek` - checks whether a CDN/WAF-fronted host is reachable outside its edge, using only dig, curl, openssl, whois, and nc; works against any reverse-proxy edge.

<br>

## Blockchain

`skills/blockchain/` - smart-contract auditing and on-chain investigation.

- `smart-contract-audit` - full smart contract audit framework with multi-expert analysis for Solidity, Anchor, Vyper, TON (FunC/Tact), and Sui (Move), with language-specific checks and vulnerability pattern references.
- `foundry-poc` - context-window-optimized skill to generate a Foundry proof of concept for a discussed finding.
- `blockchain-forensics` - trace stolen funds and attribute attacker wallets using only public on-chain data; also useful for deployer history and privileged-role validation during audits.
- `safe-hunt` - sweeps DeFi protocol Safe multisig wallets for governance misconfigurations, scoring each against a finding pattern library and producing an audit-ready ranked report.

<br>

## Cloud

`skills/cloud/` - cloud and infrastructure exposure.

- `cloud-bucket-brute` - active enumeration of publicly readable cloud-storage buckets; permutes a company name into candidate bucket names and probes AWS S3, Google Cloud, DigitalOcean, Alibaba, Oracle, and Vultr.
- `infrastructure-audit` - infrastructure security audit framework for IaC, Docker, Kubernetes, and cloud configurations; audits generate numbered folders in `.context/outputs/` for tracking and reports.

<br>

## Hunter utils

`skills/hunter-utils/` - general auditing methodology and workflow tooling picked up naturally as you travel through a codebase.

- `tiny-auditor` - context-window-optimized audit skill; think caveman for audits.
- `auditor-quiz` - get engaged with the codebase from a security-auditor perspective and test how well you memorized it by quizzing yourself.
- `audit-scope` - generate a security audit scope document from GitHub repo URLs and/or API access descriptions, with a protocol narrative and a scope table (NSLOC, focus areas, days).
- `sandboxed-audit-runner` - wraps the agent session inside the Anthropic Sandbox Runtime before auditing untrusted code, protecting the host from prompt-injection embedded in the codebase.
- `agent-onboarding` - onboard concurrent agents to a shared TODO.md so parallel auditing terminals sync work and keep coverage tracking.
- `gdocs-audit-report` - create, format, and maintain security audit reports in Google Docs via the Docs API, covering finding formatting, summary tables, severity colors, and index-drift safety.
- `git-commit` - before committing, pre-runs tests, security-reviews changed code, strips dead code and sensitive data, enforces clean commit messages, and validates the change won't break deployments.
- `context-window-to-skill` - converts a completed agent conversation into a reusable skill, extracting the pitfalls, tweaks, and lessons so the next run gets it right from the start.

<br>

## Defensive

`skills/defensive/` - blue-team and DFIR.

- `endpoint-threat-hunt` - live endpoint threat hunting across process/file/network/persistence/registry categories using native OS tools (macOS/Linux/Windows), producing a structured findings report with explicit coverage gaps.

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

