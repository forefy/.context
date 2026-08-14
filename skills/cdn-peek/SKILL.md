---
name: cdn-peek
description: Determine whether a CDN/WAF-fronted host is reachable outside its edge protection, and hunt for the real origin behind it. Works against any reverse-proxy edge (Cloudflare, CloudFront, Akamai, Fastly, Sucuri, Imperva/Incapsula, Azure Front Door, StackPath). Use for authorized security testing of a host you own or are engaged to assess - when asked to "find the origin", "bypass the CDN/WAF", "check if the origin leaks", "is this behind Cloudflare/CloudFront", or to map a domain's non-proxied attack surface. Produces a check/done ledger and, if found, a confirmed origin IP.

---

## Scope & authorization

Only run against hosts the user owns or is contractually engaged to test. This is origin discovery for defensive hardening (confirming the edge actually hides the origin), not for attacking third parties. If the target isn't clearly the user's or in-scope, ask before probing.

Keep scope tight to the requested host ("straight") unless the user asks to pivot to siblings. Sibling subdomains are enumerated for leaks, but don't treat a separate app on another IP as the target's origin without host-confusion proof.

## Step 0 - identify the edge

Resolve the host and match its IPs/NS/CNAME against known edge fingerprints, then load that provider's profile from the table below. Everything after is provider-agnostic; only the IP ranges, the client-IP header name, and the origin-allowlist source differ per provider.

| Edge | Fingerprint (IP/NS/CNAME) | Client-IP header | Origin allowlist source |
|---|---|---|---|
| Cloudflare | 104.16/13, 172.64/13, 2606:4700::/32, *.ns.cloudflare.com | CF-Connecting-IP | cloudflare.com/ips |
| CloudFront | *.cloudfront.net, AWS CLOUDFRONT ranges | CloudFront-Viewer-Address / X-Amz-Cf-Id | AWS CLOUDFRONT_ORIGIN_FACING prefix list |
| Akamai | *.akamaiedge.net, *.akamai.net, *.edgekey.net | True-Client-IP | Akamai SiteShield map |
| Fastly | *.fastly.net, 151.101/16 | Fastly-Client-IP | Fastly public-IP list / api.fastly.com/public-ip-list |
| Sucuri | *.sucuri.net, 192.88.134/23, 185.93.228/22 | X-Sucuri-ClientIP | Sucuri firewall IP list |
| Imperva/Incapsula | *.incapdns.net | Incap-Client-IP / X-Forwarded-For | Incapsula IP ranges |
| Azure Front Door | *.azurefd.net, AzureFrontDoor.Backend tag | X-Azure-ClientIP / X-Azure-SocketIP | AzureFrontDoor.Backend service tag |

## Methodology (run in order; each step is a check with a done/result state)

1. **Confirm fronted.** Resolve A/AAAA, match IPs against the edge ranges from Step 0, check NS/CNAME. If not fronted, stop - there's nothing to bypass.
2. **DNS record sweep.** `dig` A/AAAA/CNAME/TXT/MX/SOA/SRV/CAA. SPF `include`/`ip4`, MX, and autodiscover records frequently leak a non-fronted origin IP.
3. **Subdomain enum via CT.** Query Certificate Transparency (certspotter API, crt.sh) for `*.domain`. Flag any subdomain resolving to a non-edge IP.
4. **Fingerprint exposed siblings.** For each off-edge IP: ASN/hosting provider, server banner, cert CN/SAN. Reveals the hosting footprint (e.g. same cloud project) even when the box isn't the target's origin.
5. **Host-confusion vs exposed IPs.** `curl --resolve target:443:<IP>` with the target Host + SNI; compare title/body/length to the real fronted response. Same content = origin bypass; different (default vhost) = not the origin.
6. **CT search for the target's own origin cert.** A Let's Encrypt / self-issued cert scoped to just the target host (not the edge's shared cert) is a pivotable leak; 0 entries = clean.
7. **Favicon / HTML hash pivot.** mmh3 hash of `/favicon.ico` (Shodan `http.favicon.hash:`) or md5 (Censys `services.http.response.favicons.md5_hash`); also homepage body hash. Finds any box on the internet serving identical content off-edge. Needs a Shodan/Censys key.
8. **Passive / historical DNS.** SecurityTrails / Censys history for pre-edge A records on the host and the apex. Any historical non-edge IP is a prime origin candidate. Needs an API key.
9. **Client-IP header trust.** Send `X-Forwarded-For`, `X-Real-IP`, and the edge's own client-IP header (from Step 0) = `127.0.0.1`; compare responses. Bypasses IP allowlist/geo/rate-limit logic - not the origin. A hardened edge rejects a client-supplied copy of its own header (Cloudflare answers 403 `error code: 1000`); if the app instead trusts it, that is the finding.
10. **Edge header tricks.** `X-Forwarded-Host`, `X-Original-URL`, blank/mismatched `Host` - test for cache/redirect poisoning or routing bypass and header reflection in links.
11. **Confirm candidate origin.** For any candidate IP from 2/3/7/8: `curl -skI --resolve target:443:<IP>`. If it returns the target app and isn't firewalled to the edge ranges, it's a full bypass.
12. **Port-scan confirmed origin.** Non-HTTP services the edge never proxies (SSH/22, k8s API/6443, kubelet/10250, admin panels).

## Runnable snippets

```bash
# 1 confirm fronted
dig +short TARGET A; dig +short DOMAIN NS
# 2 DNS sweep
for t in A AAAA CNAME TXT MX SOA SRV CAA; do echo "$t: $(dig +short TARGET $t | tr '\n' ' ')"; done
# 3 CT subdomains
curl -s "https://api.certspotter.com/v1/issuances?domain=DOMAIN&include_subdomains=true&expand=dns_names" | python3 -c "import sys,json;[print(n) for x in json.load(sys.stdin) for n in x.get('dns_names',[])]" | sort -u
# 5 host-confusion
curl -sk --resolve TARGET:443:IP https://TARGET/ | python3 -c "import sys,re;h=sys.stdin.read();t=re.search(r'<title>(.*?)</title>',h,re.S);print('title:',t and t.group(1).strip(),'len:',len(h))"
# 6 origin cert history
curl -s "https://crt.sh/?q=TARGET&output=json" | python3 -c "import sys,json;d=json.load(sys.stdin);print('certs:',len(d))"
# 7 favicon hash
curl -sk https://TARGET/favicon.ico | python3 -c "import sys,mmh3,base64;d=sys.stdin.buffer.read();print(mmh3.hash(base64.encodebytes(d)) if d else 'none')"
# 8 historical DNS  (export SECURITYTRAILS_KEY first)
curl -s "https://api.securitytrails.com/v1/history/TARGET/dns/a" -H "APIKEY: $SECURITYTRAILS_KEY" | python3 -m json.tool
# 9 header trust  (swap EDGE_HEADER for the provider's own, from Step 0)
for h in "X-Forwarded-For: 127.0.0.1" "X-Real-IP: 127.0.0.1" "EDGE_HEADER: 127.0.0.1"; do echo "[$h] $(curl -sk -o /dev/null -w '%{http_code} %{size_download}b' -H "$h" https://TARGET/)"; done
# 11 confirm origin
curl -skI --resolve TARGET:443:CANDIDATE_IP https://TARGET/ | head
```

## Output

Finish with a `check / done? / result` ledger over all 12 steps, then a one-line verdict:
- **Clean** - every runnable technique exhausted and negative; origin not leaking via DNS/cert/header/edge.
- **Exposed** - a confirmed origin IP (name the step that found it and the confirming direct fetch), plus the fix (firewall origin to the edge ranges only, enable origin authentication such as Cloudflare Authenticated Origin Pulls or CloudFront custom-header validation, strip client-IP headers at the edge).

Report each step's true status - done or not-run - so coverage is honest; never present an unrun step as clean.
