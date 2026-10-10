
// ---------------- Orchestration ----------------
phase('Corpus')
log(`Corpus: ${CORPORA.length} assemblers; Hypothesize: ${LENSES.length} lenses; Mine: ${CHUNKS.length} chunks (concurrency is capped by host CPUs, so stages queue)`)
const corpP = parallel(CORPORA.map(c => () => agent(`${COMMON} ${c.prompt} Return the structured object with name = "${c.key}".`, { label: `corpus:${c.key}`, phase: 'Corpus', schema: CORPUS_SCHEMA })))

phase('Hypothesize')
const lensP = parallel(LENSES.map(l => () => agent(lensPrompt(l), { label: `lens:${l.key}`, phase: 'Hypothesize', schema: HYP_SCHEMA })))

const corpora = (await corpP).filter(Boolean)
log(`Corpus done: ${corpora.length}/${CORPORA.length} assembled`)

phase('Engine')
const engineP = corpora.length ? agent(enginePrompt(corpora), { label: 'engine', phase: 'Engine', schema: ENGINE_SCHEMA }) : Promise.resolve(null)

phase('Mine')
const mineP = parallel(CHUNKS.map(nn => () => agent(minePrompt(nn), { label: `mine:chunk${nn}`, phase: 'Mine', schema: MINE_SCHEMA })))

const lenses = (await lensP).filter(Boolean)
log(`Hypothesize done: ${lenses.length}/${LENSES.length} lenses; hits so far: ${lenses.reduce((n, l) => n + (l.hits || []).length, 0)}`)
const mines = (await mineP).filter(Boolean)
log(`Mine done: ${mines.length}/${CHUNKS.length} chunks; candidates tested: ${mines.reduce((n, m) => n + (m.tested_count || 0), 0)}`)
const engine = await engineP
if (engine) log(`Engine done: ${engine.forms_total} forms, ${(engine.hits || []).length} hits; truncated: ${engine.truncated}`)

phase('Retest')
const retest = await agent(RETEST_PROMPT, { label: 'retest', phase: 'Retest', schema: RETEST_SCHEMA })

const allHits = []
for (const l of lenses) for (const h of (l.hits || [])) allHits.push({ source: `lens:${l.lens}`, hit: h })
for (const m of mines) for (const h of (m.hits || [])) allHits.push({ source: `mine:${m.chunk}`, hit: h })
if (engine) for (const h of (engine.hits || [])) allHits.push({ source: 'engine', hit: h })
if (retest) for (const h of (retest.hits || [])) allHits.push({ source: 'retest', hit: h })
const uniqueHits = [...new Map(allHits.map(h => [h.hit, h])).values()]
log(`Total distinct reported hits: ${uniqueHits.length}`)

phase('Verify')
const verified = await parallel(uniqueHits.map(h => () =>
  parallel([
    () => agent(reproducePrompt(h), { label: `verify:reproduce`, phase: 'Verify', schema: VERDICT_SCHEMA, effort: 'high' }),
    () => agent(refutePrompt(h), { label: `verify:refute`, phase: 'Verify', schema: VERDICT_SCHEMA, effort: 'high' }),
  ]).then(vs => {
    const v = vs.filter(Boolean)
    const survives = v.length === 2 && v.every(x => !x.refuted) && v.some(x => x.reproduced)
    return { ...h, verdicts: v, survives }
  })))
const confirmed = verified.filter(Boolean).filter(v => v.survives)
log(`Verify done: ${confirmed.length} hit(s) survived adversarial verification`)

phase('Critic')
const summaryObj = {
  corpora,
  lenses: lenses.map(l => ({ lens: l.lens, tested: l.tested_count, hits: l.hits, hypotheses: l.hypotheses, new_facts: l.new_facts, promising_untested: l.promising_untested })),
  mines: mines.map(m => ({ chunk: m.chunk, tested: m.tested_count, hits: m.hits, creator_statements: m.creator_statements, community_claims: m.community_claims, untested_ideas: m.untested_ideas })),
  engine, retest, verified, confirmed,
}
const summaryText = JSON.stringify(summaryObj).slice(0, 120000)
const critic = await agent(criticPrompt(summaryText), { label: 'critic', phase: 'Critic', schema: CRITIC_SCHEMA })

return { confirmed, distinct_hits: uniqueHits.length, lenses: lenses.length, mines: mines.length, corpora: corpora.length, engine, retest, critic }
