# HackerOne report writeup template

Fill each section. Keep it plain and first-person. State each fact once. The `# Title` line is for the Title field only — do not paste it into the Description body.

---

# <Vuln type> via <mechanism> (<feature/component>, <version or context>)

## Summary

What the affected feature is supposed to guarantee, in one or two sentences. Then the bug: what is trusted that shouldn't be, and what an attacker does with it, ending in the concrete win (what they read/write/become). If there's a cheaper or stronger variant, state it once here.

## <Product> Version

Where it was reproduced (exact version + distribution + how it was run) and whether it was also confirmed by source review (repo @ commit/date).

Affected: which versions/configurations/feature-gates. Note default-on vs opt-in and the maturity (Alpha/Beta/GA) of every relevant gate.

## Component Version

The vulnerable component + version, then a bullet per code location with a one-line role:

* `path/to/file.go` - what's wrong here (the missing check / the bad trust).
* `path/to/sink.go` - where the tainted value is consumed as a security decision.
* (list every sink — a complete sink census pre-empts the "is this the only place?" question.)

## Steps To Reproduce

"A self-contained PoC is attached; its `README.md` drives this step-by-step (verified end-to-end on <env>)."

1. **Environment** - the exact setup command(s).
2. **Scenario** - apply the scenario config (or equivalent): the victim asset + the attacker principal with ONLY the minimal grants (spell them out; note "no admin, no direct access").
3. **Baseline** - the action that is correctly denied with the honest identity.
4. **Exploit** - the forge/abuse command, with the exact payload inline.
5. **Confirm** - show the tainted/forged state (e.g. `whoami` output).
6. **Escalate** - the money shot: the previously-denied action now succeeds, in plaintext.
7. **Control** - a near-identical attempt that still fails, proving the exploited variable (not a broad grant) is the deciding factor.
8. **Scale** (if applicable) - how it generalizes (all nodes / all tenants / etc.).
9. **Teardown** - tear down the throwaway environment.

Optional variant: one short paragraph, only if it adds a distinct precondition/mitigation-defeat — not a restatement.

## Supporting Material/References

* **poc.zip** - one line on what running it proves; then a compact inline list of the key files and their roles (scenario, payload, runner, annotated source, plumbing-not-part-of-the-vuln).
* **poc.mov** - one line describing the recording's arc (baseline denial → exploit → success → control).

## Impact

Who the attacker is (realistic starting position), what they end up able to do, and why it breaks the security boundary the feature advertises. One tight paragraph. Don't re-derive the mechanism here.

## Suggested Fix

The concrete change(s) that close it, mapped to the code locations above. One or two sentences.
