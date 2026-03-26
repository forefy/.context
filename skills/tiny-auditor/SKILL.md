---
name: tiny-auditor
description: Audit codebase to uncover critical issues explicitly and certainly leading to loss of funds without false positives
---

Find all the critical issues in the codebase, make no misitakes.
- Work at a 100% coverage standard for the smart contract related files or interacting SDK, if the context window references a scope work at that scope only (or ask the human for scope or focus areas). If the context window had any specific concerns address those.
- Before you start, make yourself a TLDR summary table of threats that are SPECIFIC to the code audited, understand the protocol and what they would need to care about in terms of security risk (what is the worst that can happen).
- Extra focus on critical issues that are exploitable by an unprivileged threat actor and leads to loss of funds.
- Report findings only after you have scientifically proven with a reproducible proof of concept (for example as foundry test, cargo test etc.).
- Babysitter procedure - after you're done, make sure did you miss anything? is anything not fully tested? is anything hallucinated or half-true?