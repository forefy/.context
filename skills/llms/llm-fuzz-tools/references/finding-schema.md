# Normalized finding schema

One record per probe result, from any tool. The two mapped fields are what make aggregation worth
doing; everything else is provenance.

## Record

| Field | Notes |
|---|---|
| `tool`, `tool_version` | exact version, not "latest" |
| `run_id` | ties back to the run ledger |
| `target_provider`, `target_model`, `target_model_version` | a result without the model version cannot be compared to a later one |
| `probe_native_id` | the tool's own label, kept verbatim |
| `technique_family` | one of the five in `../../prompt-injection-audit/references/technique-matrix.md`, or `unmapped` |
| `objective` | one of the eight in the same file, or `unmapped` |
| `detector`, `detector_type` | `pattern` / `judge` / `human` |
| `outcome` | `hit` / `miss` / `error` |
| `confidence` | `confirmed` (two or more tools, or human-verified) / `single` / `disputed` |
| `evidence_ref` | path to the raw request and response - mandatory for every `hit` |
| `cost_tokens` | per probe where the tool reports it |
| `completion` | `complete` / `truncated` - set from the tool's exit status |

## Dedupe

Collapse on `(technique_family, objective, target_model_version)`.

- Same cell hit by several tools: **one** finding, `confidence: confirmed`, with each tool's record
  kept underneath as a confirmation.
- Same cell scored differently by different tools: **one** finding, `confidence: disputed`, resolved
  by reading the raw outputs. Never average two detectors, and never report the disagreement as two
  findings.
- `unmapped` records never collapse. They stay individual until the taxonomy grows to cover them.

## Why these two axes

They are the same axes the audit skill composes payloads from, so a normalized scanner run drops
straight into that skill's family triage: families a scanner already proved the model is soft
against do not need re-testing by hand, and the saved runs go to the agent layer, which no scanner
reaches.

An `unmapped` set that keeps growing is the useful failure mode. It means the tools are probing
something the taxonomy does not name yet, and that is worth reading rather than discarding.
