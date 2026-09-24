# Browsing nuclei-templates efficiently

Two rules: filter by path before opening files, and prefer the indexes the repo already ships over walking ~10k YAML files.

## Directory map is the taxonomy

Path is signal before you open a file. Protocol is the top-level dir; under `http/` the subdir is the finding class.

| Path | Contents | Note |
|---|---|---|
| `http/cves/<year>/` | CVEs, foldered by year | year + freshness filtering |
| `http/vulnerabilities/` | non-CVE named bugs | overlaps CVEs, dedupe by `info.name` |
| `http/exposures/` | leaked configs, logs, backups, tokens | mostly single-GET, high replicable rate |
| `http/misconfiguration/` | insecure settings | benign, good default tier |
| `http/technologies/` | fingerprinting only | tier-0, no vuln claim |
| `http/exposed-panels/` | login interfaces | recon, pairs with default-logins |
| `http/default-logins/` | credential attempts | active-intrusive, gate it |
| `http/fuzzing/`, `dast/` | payload generation | never in a default run |
| `network/ ssl/ dns/` | non-HTTP protocols | different traffic profile |
| `file/` | matchers against local files | zero target traffic |
| `code/` | executes on scanner host | supply-chain risk, opt-in only |
| `headless/ javascript/` | browser / JS-protocol | heavier runtime deps |

## Use the shipped indexes first

Probe for these at repo root; fall back to a tree walk only if absent:

- `.nuclei-ignore` - canonical exclusion list. Read it, do not reinvent it.
- `cves.json` - CVE-to-template map, so a CVE query is a lookup.
- `TEMPLATES-STATS.json` - counts, for honest breadth reporting.
- `templates-checksum.txt` - detect which templates changed since last index.

## Fields that decide anything

```
info.severity                     # rank
info.tags                         # intent + intrusive families
info.metadata.product / vendor    # stack match, cleaner than tag guessing
info.metadata.max-request         # request count -> replicability
info.classification.cvss-score    # rank tiebreak
info.classification.epss-score    # real-world exploit likelihood, best first-run sort
requests[].payloads / attack      # combinatorics -> not replicable
unsafe: true                      # rawhttp -> not replicable, active
{{interactsh                      # OAST -> needs listener + permission
```

## Gotchas

- `workflows/` and `profiles/` reference templates by filter; not checks, skip them.
- `helpers/` is payloads and wordlists, skip.
- Dedupe `cves/` against `vulnerabilities/` on `info.name` + classification, not filename.
- `max-request > 1` means multi-request; do not assume one GET.
- Match both `.yaml` and `.yml`; do not follow tooling dirs or symlinks out of tree.

Order: path filter, confirm by `info.metadata`, tier by request contents, read an index instead of the tree whenever one exists.
