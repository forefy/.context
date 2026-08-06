export const meta = {
  name: 'subenum-pipeline',
  description:
    'Enumerate every in-scope subdomain of a domain list. Baseline the whole list, then fan out across methodologies the agent chooses by its own judgement - each lane picks a distinct data source, and any lane that adds a new true subdomain spawns two more, until a round goes dry or the method cap is hit. DNS-resolve for liveness, fingerprint each live host with httpx and webanalyze, then aggregate both sources into one normalized JSON report keyed by coverage.',
  phases: [
    { title: 'Baseline', detail: 'broad first-pass enumeration, technique chosen by the agent' },
    { title: 'Expand', detail: 'each lane picks a distinct methodology by its own judgement; additive lanes spawn two more, loop until dry or the method cap' },
    { title: 'Resolve', detail: 'DNS-resolve every candidate for liveness, drop wildcard answers' },
    { title: 'Fingerprint', detail: 'httpx HTTP metadata then webanalyze technology stack per live host' },
    { title: 'Report', detail: 'reporter agent cross-joins httpx and webanalyze into one normalized JSON, coverage as top key' },
  ],
}

let cfg = args || {}
if (typeof cfg === 'string') {
  try {
    cfg = JSON.parse(cfg)
  } catch (e) {
    cfg = {}
  }
}
if (Array.isArray(cfg)) cfg = { domains: cfg }
const DOMAINS = cfg.domains || []
const OUTDIR = cfg.outDir || './recon'
const MAX_METHODS = cfg.maxMethods || 8
const WORDLIST = cfg.wordlist || ''

if (!DOMAINS.length) {
  return { error: 'no target domains - pass args.domains (array) or a bare array of domains, all within your authorized scope' }
}

const ENUM_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['methodology', 'subdomains'],
  properties: {
    methodology: { type: 'string' },
    subdomains: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
}

const RESOLVE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['liveCount'],
  properties: {
    liveCount: { type: 'integer' },
    wildcardDomains: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
}

const HTTPX_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['services'],
  properties: { services: { type: 'integer' }, note: { type: 'string' } },
}

const WEB_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['hosts'],
  properties: { hosts: { type: 'integer' }, note: { type: 'string' } },
}

const REPORT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['subdomains'],
  properties: {
    subdomains: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['subdomain'],
        properties: {
          subdomain: { type: 'string' },
          url: { type: 'string' },
          ip: { type: 'array', items: { type: 'string' } },
          status: { type: 'integer' },
          title: { type: 'string' },
          server: { type: 'string' },
          cdn: { type: 'string' },
          technologies: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              required: ['name'],
              properties: {
                name: { type: 'string' },
                version: { type: 'string' },
                categories: { type: 'array', items: { type: 'string' } },
                source: { type: 'string', enum: ['httpx', 'webanalyze', 'both'] },
              },
            },
          },
          notable: { type: 'boolean' },
          notes: { type: 'string' },
        },
      },
    },
  },
}

function huntPrompt(domains, outDir, opts) {
  const { laneId, avoid, baseline } = opts
  const avoidList = avoid && avoid.length ? avoid.join(', ') : 'none used yet'
  const wordlistHint = WORDLIST ? ` A wordlist is available at ${WORDLIST} if you choose DNS brute-forcing.` : ''
  const task = baseline
    ? 'Do a BROAD baseline pass: use the single most comprehensive passive aggregation approach you know (something that pulls from many sources at once) to surface as many subdomains as possible in one go.'
    : `Choose ONE subdomain-discovery methodology by your own judgement and run it. It MUST be a distinct data source from those already used this run: ${avoidList}. Pick whatever technique is most likely to surface subdomains those methods would miss - certificate transparency, passive DNS, web archives, search-engine or scraping sources, DNS brute-forcing, ASN and reverse-DNS sweeps, threat-intel feeds, or anything else you know. Do not repeat an already-used data source. If you genuinely cannot find a distinct unused methodology, return methodology "none" with an empty list.`
  return `You are a subdomain-discovery specialist. Target domains (authorized scope only):
${domains.map((d) => '- ' + d).join('\n')}

${task}

Use whatever is installed - subfinder, curl to public APIs, dig, jq, python3, and similar. Prefer passive OSINT; do nothing more intrusive than DNS resolution.${wordlistHint}

Then across all target domains:
1. Collect every hostname found.
2. Normalize each: lowercase; strip a leading "*."; strip any scheme, port, or path; remove a trailing dot.
3. Keep only hostnames equal to or ending in ".<target>" for one of the target domains; drop out-of-scope entries, emails, and bare wildcards.
4. Deduplicate.
5. Run mkdir -p ${outDir}/raw and write the final list to ${outDir}/raw/lane-${laneId}.txt, one host per line.

Return: methodology = a short name for the data source or technique you actually used, and subdomains = the deduplicated in-scope list. If a source rate-limits or errors, note it and return whatever you have.`
}

function resolvePrompt(domains, outDir) {
  return `You are the liveness validator. Resolution only - do not probe HTTP.

1. Merge every file in ${outDir}/raw/*.txt with sort -u into ${outDir}/all_subdomains.txt.
2. Wildcard check: for each target domain (${domains.join(', ')}), resolve a random non-existent label such as "zzz$RANDOM.<domain>" with dig +short. If it returns an address, that domain serves wildcard DNS - record the domain, and when resolving its subdomains treat answers matching the wildcard address as NOT live.
3. Resolve liveness in parallel:

    cat ${outDir}/all_subdomains.txt | xargs -P 25 -I{} sh -c 'dig +short {} A | grep -qE "^[0-9]" && echo {}' | sort -u > ${outDir}/live.txt

   Exclude wildcard-poisoned answers found in step 2.
4. Return liveCount (lines in live.txt) and wildcardDomains.`
}

function httpxPrompt(outDir) {
  return `You are the HTTP prober. Input: ${outDir}/live.txt (DNS-live hosts).

Run:

    httpx -l ${outDir}/live.txt -silent -sc -title -server -td -cdn -a -json -o ${outDir}/httpx.jsonl

Then build the URL list for the fingerprint stage:

    jq -r '.url' ${outDir}/httpx.jsonl | sort -u > ${outDir}/live_urls.txt

Return services = the number of live HTTP(S) endpoints (lines in httpx.jsonl). Do not run webanalyze.`
}

function webanalyzePrompt(outDir) {
  return `You are the technology fingerprinter. Input: ${outDir}/live_urls.txt (live HTTP URLs from httpx).

Ensure the fingerprint database exists, then fingerprint:

    webanalyze -update >/dev/null 2>&1 || true
    webanalyze -hosts ${outDir}/live_urls.txt -output json > ${outDir}/webanalyze.json 2>/dev/null

If your webanalyze build names the flags differently, adjust to read the same URL file and write JSON to the same path. Return hosts = the number of URLs fingerprinted.`
}

function reportPrompt(outDir, coverage) {
  return `You are the reporter. Aggregate the recon outputs into one normalized JSON report.

Inputs:
- ${outDir}/live.txt          DNS-live hosts
- ${outDir}/httpx.jsonl       per-host HTTP metadata (url, status_code, title, webserver, tech, cdn_name, a = resolved IPs)
- ${outDir}/webanalyze.json   per-host technology stack (name, version, categories)

For every host present in httpx.jsonl, build one normalized record by CROSS-CONSIDERING both sources:
1. Join httpx and webanalyze by host and URL.
2. Merge technologies from httpx tech-detect and webanalyze into a single deduplicated list. Match names case-insensitively; keep the most specific version; set source to "both" when the two sources agree on a technology, otherwise "httpx" or "webanalyze". Carry categories through when present.
3. Carry status, title, server (webserver), cdn (cdn_name), url, and ip (the "a" array) from httpx.
4. Set notable=true for the key subdomains - anything that stands out for an attacker: admin/login/api/staging/dev/internal hostnames, uncommon or outdated technology, an unusual server banner, or an exposed framework - and state why in notes. Ordinary hosts are notable=false with no notes.
5. Order the list notable-first, then alphabetically by subdomain.

Then write ${outDir}/report.json as exactly this shape, with coverage embedded verbatim as the high-order key:

    { "coverage": ${JSON.stringify(coverage)}, "subdomains": [ ...the records... ] }

Only use what the input files support - never invent a technology, version, or IP. Omit a field rather than guess. Return the subdomains array.`
}

const inScopeRe = /^[a-z0-9.-]+$/
function normalize(h) {
  return String(h)
    .trim()
    .toLowerCase()
    .replace(/^\*\./, '')
    .replace(/^https?:\/\//, '')
    .replace(/\/.*$/, '')
    .replace(/:\d+$/, '')
    .replace(/\.$/, '')
}
function inScope(h, domains) {
  if (!inScopeRe.test(h) || !h.includes('.')) return false
  return domains.some((d) => h === d || h.endsWith('.' + d))
}
function absorb(set, result, domains) {
  for (const raw of (result && result.subdomains) || []) {
    const h = normalize(raw)
    if (h && inScope(h, domains)) set.add(h)
  }
}

let laneCounter = 0
const used = new Set()

phase('Baseline')
const S = new Set()
const base = await agent(huntPrompt(DOMAINS, OUTDIR, { laneId: laneCounter, avoid: [], baseline: true }), { schema: ENUM_SCHEMA, label: 'enum:baseline', phase: 'Baseline' })
absorb(S, base, DOMAINS)
if (base && base.methodology) used.add(base.methodology)
log(`baseline [${(base && base.methodology) || 'n/a'}]: ${S.size} in-scope subdomains across ${DOMAINS.length} domain(s)`)

// Loop-until-dry expansion. No fixed method pool - each lane picks a distinct data source by its
// own judgement, avoiding the ones already used. Any lane that adds a new true subdomain earns two
// more lanes next round. A dry round ends it; the method cap bounds total agents against runaway.
phase('Expand')
let roundSize = 2
let roundNum = 0
let stopReason = 'dry-round'
while (true) {
  if (laneCounter >= MAX_METHODS) {
    stopReason = 'method-cap'
    break
  }
  roundNum++
  const take = Math.min(roundSize, MAX_METHODS - laneCounter)
  const avoid = [...used]
  const lanes = Array.from({ length: take }, () => ++laneCounter)
  const results = await parallel(
    lanes.map((id) => () =>
      agent(huntPrompt(DOMAINS, OUTDIR, { laneId: id, avoid, baseline: false }), { schema: ENUM_SCHEMA, label: `enum:lane-${id}`, phase: 'Expand' }).then((r) => ({ id, r })),
    ),
  )
  let additive = 0
  for (const res of results) {
    if (!res || !res.r) continue
    const name = res.r.methodology || `lane-${res.id}`
    used.add(name)
    const before = S.size
    absorb(S, res.r, DOMAINS)
    const added = S.size - before
    if (added > 0) additive++
    log(`round ${roundNum} [${name}] +${added} new (total ${S.size})`)
  }
  if (additive === 0) {
    stopReason = 'dry-round'
    break
  }
  roundSize = 2 * additive
}
log(`expansion done (${stopReason}): ${S.size} subdomains from ${used.size} methodologies - ${[...used].join(', ')}`)

phase('Resolve')
const resolved = await agent(resolvePrompt(DOMAINS, OUTDIR), { schema: RESOLVE_SCHEMA, label: 'validate:dns', phase: 'Resolve' })
const wildcards = resolved.wildcardDomains || []
log(`live: ${resolved.liveCount}/${S.size}${wildcards.length ? ` (wildcard DNS: ${wildcards.join(', ')})` : ''}`)

phase('Fingerprint')
const http = await agent(httpxPrompt(OUTDIR), { schema: HTTPX_SCHEMA, label: 'httpx', phase: 'Fingerprint' })
const web = await agent(webanalyzePrompt(OUTDIR), { schema: WEB_SCHEMA, label: 'webanalyze', phase: 'Fingerprint' })
log(`fingerprinted ${http.services} HTTP services, ${web.hosts} hosts profiled by webanalyze`)

const coverage = {
  domains: DOMAINS,
  subdomainsTotal: S.size,
  live: resolved.liveCount,
  httpServices: http.services,
  fingerprinted: web.hosts,
  wildcard: wildcards,
  methodologiesTried: [...used],
  rounds: roundNum,
  stopReason,
}

phase('Report')
const report = await agent(reportPrompt(OUTDIR, coverage), { schema: REPORT_SCHEMA, label: 'report', phase: 'Report' })
const subdomains = report.subdomains || []
log(`report: ${subdomains.length} normalized records, ${subdomains.filter((s) => s.notable).length} flagged notable`)

return {
  coverage,
  subdomains,
  artifacts: {
    all: `${OUTDIR}/all_subdomains.txt`,
    live: `${OUTDIR}/live.txt`,
    httpx: `${OUTDIR}/httpx.jsonl`,
    webanalyze: `${OUTDIR}/webanalyze.json`,
    report: `${OUTDIR}/report.json`,
  },
}
