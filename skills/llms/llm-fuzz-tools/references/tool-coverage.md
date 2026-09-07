# Tool coverage map

Pick on **what a tool uniquely reaches**, not on how many probes it advertises. The broad corpus
scanners draw from the same public jailbreak and injection sets, so a second one mostly re-finds the
first one's hits at full price.

Verify invocation from each tool's own `--help` at run time; flags move between releases and are
deliberately not pinned here.

## The four roles

| Role | What it is for | Unique reach | Redundant with |
|---|---|---|---|
| **Broad corpus scanner** | Single-shot probes across a large public corpus, scored by bundled detectors | Breadth per unit of effort; provider bindings | other broad scanners, heavily |
| **Mutation layer** | Re-encodes or paraphrases a probe to slip filters | Filter evasion - shows a defense is shallow rather than absent | nothing else |
| **Multi-turn framework** | Drives an adversarial conversation across turns, with converters and scorers | Anything that only emerges over several turns: gradual reframing, trust building, staged setup | nothing else |
| **Eval harness** | Asserts on your own app's prompts, config-driven, CI-friendly | Regression over time on a codebase you own | nothing else |

The first row is where the duplication lives. The other three are orthogonal to each other and to
it, which is why the default selection is one broad scanner plus at most one of the others.

## Named tools

| Tool | Role | Runtime | Notes |
|---|---|---|---|
| Augustus (Praetorian) | broad corpus scanner | single Go binary | Largest advertised corpus and provider list; no interpreter to set up, which matters on a locked-down host. Detectors include a published harm judge. |
| garak (NVIDIA) | broad corpus scanner + mutation layer | Python | Probe / detector / generator / buff split. The buff layer is the differentiator: it mutates a probe rather than only sending it. |
| PyRIT (Microsoft) | multi-turn framework | Python | A framework, not a scanner. You compose orchestrators, converters and scorers. Highest setup cost, and the only way to reach multi-turn attacks. |
| promptfoo | eval harness | Node | Config-driven assertions with a red-team module. Belongs in CI on an app you own, not in a one-off engagement scan. |
| Spikee | dataset | - | A corpus rather than a runner; useful as input to the others and cited by the audit skill's taxonomy. |

## Selecting

1. Take **one** broad corpus scanner. Choose on runtime and provider bindings, not probe count: a Go
   binary on a host where you cannot install Python is the whole decision some days.
2. Add the **multi-turn framework** only if multi-turn attacks are in scope and the budget survives
   it. Its setup cost is real and its findings are the ones nothing else reaches.
3. Add the **eval harness** only for an application you own and intend to re-test.
4. Add the **mutation layer** when the target already refused a plain corpus. Mutation answers a
   different question - is the defense shallow - and asking it before you have baseline refusals
   wastes the run.

Record the tools you declined and why. That list is part of the coverage report, because a reader
cannot otherwise tell an uncovered cell from an unattempted one.
