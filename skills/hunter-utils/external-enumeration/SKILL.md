---
name: external-enumeration
description: >
  Full passive external enumeration of a company's domain/subdomain infrastructure.
  Covers multi-source subdomain discovery, WHOIS/NS attribution, per-subdomain HTTP header harvest,
  technology stack mapping, dual-CDN detection, open CORS/security flags, stealth CF bypass,
  subsidiary research, and a structured markdown report.
  Use when asked to enumerate, recon, or map a company's external attack surface.
  Triggers: "enumerate domains", "subdomain recon", "map infrastructure", "osint on company",
  "what subdomains does X have", "attack surface", "external recon".
---

# External Enumeration Skill

You are performing **passive external reconnaissance** on a target company's domain infrastructure.
Goal: produce a comprehensive, structured map of all domains, subdomains, technology stack, and notable security observations - using only passive/OSINT techniques (no active exploitation).

---

## Phase 0 - Scope Clarification

Ask the user for:
1. **Primary domain(s)** to enumerate (e.g. `example.com`)
2. **Known subsidiaries or related companies** (acquisitions, brand names, sister domains)
3. **Output format** - markdown report to a file path?
4. **Depth** - quick pass (passive DNS only) or deep pass (stealth browser + port scan)?

---

## Phase 1 - Domain Ownership & Attribution

Before enumerating subdomains, confirm what domains are actually owned by the target.

### 1.1 WHOIS Check
```bash
whois <domain> | grep -iE 'registrar|creation|name server|registrant'
```
> Note: Most domains use **privacy protection** (e.g. GoDaddy DomainsbyProxy) - registrant names will be hidden. Do NOT rely on registrant names for attribution.

### 1.2 Nameserver Correlation (Primary Attribution Method)
```bash
for d in domain1.com domain2.io domain3.net; do
  echo -n "$d: "; dig NS $d +short | sort | tr '\n' ' '; echo
done
```
**Identical NS pairs = same DNS account = same owner.** This is the strongest passive attribution proof even when WHOIS is privacy-protected.

### 1.3 MX + TXT Record Cross-Reference
```bash
dig MX <domain> +short
dig TXT <domain> +short
```
- Shared `*.mail.protection.outlook.com` MX = same Microsoft 365 tenant
- TXT records reveal: Azure site verifications, Google Workspace, Atlassian, SendGrid
- Azure TXT format: `MS=ms...` or `azurewebsites.net` subdomain references → same Azure tenant

### 1.4 Similar-Name Domain Trap
> Note: **Always verify** similar-sounding domains (e.g. `target.net`, `target.co`) are actually owned by the target - different registrar or NS pair = likely unrelated squatter. Never assume.

---

## Phase 2 - Multi-Source Subdomain Enumeration

**Run all sources in parallel on first pass.** crt.sh alone is never sufficient.

### 2.1 Certificate Transparency (crt.sh)
```bash
curl -s "https://crt.sh/?q=%.example.com&output=json" \
  | python3 -c "import sys,json; [print(e['name_value']) for e in json.load(sys.stdin)]" \
  | tr ',' '\n' | sort -u | grep -v '^\*'
```

### 2.2 HackerTarget
```bash
curl -s "https://api.hackertarget.com/hostsearch/?q=example.com" | cut -d',' -f1 | sort -u
```

### 2.3 Wayback Machine
```bash
curl -s "https://web.archive.org/cdx/search/cdx?url=*.example.com&output=text&fl=original&collapse=urlkey" \
  | grep -oP '[\w.-]+\.example\.com' | sort -u
```

### 2.4 urlscan.io
```bash
curl -s "https://urlscan.io/api/v1/search/?q=domain:example.com&size=100" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(r['page']['domain']) for r in d.get('results',[])]" \
  | sort -u
```

### 2.5 RapidDNS
```bash
curl -s "https://rapiddns.io/subdomain/example.com?full=1" \
  | grep -oP '[\w.-]+\.example\.com' | sort -u
```

### 2.6 AlienVault OTX
> Note: **Use `curl` - NOT Python urllib** (SSL verify errors). Rate limiting is aggressive; skip if blocked.
```bash
curl -s "https://otx.alienvault.com/api/v1/indicators/domain/example.com/passive_dns" \
  | python3 -c "import sys,json; [print(r.get('hostname','')) for r in json.load(sys.stdin).get('passive_dns',[])]" \
  | sort -u
```

### 2.7 subfinder (if installed)
```bash
subfinder -d example.com -silent 2>/dev/null | sort -u
```
Install: `brew install subfinder`

### 2.8 Deduplicate Everything
```bash
cat all_sources.txt | sort -u > subdomains_unique.txt
wc -l subdomains_unique.txt
```

---

## Phase 3 - DNS Resolution & Live Check

```bash
# Resolve all subdomains, identify live ones
while read sub; do
  ip=$(dig +short A "$sub" 2>/dev/null | grep -m1 -oP '\d+\.\d+\.\d+\.\d+')
  if [ -n "$ip" ]; then
    echo "$sub -> $ip"
  fi
done < subdomains_unique.txt
```

Tag Cloudflare IPs: `173.245.x.x`, `103.21.x.x`, `103.22.x.x`, `103.31.x.x`, `104.16.x.x`, `104.17.x.x`, `104.18.x.x`, `104.19.x.x`, `104.20.x.x`, `104.21.x.x`, `108.162.x.x`, `162.158.x.x`, `172.64.x.x`, `172.65.x.x`, `172.66.x.x`, `172.67.x.x`, `188.114.x.x`, `190.93.x.x`, `197.234.x.x`, `198.41.x.x`

---

## Phase 4 - One-Pass Comprehensive Header Harvest

**Collect ALL headers in a single pass.** Do not come back for a second pass.

```bash
collect_headers() {
  local sub=$1
  local result=$(curl -sk -o /dev/null \
    --max-time 10 \
    -D - \
    -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
    "https://$sub" 2>/dev/null | head -80)

  local status=$(echo "$result" | head -1 | grep -oP '\d{3}')
  local ip=$(dig +short A "$sub" 2>/dev/null | grep -m1 -oP '\d+\.\d+\.\d+\.\d+')

  python3 -c "
import sys, json
headers_raw = '''$result'''
h = {}
for line in headers_raw.split('\n')[1:]:
    if ': ' in line:
        k, v = line.split(': ', 1)
        h[k.lower().strip()] = v.strip()
print(json.dumps({'subdomain': '$sub', 'status': '$status', 'ip': '$ip', **h}))
"
}
```

### Headers to capture (all of these, every time):
| Header | Why It Matters |
|---|---|
| `server` | Backend tech (cloudflare / gunicorn / nginx / apache) |
| `via` | **Dual CDN leak** - `via: 1.1 *.cloudfront.net` through Cloudflare = CloudFront backend |
| `x-amz-cf-pop` | AWS CloudFront PoP code → geographic location of CDN node |
| `x-amz-cf-id` | Confirms CloudFront, useful for timing correlation |
| `x-cache` | `HIT/MISS from cloudfront` confirms CF backend |
| `cf-cache-status` | Cloudflare caching layer behavior |
| `x-frame-options` | Security header (DENY / SAMEORIGIN / missing) |
| `x-xss-protection` | Legacy XSS header presence |
| `content-security-policy` | Reveals allowed origins, CDN domains, analytics, font CDNs |
| `access-control-allow-origin` | **Flag if `*`** - open CORS |
| `location` | Redirect target → reveals SaaS platform (HubSpot, Azure AD, LearnUpon, etc.) |
| `set-cookie` | Cookie flags (Secure/HttpOnly), platform fingerprinting |
| `x-runtime` | Ruby on Rails indicator |
| `x-request-id` | Application framework fingerprint |
| `alt-svc` | HTTP/3 / QUIC support |
| `content-type` | API vs HTML vs XML |

---

## Phase 5 - Technology Identification

### 5.1 From Server Headers
| `server` value | Technology |
|---|---|
| `cloudflare` | Cloudflare WAF/proxy |
| `gunicorn` | Python WSGI - **direct exposure, no WAF** |
| `nginx` | Nginx (may be direct or behind CDN) |
| `UploadServer` | Google Cloud Storage |
| `AmazonS3` | AWS S3 bucket |

### 5.2 From CNAME Chains
```bash
dig CNAME <subdomain> +short
```
| CNAME target | Platform |
|---|---|
| `*.hubspot.net` | HubSpot (email/link tracking) |
| `*.lmspowered.com` | LearnUpon LMS |
| `*.partner-experience.com` | Partner portal SaaS |
| `*.pendo.io` | Pendo product analytics |
| `*.salesforce.com` | Salesforce CRM |
| `*.zendesk.com` | Zendesk support |
| `*.freshdesk.com` | Freshdesk support |
| `*.atlassian.net` | Atlassian (Jira/Confluence) |
| `*.cloudfront.net` | AWS CloudFront (if direct CNAME, not leaked via) |
| `*.vercel.app` | Vercel hosting |
| `*.netlify.app` | Netlify hosting |
| `*.azurewebsites.net` | Azure App Service |

### 5.3 From Redirect Targets (`location` header)
- `launcher.myapps.microsoft.com` → Azure AD SSO (check URL for tenant ID)
- `*.okta.com` → Okta SSO
- `accounts.google.com` → Google Workspace SSO
- `*.auth0.com` → Auth0

### 5.4 Azure AD Tenant ID Extraction
If redirect leads to Microsoft login:
```
location: https://launcher.myapps.microsoft.com/api/signin/APP_ID?tenantId=TENANT_UUID
```
Extract `tenantId=` value - this is the organization's Azure AD tenant ID.

---

## Phase 6 - Dual CDN Detection

This is a **high-value finding** often missed on first pass.

**The pattern:** Cloudflare as outer WAF → AWS CloudFront as real CDN → origin
```
curl -sI https://app.example.com | grep -iE 'via|x-amz|x-cache|server'
```
**Indicators:**
- `server: cloudflare` AND `via: 1.1 xxxxxxxxx.cloudfront.net (CloudFront)` → dual CDN confirmed
- `x-amz-cf-pop: TLV55-P1` → CloudFront PoP in Tel Aviv
- `x-cache: Miss from cloudfront` → CloudFront active behind CF
- `x-amz-cf-id:` → unique CloudFront request ID

**Why it matters:** Reveals true backend CDN provider, geographic PoP locations, and hints at origin server region.

---

## Phase 7 - Cloudflare Bypass (Stealth Browser)

When Cloudflare blocks curl, use stealth Playwright.

> Note: **Critical package name:** Use `puppeteer-extra-plugin-stealth` - NOT `playwright-extra-plugin-stealth` (that package does NOT exist and will throw an error).

```bash
cd /tmp && mkdir cf-stealth && cd cf-stealth
npm init -y
npm install playwright playwright-extra puppeteer-extra-plugin-stealth
npx playwright install chromium
```

```javascript
const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
chromium.use(StealthPlugin());

const targets = [
  'https://app.example.com',
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  for (const url of targets) {
    const page = await browser.newPage();
    const headers = {};
    page.on('response', async resp => {
      if (resp.url() === url || resp.url().startsWith(url)) {
        Object.assign(headers, resp.headers());
      }
    });
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
      console.log(JSON.stringify({ url, headers }));
    } catch(e) {
      console.log(JSON.stringify({ url, error: e.message }));
    }
    await page.close();
  }
  await browser.close();
})();
```

---

## Phase 8 - Port Scan (Second Pass)

Only run on **non-Cloudflare** IPs (CF-fronted domains rarely expose alternate ports).

```bash
for host in direct-ip-1 direct-ip-2; do
  for port in 80 443 8080 8443 3000 4443; do
    result=$(curl -sk --max-time 5 -o /dev/null -w "%{http_code}" \
      "$([ $port = 443 ] || [ $port = 8443 ] && echo https || echo http)://$host:$port/")
    [ "$result" != "000" ] && echo "$host:$port -> HTTP $result"
  done
done
```

---

## Phase 9 - Subsidiary & Acquisition Research

Stealth startups acquired by the target may have **no public domain** - this is normal.

Search strategy:
1. `"[company name]" acquisition site:crunchbase.com`
2. `"[company name]" acquired site:techcrunch.com OR site:businesswire.com`
3. LinkedIn: search target company name → filter by "acquired by" or check leadership history
4. Check registrant/NS of likely related domains (founder names, product names)

> Note: A stealth startup may have: no domain, no Wayback archive, no CT certificates, no passive DNS entries - this is expected, not a gap in enumeration.

---

## Phase 10 - Notable Findings (Auto-Flag)

Always flag these automatically in the report:

| Pattern | Flag |
|---|---|
| `access-control-allow-origin: *` | Warning - **Open CORS** - unauthenticated cross-origin requests allowed |
| HTTP `525` status | Warning - **SSL Handshake Failure** - origin SSL misconfiguration behind Cloudflare |
| `server: gunicorn` or `server: unicorn` with no CDN | Warning - **Direct backend exposure** - no WAF, origin IP exposed |
| HTTP `301` → self (same host) | Info - Likely internal-only / auth-required (especially on `cslab*`, `vpn*`, `admin*`) |
| Azure AD `tenantId=` in redirect URL | Info - Azure AD Tenant ID leak - extract UUID |
| `x-amz-cf-pop` with city code | Info - CDN geographic PoP - reveals infrastructure region |
| `via: *.cloudfront.net` on a CF-served domain | Info - Dual CDN architecture |
| Subdomain → `*.mail.protection.outlook.com` CNAME | Info - Microsoft 365 tenant confirmation |

---

## Phase 11 - Report Structure

Always produce the markdown report with this structure:

```markdown
# [Company] Recon Report
**Date:** YYYY-MM-DD  
**Scope:** domain1.com · domain2.io · domain3.com

## Table of Contents
1. Confirmed Owned Domains
2. Technology Stack Summary
3. Notable Findings
4. [Primary Domain] - Subdomain Headers
   - Live - Cloudflare + CloudFront (Dual CDN)
   - Live - Cloudflare Only
   - Live - Third-Party / No CDN
   - Cloudflare DNS-Only / No HTTP Response
5. [Other domains]
6. Ownership & Attribution
7. Enumeration Sources

## 1. Confirmed Owned Domains
| Domain | Registrar | Created | Nameservers | Verdict |

## 2. Technology Stack Summary
| Layer | Technology | Evidence |

## 3. Notable Findings
| Finding | Detail |

## 4. Per-Subdomain Tables
### [subdomain]
| Header | Value |
(include: status, ip, server, via, x-amz-cf-pop, x-cache, x-frame-options, CSP, CORS, location, platform)

## 5. Ownership & Attribution
(people, entities, investors, Azure tenant, WHOIS proof)

## 6. Enumeration Sources
| Source | Results | Method |
**Total unique subdomains: N**  
**Vercel detected: yes / no**
```

---

## Common Pitfalls Reference

| Pitfall | Correct Approach |
|---|---|
| Using `playwright-extra-plugin-stealth` | Package does not exist. Use `puppeteer-extra-plugin-stealth` |
| Using Python urllib for OTX/VirusTotal | Use `curl` instead - Python SSL verify fails on these APIs |
| Assuming WHOIS registrant names identify owner | Use NS correlation + MX + TXT instead (privacy protection hides names) |
| Assuming `target.net` or `target.co` = same company | Verify NS + MX independently - often different owners |
| Running crt.sh only for subdomain discovery | Always run 6+ sources in parallel |
| Doing header harvest after initial recon | Collect ALL headers in the first live check pass |
| Port scanning CF-fronted IPs | Pointless - Cloudflare terminates connections. Only port-scan direct/non-CF IPs |
| Expecting acquired stealth startup to have a domain | Many acquisitions are stealth - zero DNS footprint is normal |
