export const meta = {
  name: 'gsmg-solve-campaign',
  description: 'GSMG puzzle: mine 7-year chat for untested candidates, lens-based hypothesis panel, local-corpus dictionary campaign, adversarial verification of any hit',
  phases: [
    { title: 'Corpus', detail: 'assemble local and public-domain text corpora' },
    { title: 'Hypothesize', detail: 'lens panel proposes and tests concrete candidates' },
    { title: 'Engine', detail: 'bulk dictionary campaign over the assembled corpora' },
    { title: 'Mine', detail: 'one agent per transcript chunk: extract and test candidates' },
    { title: 'Retest', detail: 'consolidated independent retest of every candidate file' },
    { title: 'Verify', detail: 'adversarial verification of any reported hit' },
    { title: 'Critic', detail: 'completeness critic and next steps' },
  ],
}

const BRIEF = '/home/vin/bitcoin_puzzle/scratch/wf/BRIEF.md'
const WF = '/home/vin/bitcoin_puzzle/scratch/wf'
const SCR = '/home/vin/bitcoin_puzzle/scratch'
const COMMON = `First read ${BRIEF} completely and obey its hard rules. Work from ${SCR} when running tools. ` +
  `Every candidate string you test MUST also be appended to a file under ${WF}/ named as instructed so it can be retested independently. ` +
  `Never print private keys or full decrypted plaintexts; report hits as described in the brief. ` +
  `Do not bulk-download copyrighted transcripts, scripts or lyrics; rely on your own knowledge and short quotations only. ` +
  `Your final output is consumed by a script: return the structured object only.`

const HITS = { type: 'array', items: { type: 'string' } }
const MINE_SCHEMA = { type: 'object', properties: {
  chunk: { type: 'string' },
  candidates_file: { type: 'string' },
  tested_count: { type: 'integer' },
  hits: HITS,
  creator_statements: { type: 'array', items: { type: 'object', properties: { date: { type: 'string' }, text: { type: 'string' } }, required: ['date', 'text'] } },
  community_claims: { type: 'array', items: { type: 'object', properties: { who: { type: 'string' }, date: { type: 'string' }, claim: { type: 'string' }, status: { type: 'string' } }, required: ['claim'] } },
  untested_ideas: { type: 'array', items: { type: 'string' } },
  notes: { type: 'string' } }, required: ['chunk', 'candidates_file', 'tested_count', 'hits', 'creator_statements', 'community_claims', 'untested_ideas'] }
const HYP_SCHEMA = { type: 'object', properties: {
  lens: { type: 'string' },
  candidates_file: { type: 'string' },
  tested_count: { type: 'integer' },
  hits: HITS,
  hypotheses: { type: 'array', items: { type: 'object', properties: { hypothesis: { type: 'string' }, evidence: { type: 'string' }, candidates_tested: { type: 'integer' }, result: { type: 'string' } }, required: ['hypothesis', 'result'] } },
  new_facts: { type: 'array', items: { type: 'string' } },
  promising_untested: { type: 'array', items: { type: 'string' } },
  notes: { type: 'string' } }, required: ['lens', 'candidates_file', 'tested_count', 'hits', 'hypotheses', 'new_facts', 'promising_untested'] }
const CORPUS_SCHEMA = { type: 'object', properties: {
  name: { type: 'string' }, path: { type: 'string' }, bytes: { type: 'integer' }, words: { type: 'integer' },
  sources: { type: 'array', items: { type: 'string' } }, coverage: { type: 'string' }, notes: { type: 'string' } }, required: ['name', 'path', 'bytes', 'words', 'sources', 'coverage'] }
const ENGINE_SCHEMA = { type: 'object', properties: {
  candidates_total: { type: 'integer' }, forms_total: { type: 'integer' }, hits: HITS,
  generation_rules: { type: 'string' }, per_corpus: { type: 'array', items: { type: 'string' } }, truncated: { type: 'string' }, notes: { type: 'string' } }, required: ['candidates_total', 'forms_total', 'hits', 'generation_rules', 'per_corpus', 'truncated'] }
const RETEST_SCHEMA = { type: 'object', properties: { files: { type: 'integer' }, candidates_total: { type: 'integer' }, forms_total: { type: 'integer' }, hits: HITS, notes: { type: 'string' } }, required: ['files', 'candidates_total', 'forms_total', 'hits'] }
const VERDICT_SCHEMA = { type: 'object', properties: { refuted: { type: 'boolean' }, reproduced: { type: 'boolean' }, address_match: { type: 'boolean' }, reasoning: { type: 'string' } }, required: ['refuted', 'reproduced', 'address_match', 'reasoning'] }
const CRITIC_SCHEMA = { type: 'object', properties: { missing: { type: 'array', items: { type: 'object', properties: { item: { type: 'string' }, why: { type: 'string' }, how: { type: 'string' } }, required: ['item', 'why', 'how'] } }, ranked_next_steps: { type: 'array', items: { type: 'string' } }, summary_path: { type: 'string' } }, required: ['missing', 'ranked_next_steps', 'summary_path'] }
