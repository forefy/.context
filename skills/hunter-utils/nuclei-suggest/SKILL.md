---
name: nuclei-suggest
description: Browse the nuclei-templates library, recommend a scoped template set for a given stack, target, or CVE, then run it against an authorized target and report findings.
compatibility: nuclei-templates, nuclei binary
---

See `./references/install.md` for first installation of nuclei on the environment
See `./references/browsing.md` for suggesting or using befitting templates to the hunt context

Index once into id, path, severity, tags, tier, replicable; rebuild only when the templates tree mtime changes. See `references/browsing.md` for traversal.

Confirm scope before any run: in-scope hosts, an explicit tier ceiling, and whether OAST callbacks are allowed. No confirmation, no execution; browsing and selection still work.

Tier by blast radius from template contents: `file/`, `dns/`, `ssl/` and single benign GETs are safe; `intrusive`, `brute`, `fuzz`, `unsafe: true` and `{{interactsh` are not; `code/` executes on your own host. Honor `.nuclei-ignore` and never exceed the confirmed ceiling.

Run the scoped set with `-duc` (disable the update check, which otherwise stalls scripted runs), `-jsonl -irr -store-resp -srd <dir>` for structured output plus captured request/response, `-etags` above the cap, `-rl` rate limiting, and a self-hosted OAST server if callbacks are permitted. On a target that returns a 200 catch-all (SPA app shell), prefer content/word matchers over status-only templates, which false-positive. Treat a skipped template as unrun, not clean.

Surface every finding, ranked by severity and EPSS, with: its `template-id`; a full clickable template link, `https://github.com/projectdiscovery/nuclei-templates/blob/<sha>/<template-path>` where `<sha>` is `git -C <clone> rev-parse HEAD`, commit-pinned so the link is the exact template that fired; the `matched-at` URL; and the captured evidence, http/dns from the JSONL `request`/`response` and ssl/network from the stored file under `-srd`. In the response, re-run the template's own matcher (`words`/`regex`/`dsl`) to locate the indicator and mark it: ANSI-highlight the matched span in a terminal, caret-underline it when piped no-color, and name the pattern that fired. Reproduce a single high-value finding with curl to confirm it before it goes in a report; if a template is not replicable, name it and do not approximate the check.

