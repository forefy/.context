# Manifest and data shapes

## The hash chain

Each step stores the SHA-256 of its captured frame, plus `prev_sha256`, the chain hash of the previous step (`0` * 64 for the first). The step's own `sha256` is the SHA-256 of its JSON body (every field except `sha256`), which includes `prev_sha256`. So any change to a frame, a field, or the order breaks that step's hash and every hash after it. `verify` recomputes the whole chain from the files on disk and the stored bodies, and exits non-zero if anything fails.

This is what makes the video trustworthy: a reader re-runs `verify` against the frames and the manifest, and either the chain holds or it does not.

## Manifest

```
{
  "story": "As a <role>, I <do X> so that <Y>.",
  "subject": "<host or target>",
  "capture_tool": "<how frames were captured>",
  "started_at": "<UTC ISO8601>",
  "steps": [
    {
      "n": 1,
      "title": "Login page",
      "action": "Open the app, redirected to /login",
      "url": "https://target/login",
      "captured_at": "<UTC ISO8601, frame mtime>",
      "frame": {"path": "frames/01.png", "sha256": "<64 hex>", "w": 1568, "h": 590},
      "focus": {"x": 545, "y": 262, "w": 260, "h": 82},
      "network": [{"method": "GET", "path": "/login", "status": 200}],
      "burp": [4550],
      "prev_sha256": "<64 hex or 0*64>",
      "sha256": "<64 hex, chain hash>"
    }
  ]
}
```

`focus`, `network` and `burp` are optional. `burp` records the Burp history ids a step came from, for traceability back to the proxy project.

## `--http` (one real request and response as a scene)

```
{
  "after_step": 2,
  "eyebrow": "WHAT ACTUALLY WENT OVER THE WIRE",
  "title": "Sign in = one POST /api/token",
  "lines": ["POST /api/token HTTP/2", "Host: target", "Cookie: [redacted [redacted]]", "", "email=user%40example.com&password=[redacted]", "", "<- HTTP/2 200 OK   (180 ms)"],
  "highlight": [0, 4, 6],
  "meta": "Burp proxy history, <time>. Secrets redacted; original request sha256 <16 hex>..."
}
```

Redact every secret before the request enters this file. `lines` is already-redacted text. `highlight` is the indexes of lines to emphasize.

## `--insight` (the required closer)

```
{
  "severity": "medium",
  "headline": "One sentence: what this flow really means.",
  "insight": "What the flow actually is, grounded in the captures.",
  "impact": "Who is affected and what is at stake.",
  "risk": "What to watch; the condition that would make it worse.",
  "verify": [
    "A concrete check a reader can run.",
    "Another concrete check."
  ],
  "impact_map": {
    "eyebrow": "BLAST RADIUS - WHAT ONE SESSION REACHES",
    "center": {"label": "Post-auth session", "sub": "one cookie"},
    "hub": {"label": "Service", "sub": "/api"},
    "nodes": [
      {"kind": "routine", "label": "Routines", "sub": "scheduled jobs"},
      {"kind": "connector", "label": "Connectors", "sub": "external tools"},
      {"kind": "session", "label": "Sessions", "sub": "prior runs"},
      {"kind": "project", "label": "Projects", "sub": "workspaces"},
      {"kind": "data", "label": "Tenant data", "sub": "records, scores"}
    ]
  }
}
```

`severity` colors the chip. `impact_map` draws a node graph from `center` through `hub` to up to five `nodes`; `kind` colors each edge and card (routine, connector, session, project, data). Keep every node grounded in an endpoint, object or UI element the captures actually show.

## CLI

```
evidence.py init    --manifest M --story S [--subject SUB] [--tool T]
evidence.py add     --manifest M --title T --action A [--url U] --frame F
                    [--focus JSON] [--network net.json] [--burp JSON]
evidence.py verify  --manifest M
evidence.py build   --manifest M --project DIR [--http http.json] [--insight insight.json]
```

`build` writes `index.html` plus one sub-composition per scene under `compositions/`, and copies each frame into the project's `assets/`. Render with HyperFrames from the project directory.
