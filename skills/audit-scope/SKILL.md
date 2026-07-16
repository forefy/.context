---
name: audit-scope
description: >
  Generate a security audit scope document from one or more GitHub repo URLs
  and/or API access descriptions. Outputs a 3-line protocol narrative (mission,
  user story, attacker story) followed by a scope table with NSLOC, focus
  areas, and days. Use when scoping a new audit engagement.
---

# Audit Scope Skill

## Inputs

User provides one or more of:
- GitHub repo URL(s)
- API documentation / access description (no repo)
- Named scope components (e.g. "also include the webhook service")

No report-days input needed - report writing is hardcoded (see Constants).

## Constants (hardcoded, never ask user)

- **Report writing**: always 1 day

Scope is measured in days. Do not attach monetary amounts to the output - days are the unit of measurement here.

## Step-by-step execution

### 1. Ingest repos

For each GitHub repo URL provided:
- Clone to `/tmp/<repo-name>-audit` via `gh repo clone`
- Run `cloc <repo> --quiet --not-match-f="(?i)(spec|test)" --not-match-d="(test|spec|__tests__|__mocks__)" --include-lang=TypeScript,JavaScript,Kotlin,Java,Go,Python,Rust,Solidity,HCL` (exclude test/spec files and dirs, case-insensitive; adjust `--include-lang` for the repo's stack)
- Record NSLOC per repo (source lines only - exclude test/spec files, Markdown, YAML, Gradle, shell)
- Never estimate NSLOC manually - always run cloc

For API-only scope (no repo):
- NSLOC = N/A
- Estimate days from endpoint count and complexity description

### 2. Explore repo structure

Read enough to understand:
- What the component does (SDK? API server? webhook handler?)
- Core tech: cryptographic primitives, auth mechanisms, external dependencies
- Language-specific security surface (JVM, Node, etc.)
- Key files: entry point, signing/crypto logic, error handling, config/env

### 3. Identify discounts

Apply these automatically - do not ask user:

| Condition | Discount |
|---|---|
| Multiple repos audited back-to-back (streak) | -0.5d lift-off discount |
| Multiple repos share same domain/features (similarity) | -20-35% off affected component's days |
| Spec/rules doc in scope alongside backend that implements it | -1-2d off backend (domain fluency pre-built) |

Lift-off discount = negative row in table (streak saves ramp time).
Similarity discount = **bidirectional** - applies whenever two components share significant overlapping attack surface, regardless of order. E.g. SDKs and backend sharing the same signing/API domain discount each other: SDKs get discounted because backend covers the server-side of the same flow; backend gets discounted because SDK work already mapped the signing trust boundary. Bake into the component day estimate directly (no separate row).

### 4. Estimate days per component

Base pace: ~300-400 NSLOC/day for deep manual security audit.
Adjust for:
- Cryptographic code: slower (~200 NSLOC/day)
- Boilerplate-heavy languages (Kotlin, Java): filter ~30% noise
- Framework-heavy TS backends (NestJS, etc.): DTOs, decorators, module definitions don't need line-by-line audit - pace ~400-500 NSLOC/day for those layers
- Narrow attack surface (signer-only, no HTTP): faster
- Wide attack surface (HTTP API, DB, auth): slower

**Do not pace all NSLOC uniformly. First split the repo into trust-boundary vs non-audited code, then only price the trust boundary at audit depth.** Raw cloc NSLOC != auditable NSLOC. This is the #1 source of overquoting - especially on web frontends, where most lines are presentational or read-only.

- **Excluded entirely (not in NSLOC, not priced):** presentational React/Vue UI, charts, visualizers, layout/page JSX, styles, assets. These have no trust boundary. On a frontend this is often 60-80% of cloc's count.
- **Skim only (~0.5d flat, not per-NSLOC):** read-only data-fetch and display logic - react-query hooks that fetch stats, `*Stats` mappers, APY/TVL math that only feeds charts, zustand stores, config/utils. Skim for leaked secrets, injection into outbound requests, and any value that feeds transaction sizing - then move on. Do NOT read line-by-line.
- **Full audit depth:** the actual trust boundary - transaction/instruction construction, signing & approval flow, output/slippage guards, auth, proxy/SSRF surface, input validation on server routes. This is usually a minority of the lines but where all the findings are.

**Contract/SDK out of scope -> frontend crypto pace is faster, not slower.** If the on-chain program or signing SDK lives in a separate repo (imported dependency, not vendored), the frontend only *orchestrates* pre-built instructions. Don't apply the ~200 NSLOC/day crypto pace to it - the frontend can only validate at the guard layer, so those passes are firm but quick. Flag the separate contract/SDK repo as its own potential line item (that's where fund-safety bugs actually live).

### 4b. Sanity-check against common scope sizes

Before finalizing days, compare against typical engagement sizes below. These are calibration anchors - if a NSLOC-derived estimate lands well outside the range for its type, re-check the tiering in step 4 (usually display/read-only code priced at audit depth).

| Engagement type | Typical days |
|---|---|
| Red team engagement | ~10-25 |
| Security tool development services | ~15-20 |
| Cloud misconfiguration review | ~8-12 |
| Secure code review | ~10 |
| Low-level secure code review | ~10 |
| Web app penetration test | ~5-8 |
| Android app pentest | ~5 |
| SDK secure code review | ~3-5 |
| Miniapp with lean backend | ~3-4 |
| Incident response | ~2-5 |
| 2-day custom training (build time) | ~20 |

Web/frontend protocol audits track the "web app pentest" row (5-8d), not "secure code review" (~10d), unless the frontend vendors its own contracts/signing code.

### 5. Build narrative (3 lines, before table)

**Line 1 - Protocol mission + why audit needed:**
`<Protocol name> is a <what it does>. <Scope components> are/is <role in system> - <why a flaw here = business impact>, making it <risk framing for the engagement>.`

Scope components must be woven into this line with clear business justification for auditing them.

**Line 2 - User story:**
`A <user type> <does X> - <SDK/component> <does Y> and <delivers Z to downstream system>.`

**Line 3 - Attacker story + incentives:**
`Attacker targets <attack surface> to <attack goal> - enabling <business-critical impact e.g. fund theft, unauthorized access, data breach>.`

### 6. Build scope table

Columns: `Component | NSLOC | Focus Areas | Days`

Row order:
1. One row per auditable component (repo or API surface)
2. Lift-off discount row (if streak): `Lift-off discount (streak) | - | - | -0.5`
3. Similarity discount already baked into component days (no separate row)
4. Report writing row: `Report writing | - | - | 1`
5. **Total** row: sum all days

Focus areas per component:
- Name the specific crypto primitives, key-handling patterns, auth mechanisms, serialization paths, and language-specific risks
- 4-6 items, comma-separated

### 7. Output

Print narrative (3 lines), blank line, then table. Nothing else.

## Example output shape

**Protocol:** Acme is a payments infrastructure API enabling businesses to move digital assets across chains. The SDKs (`sdk-lang1`, `sdk-lang2`) are the sole cryptographic trust boundary between a business's private keys and the Acme API - any signing flaw directly enables fund theft or unauthorized wallet creation, making them the highest-risk component in the integration stack.

**User story:** A fintech backend creates a wallet and signs a transaction step - the SDK constructs and stamps the activity payload locally, returning a signature the app posts to the Acme API.

**Attacker story & incentives:** Attacker targets the private key or signing flow to forge activity stamps - enabling unauthorized wallet creation or hijacking transactions to redirect funds to attacker-controlled addresses.

---

## Expected output table example:

| Component | NSLOC | Focus Areas | Days |
|---|---|---|---|
| sdk-lang1 audit | 943 | P-256 stamp construction, key isolation, body serialization, input validation, logger redaction | 1.5 |
| sdk-lang2 audit (similarity discount) | 1,764 | Signing parity with sdk-lang1, JVM key handling, coroutine error propagation, serialization safety | 2 |
| Lift-off discount (streak) | - | - | -0.5 |
| Report writing | - | - | 1 |
| **Total** | **2,707** | | **4** |

## Edge cases

- **Single repo, no streak**: no lift-off row, no similarity discount
- **3+ repos**: apply lift-off once (-0.5d), apply similarity discount to each repo after the first
- **API-only scope**: NSLOC = N/A, days from endpoint/complexity estimate, note estimation method
- **Mixed repo + API**: repo gets cloc, API gets endpoint-based estimate; both in same table
- **Web/frontend repo**: expect raw cloc to be dominated by presentational UI. Report NSLOC as the auditable surface (trust boundary + skim), not raw cloc, and say so. The trust boundary is: what the app builds & signs, output/slippage guards, wallet/session handling, and any server/proxy routes (SSRF, allowlists, rate-limit, secret exposure). A frontend audit is typically 4-6 days even at 20k+ raw NSLOC; if the estimate exceeds that, check whether display/read-only code got priced at audit depth.
