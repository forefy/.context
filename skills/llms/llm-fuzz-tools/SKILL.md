---
name: llm-fuzz-tools
description: Run several LLM fuzzing and red-team scanners against one target, normalize their output to a common schema, dedupe across them, and report honest coverage. Use when scanning a model endpoint with more than one tool.
compatibility: Each tool brings its own runtime (Go binary, Python venv, Node). Provider API keys and a spend cap are prerequisites, not details.
---

## Contents
- Scope, authorization & cost
- Phase 1 - pick two tools, not five
- Phase 2 - run them as background jobs
- Phase 3 - normalize
- Phase 4 - dedupe and triage
- False-positive gates
- Output
- Reference files: `references/tool-coverage.md`, `references/finding-schema.md`

## Scope, authorization & cost

Only scan an endpoint you own or are contractually engaged to test.

**Cost is a first-class constraint here, not a footnote.** Every other skill in this set spends your
time; this one spends the client's money. A single broad scanner is on the order of 200 probes, each
a paid completion, multiplied by every provider binding you point it at, multiplied by any mutation
layer. Two tools with overlapping corpora double the bill for a fraction of the coverage.

Before the first run:

- Get a **stated ceiling** in writing, in currency, not in probe count.
- Confirm whether the key you were given is **production or a test project**. Scanner traffic on a
  production key distorts the client's own usage metrics and can trip their abuse detection.
- Check the endpoint's **rate limits**. A run that dies at 40 percent looks like a clean result.
- Run one tool's smallest probe subset first, measure actual spend per probe, and extrapolate before
  committing to the full matrix.

Blast radius: this sends adversarial prompts to a metered third-party API and stores the responses.
Some responses will be harmful content by design. Treat the artifact store as sensitive.

## Phase 1 - pick two tools, not five

The instinct is to run everything and sum the results. That produces a bigger number, not better
coverage: the broad corpus scanners carry substantially the same public jailbreak and injection
sets, so the second one mostly re-finds the first one's hits at full price.

`references/tool-coverage.md` splits the field by what each tool uniquely does. The short version:

- **one** broad single-shot corpus scanner (they overlap heavily with each other; pick on runtime
  and provider bindings, not on probe count)
- **plus** a multi-turn attack framework, if adversarial conversation is in scope - single-shot
  corpora structurally cannot find what only emerges over several turns
- **plus** an eval harness, only if you own the application and want the result wired into CI

Two is the normal answer. Write down what you declined and why; that goes in the coverage ledger.

## Phase 2 - run them as background jobs

These are long-running CLIs, so the parallelism you want is process-level. Launch each tool as a
background job writing to its own artifact directory, then poll. Do not spawn one agent per tool:
an agent adds no value while a binary runs, and the reasoning work comes later, once.

Per tool, capture into `artifacts/<tool>/`: the raw report file, the exact invocation, the tool
version, start and end timestamps, and the exit status. A tool that exited non-zero has partial
results, and phase 3 must know that.

Confirm invocation against each tool's own `--help` at run time. Flags move between releases, and a
skill that pins them ages badly.

## Phase 3 - normalize

Map every tool's native output onto the single record in `references/finding-schema.md`. Two fields
carry the weight:

- **`technique_family`** - one of the five families in
  `../prompt-injection-audit/references/technique-matrix.md`
- **`objective`** - one of the eight objectives in the same file

Every tool names its probes differently. Mapping both axes onto one taxonomy is what makes the
results comparable, is the only reason aggregating beats reading each report separately, and lets a
scanner run feed the triage phase of `prompt-injection-audit` directly.

Where a probe does not map, record it as `unmapped` with the tool's own label. Do not force it, and
do not drop it - a growing `unmapped` set is how the taxonomy learns.

## Phase 4 - dedupe and triage

One reasoning pass over the pooled records.

**Dedupe key:** `(technique_family, objective, target_model_version)`. The same family firing in
three tools is one finding with three confirmations, not three findings. Keep the per-tool records
as evidence under the collapsed row.

**Disagreement is signal, not arithmetic.** Where two tools score the same cell differently, that is
one finding at reduced confidence, and the raw outputs decide it. Never average two detectors.

**Then rate.** A scanner verdict is a statement about the endpoint. It becomes a finding about the
product only after you check whether the application in front of it filters, refuses or never
exposes that path. Hand that question to `../prompt-injection-audit`.

## False-positive gates

- **Probe count is not coverage.** Two scanners at 200 probes each, overlapping 80 percent, is not
  400 tests. Report distinct `(family, objective)` cells reached, never the summed probe count.
- **Pattern detectors overfire.** String-matching detectors score refusals and quoted payloads as
  successes. Any pattern-scored hit needs the raw output attached before it survives triage.
- **Judge detectors are not oracles.** A judge verdict without the quoted span that justifies it is
  not evidence. Same rule as the audit skill's phase 4.
- **A truncated run is not a clean run.** Rate limits, spend caps and crashes all end a scan early
  and look identical to "found nothing". Record completion status per tool and per probe set.
- **Endpoint findings are not product findings.** A model that complies behind an application that
  never routes attacker text to it is a note, not a vulnerability.

## Output

- **Run ledger** - per tool: version, invocation, probe set, start and end, exit status, completion
  percentage, actual spend. Include the tools you declined in phase 1 and why.
- **Coverage** - distinct `(technique_family, objective)` cells reached, cells reached by only one
  tool, and cells no selected tool covers. The third list is the honest part and the reason to run
  this at all.
- **Findings** - deduped rows, each with its confirmations, disagreements, and evidence references.
- **Unmapped** - probes that did not fit the taxonomy, with their native labels.

A cell no tool covered must appear as uncovered. Summing probe counts across overlapping tools and
calling it coverage is the specific failure this skill exists to prevent.
