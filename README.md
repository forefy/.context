# LLM Instructions for Smart Contract Auditing

<p align="center">
<a href="https://github.com/forefy/.context/edit/main/copilot-instructions.md"><img alt="Contribute" title="Contribute to copilot-instructions.md" src="https://img.shields.io/badge/Contribute-copilot--instructions.md-blue?logo=github"></a>
<img alt="GitHub last commit" title="GitHub last commit" src="https://img.shields.io/github/last-commit/forefy/.context">
<a href="https://twitter.com/forefy"><img alt="Forefy Twitter" title="Forefy Twitter" src="https://img.shields.io/twitter/follow/forefy.svg?logo=twitter"></a>

</p>

## What is this?

Smart Contract Auditors are using agentic AI to uncover potential leads, learn the codebase faster, and even generate PoC's for exploits from time to time.

This is just a side tool though, and the human is what counts. This repo aims to empower the human-to-agent interactions, by incorporating auditing methodologies and way-of-thinking, so that when these agents are used they are supercharged with community insight focusing on providing more qualitative results.

## Setup locally - choose the relevant command and run from the project root directory

Open your project in VS Code and install the GitHub Copilot extension if you haven't already.

For best results, copy `.context` to your audited workspace root, and the instructions to their expected directory, via one of the following commands:

### <img src="https://github.githubassets.com/images/modules/site/copilot/copilot.png" width="16" height="16" alt="GitHub Copilot"> GitHub Copilot (Generic Smart Contract Audit)

```bash
git clone https://github.com/forefy/.context && mkdir -p .github/ && cp .context/copilot-instructions-smart-contracts-generic.md .github/copilot-instructions.md && echo "\\n [ .context ] Custom copilot instructions copied to workspace."
```

### <img src="https://claude.ai/favicon.ico" width="16" height="16" alt="Claude"> Claude Code (Solidity)

```bash
git clone https://github.com/forefy/.context && mkdir -p .claude/commands/ && cp ../.context/security-review-solidity.md .claude/commands/security-review.md && echo "\\n [ .context ] Custom Solidity auditing security-review instructions copied to workspace."
claude security-review
```

### <img src="https://claude.ai/favicon.ico" width="16" height="16" alt="Claude"> Claude Code (Anchor/Solana)

```bash
git clone https://github.com/forefy/.context && mkdir -p .claude/commands/ && cp ../.context/security-review-anchor.md .claude/commands/security-review.md && echo "\\n [ .context ] Custom Anchor/Rust auditing security-review instructions copied to workspace."
claude security-review
```

## Preprompting
Files under the `preprompts/` folder provide a quick way to ask the instructions-loaded agent to work for you in different ways. These are usually small simple requests that take in account that the major instructions are already picked up through the regular instruction files in this repo.

## Contributing

Contributions are welcome. Focus on improvements that benefit the entire auditing community while keeping your proprietary techniques private.
