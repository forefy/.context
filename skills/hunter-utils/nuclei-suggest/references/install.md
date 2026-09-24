# Nuclei install reference

Nuclei distributes a single static binary and a git-cloned template library. There is no framework to vendor. Prefer a package manager; fall back to the API-resolve snippet. Never hardcode a version-stamped asset URL, it goes stale on the next release.

## Canonical sources

| What | URL |
|---|---|
| Binary releases | https://github.com/projectdiscovery/nuclei/releases |
| Source | https://github.com/projectdiscovery/nuclei |
| Templates | https://github.com/projectdiscovery/nuclei-templates |
| Docker image | docker pull projectdiscovery/nuclei |
| Docs | https://docs.projectdiscovery.io/tools/nuclei |

## Binary

Package managers resolve the version for you:

```bash
brew install nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

Release assets are version-stamped (e.g. `nuclei_3.4.10_linux_amd64.zip`), so resolve the latest from the API rather than guessing a filename:

```bash
OS=linux ARCH=amd64
URL=$(curl -s https://api.github.com/repos/projectdiscovery/nuclei/releases/latest \
  | grep -o "https://github.com/[^\"]*nuclei_[0-9.]*_${OS}_${ARCH}.zip")
curl -sL "$URL" -o nuclei.zip
curl -sL "$(dirname "$URL")/checksums.txt" -o checksums.txt
grep "$(basename "$URL")" checksums.txt | sha256sum -c -   # verify before unzip
unzip -o nuclei.zip nuclei
```

## Templates

```bash
git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates
nuclei -update-templates   # if the binary exists; clones to ~/.local/nuclei-templates
```

## What this skill requires

- Templates clone: required for browsing and selection (no target traffic).
- Binary: required only to execute the emitted command.

Both are offers, not steps. Print the command; let the operator run it.
