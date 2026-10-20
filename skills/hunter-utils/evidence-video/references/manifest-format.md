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

`focus`, `network` and `burp` are optional. `focus` is the one region to call out on this step's frame: `{x, y, w, h, label}` in frame pixels, drawn as a labelled box and given a zoom punch-in. `burp` records the Burp history ids a step came from, for traceability back to the proxy project.

## `--annotate` (on-image marks for a dense capture)

Pass a separate JSON file to `build --annotate <file>` to draw several labelled boxes on a step's frame, for pointing at the parts that matter on a crowded screen (a Burp request or response, a busy UI). Keyed by step number:

```
{
  "4": [
    {"x": 628, "y": 250, "w": 462, "h": 60, "label": "prompt that runs agents"},
    {"x": 628, "y": 358, "w": 462, "h": 72, "label": "scheduled routines"}
  ]
}
```

Each box is drawn on the frame with a numbered flag at its top-left. Coordinates are in frame pixels. Marks are a **presentation overlay, not part of the hashed chain**: the frame is the evidence, the marks only say where to look, so you can reposition or relabel them without breaking `verify` or re-capturing. Keep labels to a few words, and do not repeat a marked detail as text elsewhere in the scene; when a step has marks the generator already drops its side-panel prose so the image carries it.

## `--http` (one real request and response as a scene)

```
{
  "after_step": 1,
  "eyebrow": "WHAT ACTUALLY WENT OVER THE WIRE",
  "title": "Sign in = one POST /api/login",
  "lines": ["POST /api/login HTTP/2", "Host: target", "Cookie: [redacted]", "", "email=user%40example.com&password=[redacted]", "", "<- HTTP/2 200 OK   (180 ms)"],
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

## `divergence` (user story vs attacker story)

Add it to the `--insight` object (or at the manifest root) to replace the hash-chain scene with the fork between normal use and abuse.

```
"divergence": {
  "eyebrow": "USER STORY  vs  ATTACKER STORY",
  "intended": {
    "label": "INTENDED USE",
    "sub": "what the feature is for",
    "steps": ["Sign in", "Open the feature", "Act on your own data"]
  },
  "attacker": {
    "label": "ATTACKER'S PATH",
    "sub": "where it gets diverted",
    "divert_at": 0,
    "steps": ["Obtain a session illegitimately", "Open the feature", "Act on the victim's data"]
  },
  "footer": "Same feature. The fork is one step; everything after it is identical."
}
```

`intended` is the normal flow, `attacker` is the diverted flow. Line the two `steps` lists up position for position so the fork reads across. `divert_at` is the 0-based index in `attacker.steps` of the step where normal use becomes abuse; that row is highlighted. Keep both paths grounded in the captured flow. When `divergence` is absent, this beat is omitted; the tool never renders hashes on the video. The hash chain is a manifest-and-`verify` mechanism only.

## CLI

```
evidence.py init    --manifest M --story S [--subject SUB] [--tool T]
evidence.py add     --manifest M --title T --action A [--url U] --frame F
                    [--focus JSON] [--network net.json] [--burp JSON]
evidence.py verify  --manifest M
evidence.py build   --manifest M --project DIR [--http http.json] [--insight insight.json]
```

`build` writes `index.html` plus one sub-composition per scene under `compositions/`, and copies each frame into the project's `assets/`. Render with HyperFrames from the project directory.
