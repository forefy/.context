# Video-ready PoC README pattern

The README is a script for a user-filmed demo: every block copy-pastes in order, and the reader can narrate over it. One command per step. Verify the exact blocks on a clean environment before shipping — copy-paste repros fail in ways your mental model won't (auth/credential precedence, working-directory resets between shells, CLI flags that don't override config files).

Structure:

```
# <Finding title> (PoC)

<2-3 sentence plain-language statement of the bug and the win, and what's affected/default-on.>

Everything below is copy-paste, one block at a time.

## Prerequisites
<one command that checks the tools are present>

## Step 0 - Set up a throwaway environment
<create the disposable target (docker/VM/local sandbox/etc.), fully self-contained>
<apply the scenario: victim asset + attacker principal with minimal grants>

## THE PROOF - N commands
<any one-time setup for acting AS the attacker identity, with a note on WHY
 it's needed (e.g. a token-only client, because --token doesn't override a
 cert-based config). Wrap repeated long invocations in a tiny helper fn.>

1. <baseline: the request that is DENIED with the honest identity>     # -> DENIED
2. <the forge/abuse step; show the tainted state>                      # -> forged X
3. <the same request, now SUCCEEDING via the exploit>                  # -> <secret/flag>

<one line: command 1 denied, command 3 succeeded, only <var> changed. Then how it scales.>

## Teardown
<delete the throwaway environment>

## Optional extras
- run-all.sh    - the above non-interactively, for a hands-off take
- <variant>.sh  - a distinct stronger/cheaper variant (kept optional)
- <source>      - annotated excerpt of the vulnerable lines
- <scenario>    - the attacker's exact minimal role/permission config
```

Principles:

- **The money shot is the before/after.** Command 1 (denied) and command 3 (succeeds) differ only by the exploited variable. That contrast is what the video sells.
- **Prefer transparent commands over an opaque script.** If shared shell state (a captured token, a URL) is the only reason for a script, put it in a small helper function in the README and keep each proof line short and readable.
- **Label plumbing.** Anything that's convenience, not vulnerability, says so — triagers must not mistake it for the bug.
- **Attach, don't inline secrets.** The user records `poc.mov`; the zip carries the runnable files. The report references both.
