export const meta = {
  name: 'k8s-crit-hunt',
  description:
    'Hunt hackerone.com/kubernetes for one critical bug. Map the scope, fan out across attack-surface lanes, and gate every candidate behind an adversarial judge wave — a finding only counts if a skeptic cannot break its reproduction.',
  phases: [
    { title: 'Scope', detail: 'list in-scope components and rules' },
    { title: 'Hunt', detail: 'parallel lanes, each returns a reproducible PoC' },
    { title: 'Judge', detail: 'skeptics try to refute the reproduction' },
    { title: 'Coverage', detail: 'which surfaces were hunted vs. skipped' },
    { title: 'Report', detail: 'write up what survives' },
  ],
}

const SCOPE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['assets', 'rules'],
  properties: {
    assets: { type: 'array', items: { type: 'string' } },
    rules: { type: 'array', items: { type: 'string' } },
  },
}

const FINDINGS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['title', 'component', 'hypothesis', 'impact', 'repro'],
        properties: {
          title: { type: 'string' },
          component: { type: 'string' },
          hypothesis: { type: 'string' },
          preconditions: { type: 'string' },
          impact: { type: 'string' },
          repro: { type: 'string' },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['reproduced', 'reason'],
  properties: {
    reproduced: { type: 'boolean' },
    critical: { type: 'boolean' },
    reason: { type: 'string' },
  },
}

// One hunter per attack-surface lane. Together the lanes are the coverage map, so a lane that
// finds nothing still counts as "hunted, clean" rather than a silent gap.
const LANES = [
  { key: 'authn-authz', prompt: 'Authentication and authorization: API server authn plugins, RBAC evaluation, token and bootstrap handling, impersonation, privilege escalation.' },
  { key: 'admission', prompt: 'Admission control: built-in and webhook admission, bypasses, TOCTOU between admit and persist, policy-enforcement gaps.' },
  { key: 'apiserver', prompt: 'API server: request routing, the aggregation layer, field and patch handling, resource exhaustion, deserialization.' },
  { key: 'kubelet-cri', prompt: 'Kubelet and the CRI boundary: node authorization, pod and host isolation, volume and mount handling, container-escape-adjacent paths.' },
  { key: 'secrets-crypto', prompt: 'Secrets and credentials: encryption-at-rest, secret projection, serviceaccount token flows, accidental logging leaks.' },
  { key: 'supply-chain', prompt: 'Build and supply chain: release artifacts, image signing and verification, dependency handling, provenance gaps.' },
]

const GUARDRAILS = 'Stay in scope — read the hackerone.com/kubernetes policy first, and only reproduce on a cluster you own.'

phase('Scope')
const scope = await agent(
  `Read the hackerone.com/kubernetes policy and list the in-scope components and the rules of engagement. ${GUARDRAILS}`,
  { schema: SCOPE_SCHEMA, label: 'scope' },
)
log(`In scope: ${scope.assets.length} assets, ${scope.rules.length} rules`)

// Fan the lanes out and judge each candidate the moment its lane returns — a pipeline, so a
// slow lane never holds up judging of a fast one. The judge wave is the oracle here: a
// candidate is real only if a majority of skeptics fail to break its reproduction.
const covered = new Set()
const judged = await pipeline(
  LANES,
  (lane) =>
    agent(
      `Hunt for a critical vulnerability in the Kubernetes codebase, lane "${lane.key}": ${lane.prompt}\n` +
        `Rules: ${scope.rules.join('; ')}. ${GUARDRAILS}\n` +
        `Return only candidates you can actually reproduce — each with a hypothesis, the attacker's gain, and the exact steps that reproduce it from a clean cluster. Prefer nothing over a false positive.`,
      { schema: FINDINGS_SCHEMA, label: `hunt:${lane.key}`, phase: 'Hunt' },
    ),
  (result, lane) => {
    covered.add(lane.key)
    return parallel(
      (result.findings || []).map((f) => () =>
        parallel(
          ['walk-the-repro', 'reachability', 'preconditions'].map((lens) => () =>
            agent(
              `You are a skeptic. Try to break this Kubernetes finding through the "${lens}" lens: follow its repro steps from a clean cluster and find where they don't hold — a missing precondition, an unreachable path, an environment assumption.\n` +
                `Finding: ${JSON.stringify(f)}\n` +
                `Only report reproduced=true if the steps genuinely reproduce the impact. Default to false when unsure.`,
              { schema: VERDICT_SCHEMA, label: `judge:${lane.key}:${lens}`, phase: 'Judge' },
            ),
          ),
        ).then((verdicts) => {
          const ok = verdicts.filter(Boolean)
          const survives = ok.filter((v) => v.reproduced).length >= 2
          return { ...f, lane: lane.key, survives, verdicts: ok }
        }),
      ),
    )
  },
)

const candidates = judged.flat().filter(Boolean)
const survivors = candidates.filter((c) => c.survives)

phase('Coverage')
const skipped = LANES.filter((l) => !covered.has(l.key)).map((l) => l.key)
log(`Coverage: ${covered.size}/${LANES.length} lanes hunted${skipped.length ? ` — SKIPPED: ${skipped.join(', ')}` : ''}`)
log(`Candidates: ${candidates.length}, reproduced under judging: ${survivors.length}`)

phase('Report')
if (!survivors.length) {
  return { verdict: 'nothing reproduced under judging', coverage: { hunted: [...covered], skipped }, candidates: candidates.length }
}
const report = await agent(
  `Write submission-ready HackerOne reports for these findings — each one reproduced under adversarial judging. For each: title, affected component and versions, the exact repro from a clean cluster, what the attacker gains, and the fix. Match the disclosure policy.\n` +
    `Findings: ${JSON.stringify(survivors)}`,
  { label: 'report', phase: 'Report' },
)
return { verdict: `${survivors.length} finding(s) reproduced and written up`, coverage: { hunted: [...covered], skipped }, report }
