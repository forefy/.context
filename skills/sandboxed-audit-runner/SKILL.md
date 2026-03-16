---
name: sandboxed-audit-runner
description: "Wrap the current audit agent session inside the Anthropic Sandbox Runtime (srt) before starting any security audit. Use this before invoking smart-contract-audit, infrastructure-audit, or any other audit skill on an untrusted codebase. Triggers include: start a sandboxed audit, run audit in sandbox, sandbox before auditing, protect my session during audit."
---

# Sandboxed Audit Runner

Before running any audit on untrusted code, this skill configures and launches `srt` to wrap the entire agent session. The goal is to protect the host from prompt injection attacks embedded in the codebase under review - malicious comments, filenames, or configs designed to make the auditing agent exfiltrate SSH keys, tokens, or make unauthorized network calls.

**SKILL DIRECTORY DETECTION:**
```bash
SKILL_DIR=$([ -d "$HOME/.context/skills/sandboxed-audit-runner" ] && echo "$HOME/.context/skills/sandboxed-audit-runner" || echo ".context/skills/sandboxed-audit-runner")
```

## Prerequisites

```bash
npm install -g @anthropic-ai/sandbox-runtime
srt --version
```

On Linux, also install bubblewrap: `apt install bubblewrap`.

## Setup

### 1. Create the audit session config

Read `$SKILL_DIR/references/smart-contract.srt.md`, extract the JSON block, and write it to `.srt-audit.json` in the project root. Remove any `allowedDomains` entries the audit does not need.

### 2. Start the sandboxed session

```bash
srt --settings .srt-audit.json bash
```

All commands run inside that shell - including any invoked audit skill - are now sandboxed at the OS level. On macOS this uses `sandbox-exec`; on Linux it uses `bubblewrap`.

### 3. Invoke the audit skill normally

With the sandbox active, invoke the audit skill as usual:

```
run smart-contract-audit
```

The entire agent conversation and all tool calls it makes will execute under the srt restrictions for the duration of the session.

### 4. Verify the sandbox is active (optional)

```bash
cat ~/.ssh/id_rsa      # should be blocked
curl https://example.com  # should be blocked if not in allowedDomains
```

### 5. Clean up

```bash
exit
rm .srt-audit.json
```

## Why this matters

Audited code can contain:
- Comments or string literals with prompt injection payloads targeting the AI
- `package.json` postinstall scripts that probe `~/.aws` or `~/.ssh`
- Test fixtures or build scripts with embedded exfiltration logic
- Configs that instruct tooling to phone home

Wrapping the session in `srt` means these attempts are blocked at the OS level before any tool executes them, regardless of whether the AI detected the injection.
