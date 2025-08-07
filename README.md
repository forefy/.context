# LLM Instructions for Smart Contract Auditing

<p align="center">
<a href="https://github.com/forefy/.context/edit/main/copilot-instructions.md"><img alt="Contribute" title="Contribute to copilot-instructions.md" src="https://img.shields.io/badge/Contribute-copilot--instructions.md-blue?logo=github"></a>
<img alt="GitHub last commit" title="GitHub last commit" src="https://img.shields.io/github/last-commit/forefy/.context">
<a href="https://twitter.com/forefy"><img alt="Forefy Twitter" title="Forefy Twitter" src="https://img.shields.io/twitter/follow/forefy.svg?logo=twitter"></a>

</p>

## What is this?

Smart Contract Auditors are using agentic AI to uncover potential leads, learn the codebase faster, and even generate PoC's for exploits from time to time.

This is just a side tool though, and the human is what counts. This repo aims to empower the human-to-agent interactions, by incorporating auditing methodologies and way-of-thinking, so that when these agents are used they are supercharged with community insight focusing on providing more qualitative results.


## Setup (Choose One)

### GitHub Copilot

```bash
git clone https://github.com/forefy/.context
cp .context/copilot-instructions.md your-project/.github/copilot-instructions.md
```

### Claude (Solidity)

```bash
git clone https://github.com/forefy/.context
cp .context/security-review-solidity.md your-project/.claude/commands/security-review.md
claude
> /security-review
```

### Claude (Anchor/Solana)

```bash
git clone https://github.com/forefy/.context
cp .context/security-review-anchor.md your-project/.claude/commands/security-review.md
claude
> /security-review
```


## Contributing

Contributions are welcome. Focus on improvements that benefit the entire auditing community while keeping your proprietary techniques private.