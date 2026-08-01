export const meta = {
  name: 'dynamic-audit',
  description:
    'A self-shaping audit that keeps tiny-auditor\'s judgment, not just its shape. It discovers the surfaces worth hunting for this target, aims them at the crown-jewel assets, and grows the surface on every confirmed hit. Candidates must survive skeptics who name-check a realistic actor and strip privileged-breach redundancy; survivors are proven, deduped, ranked with attackonomics demotions, then written up under do-no-harm rules and gated by a report-QA pass. Prefer nothing over a false positive.',
  phases: [
    { title: 'Discover', detail: 'derive crown jewels, known/acknowledged issues, and initial lanes' },
    { title: 'Hunt', detail: 'parallel lanes off the queue' },
    { title: 'Refute', detail: 'skeptics kill anything without a real actor or that assumes a devastating breach' },
    { title: 'Prove', detail: 'a working PoC or clear reachability evidence, code left untouched' },
    { title: 'Merge', detail: 'fold sibling near-duplicates into one finding' },
    { title: 'Rank', detail: 'risk x probability with attackonomics demotions, comparative' },
    { title: 'Report', detail: 'actor-named, do-no-harm writeups' },
    { title: 'QA', detail: 'skeptic checks each writeup, one rewrite on failure' },
  ],
}

const LANE = {
  type: 'object',
  additionalProperties: false,
  required: ['key', 'focus', 'ev'],
  properties: { key: { type: 'string' }, focus: { type: 'string' }, ev: { type: 'number' } },
}

const FRAME_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['crown_jewels', 'known', 'acknowledged', 'lanes'],
  properties: {
    crown_jewels: { type: 'array', items: { type: 'string' } },
    known: { type: 'array', items: { type: 'string' } },
    acknowledged: { type: 'array', items: { type: 'string' } },
    lanes: { type: 'array', items: LANE },
  },
}

const SURFACE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['lanes'],
  properties: { lanes: { type: 'array', items: LANE } },
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
        required: ['claim', 'where', 'reach', 'gain'],
        properties: {
          claim: { type: 'string' },
          where: { type: 'array', items: { type: 'string' } },
          reach: { type: 'string' },
          gain: { type: 'string' },
        },
      },
    },
  },
}

const VOTE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['holds', 'reason'],
  properties: { holds: { type: 'boolean' }, reason: { type: 'string' } },
}

const PROOF_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['proven', 'detail'],
  properties: { proven: { type: 'boolean' }, detail: { type: 'string' } },
}

const MERGED_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['id', 'claim', 'merged_from'],
        properties: {
          id: { type: 'string' },
          claim: { type: 'string' },
          merged_from: { type: 'array', items: { type: 'number' } },
        },
      },
    },
  },
}

const RANK_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['ranked'],
  properties: {
    ranked: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['id', 'title', 'severity', 'likelihood', 'rationale'],
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
          likelihood: { type: 'string', enum: ['high', 'medium', 'low'] },
          rationale: { type: 'string' },
        },
      },
    },
  },
}

const WRITEUP_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['id', 'writeup'],
  properties: { id: { type: 'string' }, writeup: { type: 'string' } },
}

const QA_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['ok', 'issues'],
  properties: { ok: { type: 'boolean' }, issues: { type: 'array', items: { type: 'string' } } },
}

const RULES = 'Authorized scope only. Surface only new issues; never re-report known ones. Prefer nothing over a false positive.'
const FLOOR = 60000
const BATCH = 4
const QUIET_CAP = 2

phase('Discover')
const frame = await agent(
  `Inspect the target. Name the crown-jewel assets an attacker would go after, the already-known issues to skip (prior audits), the team-acknowledged issues (aware and accepted), and propose the audit lanes worth hunting HERE - each a key, a focus, and ev (1-5). Favor where bugs hide: broken invariants, doc-vs-code drift, a guard on one path missing on a sibling, and code from authors whose history most needed security fixes. ${RULES}`,
  { schema: FRAME_SCHEMA, label: 'discover' },
)
log(`Crown jewels: ${frame.crown_jewels.join(', ')}; ${frame.lanes.length} lanes; ${frame.known.length} known, ${frame.acknowledged.length} acknowledged`)

const known = new Set(frame.known.map((k) => k.toLowerCase()))
const priorList = [...frame.known, ...frame.acknowledged].join('; ') || 'none'
const seen = new Set(frame.lanes.map((l) => l.key))
const hunted = new Set()
let queue = [...frame.lanes].sort((a, b) => b.ev - a.ev)
const confirmed = []
let quiet = 0
let round = 0

const LENSES = [
  ['reachability', 'Follow the path from an unprivileged start - where does it fail to reach the stated gain?'],
  ['preconditions', 'What unstated precondition does it need that a real attacker would not have?'],
  ['realistic-actor', 'Name the realistic actor - external attacker, fat-fingering operator, lazy dev, curious user. If you cannot name one, holds=false: this is hardening, not an attack.'],
  ['privileged-redundancy', 'Does it assume an already-privileged breach? If that breach would itself be devastating, the workaround is redundant - holds=false.'],
  ['known-drift', `Is this within ~20% of an already-known or acknowledged issue (${priorList})? If the team is effectively already aware, holds=false.`],
  ['impact-honesty', 'Is the stated impact the mature, certain exploitation - not a worst case asserted as guaranteed? holds=false if inflated.'],
]

const huntAndGate = [
  (lane) =>
    agent(
      `Hunt lane "${lane.key}": ${lane.focus}\nAim at the crown jewels: ${frame.crown_jewels.join('; ')}.\n` +
        `Each finding: the claim, where (file:line), how an unprivileged attacker reaches it, what they gain. ${RULES}`,
      { schema: FINDINGS_SCHEMA, label: `hunt:${lane.key}`, phase: 'Hunt' },
    ),
  (result, lane) => {
    hunted.add(lane.key)
    const fresh = (result.findings || []).filter((f) => !known.has(f.claim.toLowerCase()))
    return parallel(
      fresh.map((f) => () =>
        parallel(
          LENSES.map(([lens, q]) => () =>
            agent(
              `Skeptic, "${lens}" angle. ${q}\nFinding: ${JSON.stringify(f)}\nholds=true only if it genuinely survives your attack. Default false when unsure.`,
              { schema: VOTE_SCHEMA, label: `refute:${lane.key}:${lens}`, phase: 'Refute' },
            ),
          ),
        ).then((votes) => {
          const ok = votes.filter(Boolean)
          return { f, survives: ok.length === LENSES.length && ok.every((v) => v.holds) }
        }),
      ),
    ).then((checked) =>
      parallel(
        checked
          .filter((c) => c.survives)
          .map((c) => () =>
            agent(
              `Prove this under realistic attacker conditions - a PoC that runs, no synthetic setup. Do NOT modify the audited code; any PoC or test file you create must open with a comment marking it a temporary audit-phase artifact. If a prerequisite is realistically attacker-obtainable but you lack it, proven=false and point at the evidence in detail.\nFinding: ${JSON.stringify(c.f)}`,
              { schema: PROOF_SCHEMA, isolation: 'worktree', label: `prove:${lane.key}`, phase: 'Prove' },
            ).then((proof) => (proof && proof.detail ? { ...c.f, lane: lane.key, proof } : null)),
          ),
      ),
    )
  },
]

while (queue.length && quiet < QUIET_CAP && (budget.total ? budget.remaining() > FLOOR : round < 6)) {
  round++
  const batch = queue.splice(0, BATCH)
  log(`round ${round}: ${batch.map((l) => l.key).join(', ')} (${queue.length} queued, ${confirmed.length} confirmed)`)
  const hits = (await pipeline(batch, ...huntAndGate)).flat().filter(Boolean)

  if (!hits.length) {
    quiet++
    continue
  }
  quiet = 0
  confirmed.push(...hits)

  const branches = (
    await parallel(
      hits.map((h) => () =>
        agent(
          `This finding is confirmed. Propose adjacent audit lanes likely to share it - sibling paths, the same author's other code, the same anti-pattern elsewhere. Each a key, focus, ev.\nFinding: ${JSON.stringify(h)}`,
          { schema: SURFACE_SCHEMA, label: `branch:${h.lane}`, phase: 'Discover' },
        ),
      ),
    )
  )
    .filter(Boolean)
    .flatMap((r) => r.lanes)

  let added = 0
  for (const n of branches) {
    if (!seen.has(n.key)) {
      seen.add(n.key)
      queue.push(n)
      added++
    }
  }
  queue.sort((a, b) => b.ev - a.ev)
  if (added) log(`  branched into ${added} new lane(s) from ${hits.length} hit(s)`)
}

const stopReason = !queue.length ? 'surface dry' : quiet >= QUIET_CAP ? 'went quiet' : 'budget/round cap'
log(`Stopped (${stopReason}): ${hunted.size} lanes over ${round} rounds, ${confirmed.length} raw confirmed`)

if (!confirmed.length) {
  return { verdict: 'nothing survived refutation with a proof', stopReason, lanes_hunted: [...hunted], acknowledged: frame.acknowledged }
}

phase('Merge')
const merged = await agent(
  `These findings came from a branching hunt, so some are the same core issue reported on sibling paths, or a "moreover" sub-point of another. Fold near-duplicates into one canonical finding; keep genuinely distinct ones separate. Reference the input findings by their index in merged_from.\nFindings: ${JSON.stringify(confirmed.map((c, i) => ({ i, claim: c.claim, where: c.where, gain: c.gain })))}`,
  { schema: MERGED_SCHEMA, label: 'merge', phase: 'Merge' },
)
const canon = merged.findings.map((m) => ({
  ...m,
  evidence: m.merged_from.map((i) => confirmed[i]).filter(Boolean),
}))
log(`Merged ${confirmed.length} -> ${canon.length} distinct`)

phase('Rank')
const ranked = await agent(
  `Rank these together, severity = risk x probability, comparative (a critical must outrank a low), numbered within band by descending priority. Apply these probability rules strictly:\n` +
    `- a privileged prerequisite (e.g. admin) forces probability Low, UNLESS the bug arises from a privileged actor's normal routine\n` +
    `- no real attacker incentive forces probability Low\n` +
    `- uncertain or unprovable probability defaults to Low\n` +
    `Bump severity where a business-critical asset is directly hit or an easy, ricochet-free fix exists. Do not expose raw risk numbers - only severity and likelihood.\n` +
    `Findings: ${JSON.stringify(canon.map((c, i) => ({ id: c.id, i, claim: c.claim, evidence: c.evidence })))}`,
  { schema: RANK_SCHEMA, label: 'rank', phase: 'Rank' },
)

phase('Report')
const byId = Object.fromEntries(canon.map((c) => [c.id, c]))
const reports = await pipeline(
  ranked.ranked,
  (r) =>
    agent(
      `Write this finding up for the engineering team. Rules:\n` +
        `- Impact names the realistic actor and the loss in plain terms, honest about reachability.\n` +
        `- Follow "X is a feature that does X. During the audit it was found that X. Although <the mitigating factor or the team's likely counter-argument>, an attacker who does X might...". The "although" clause is required - state what reduces the risk.\n` +
        `- Speak at ~80% certainty: describe the vulnerable condition and the surface it opens, do not assert the worst case as guaranteed. If there is no clean PoC, end with a short realism note.\n` +
        `- Attack Flow: a breadcrumb from prerequisites to exploitation (or "operator/dev makes mistake Y" if it is not attacker-driven).\n` +
        `- Locations: exact file:line, evidence token first.\n` +
        `- Remediations: 2-3, priority-sorted, battle-tested, introducing no new risk or complexity; mark any complementary one as such.\n` +
        `- Description + Impact under ~12 lines. No fluff, no semicolons, regular dashes.\n` +
        `Ranked: ${JSON.stringify(r)}\nEvidence: ${JSON.stringify(byId[r.id])}`,
      { schema: WRITEUP_SCHEMA, label: `write:${r.id}`, phase: 'Report' },
    ),
  (draft, r) =>
    agent(
      `Skeptic pass on this writeup. Fail (ok=false) if: impact names no realistic actor, the "although" mitigating clause is missing, it overclaims beyond the evidence, the attack flow is not a concrete reachable trace, locations are not exact, or remediations add new risk. List concrete issues.\nRanked: ${JSON.stringify(r)}\nWriteup: ${draft.writeup}`,
      { schema: QA_SCHEMA, label: `qa:${r.id}`, phase: 'QA' },
    ).then((qa) =>
      qa.ok
        ? draft
        : agent(
            `Rewrite the writeup once, fixing exactly these issues and nothing else: ${qa.issues.join('; ')}\nOriginal: ${draft.writeup}\nRanked: ${JSON.stringify(r)}\nEvidence: ${JSON.stringify(byId[r.id])}`,
            { schema: WRITEUP_SCHEMA, label: `rewrite:${r.id}`, phase: 'QA' },
          ),
    ),
)

return {
  verdict: `${ranked.ranked.length} survived, deduped, and written up`,
  stopReason,
  lanes_hunted: [...hunted],
  acknowledged: frame.acknowledged,
  findings: ranked.ranked.map((r) => ({ ...r, writeup: (reports.find((w) => w && w.id === r.id) || {}).writeup })),
}
