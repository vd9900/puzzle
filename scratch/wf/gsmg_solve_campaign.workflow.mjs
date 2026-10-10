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

// ---------------- Corpus assemblers (local repo material and public-domain texts only) ----------------
const CORPORA = [
  { key: 'puzzle_texts', prompt: `Assemble a corpus from the puzzle's own decrypted and public page texts already in the repo: research/artifacts/phase2.txt, phase3.txt, phase32.txt (latin-1), phase32-beaufort.txt, phase32-checkerboard.txt, the SalPhaseIon textarea text (research/sources/salphaseion.html), research/sources/phase2.html, theseedisplanted.html, and the puzzle README files (research/sources/community-README.md and maintained-README.md). Normalize to UTF-8 plain text, one sentence or clause per line where possible. Save to ${SCR}/corpora/puzzle_texts.txt.` },
  { key: 'creator_messages', prompt: `Assemble a corpus of every creator-attributed Telegram message (research/evidence/cycle02/_work__creator_jrk.txt) plus every message in the full transcript (research/evidence/cycle02/_work__chat_transcript.txt) authored by Jrk Bgrt, SoWut or marked admin. One message per line, header dates stripped, duplicates removed. Save to ${SCR}/corpora/creator_messages.txt.` },
  { key: 'chat_substantive', prompt: `Assemble a corpus of all substantive community messages: concatenate ${SCR}/chat_chunks/chunk*.filtered.txt, strip the header lines, keep one message per line, drop exact duplicates and lines shorter than 8 characters. Save to ${SCR}/corpora/chat_substantive.txt.` },
  { key: 'carroll_public_domain', prompt: `Assemble a public-domain Lewis Carroll corpus: clean the existing OCR of The Game of Logic at research/evidence/cycle02/_work__gameoflogic_ocr.txt, and download the Project Gutenberg plain-text editions of Alice's Adventures in Wonderland and Through the Looking-Glass (public domain). Strip Gutenberg headers and footers, one sentence per line. Save to ${SCR}/corpora/carroll_public_domain.txt.` },
  { key: 'gsmg_public_site', prompt: `Assemble a corpus of GSMG.io's own public web text: fetch https://gsmg.io/ and the first-party pages it links (about, docs, blog, FAQ), plus Wayback Machine snapshots of gsmg.io from 2019 and 2020 (use the availability API with modest pacing). Extract visible text only, one sentence per line. Save to ${SCR}/corpora/gsmg_public_site.txt. If you receive HTTP 429, stop rather than retrying aggressively.` },
]

// ---------------- Hypothesis lenses ----------------
const LENS_TAIL = `Write every candidate you test, one per line, to ${WF}/cands_lens_KEY.txt (replace KEY with your lens key) and run the oracle on it. Put door-type candidates in ${WF}/cands_lens_KEY_doors.txt and run the oracle on that file with --doors 40. Record each hypothesis with its evidence and result.`
const LENSES = [
  { key: 'architect_choice', prompt: `Lens: the token "lastwordsbeforearchichoice". Using your own knowledge of the Architect scene (short quotations only), enumerate every plausible reading: the Architect's final sentences before Neo picks a door, Neo's final words before choosing, the words immediately preceding the word "choice", the closing exchange, and the alternative that "archi" abbreviates something other than Architect. For each reading produce exact-wording candidates in the puzzle's normalizations (as written, lowercase joined, no punctuation) and test them, including as hidden-door preimages.` },
  { key: 'mr_robot_table', prompt: `Lens: the Phase 2 riddle table "# X 2 S H 4 Y 0 Q B 15 #" with its four definitions (Q: a hacker's swordless fish, extended, with I and W below; B: ((BV80605001911AP) - sqrt(-1))^2; H: (answer to only this puzzle) * -1; S: Klingon cha' + (vagh * jav)). Re-derive each value yourself and compare with the community values (S=32, H=42, Q=82, B=25 or -42). Treat the result as (a) Decentraland coordinate pairs, checking the public catalyst content API for scenes at every (X,Y) and (Y,X) pair with modest pacing and reporting any GSMG-related entity, (b) a numeric password or key fragment, (c) chessboard squares. Produce concrete candidate strings for each reading and test them.` },
  { key: 'classical_crypto', prompt: `Lens: classical cryptanalysis of dbbi (91) and faed (570) using the Phase 3.2 conventions. Key observation to test first: under the a=0..i=8 mapping the dbbi marker symbols b and e are digits 1 and 4, the exact escape digits of the solved straddling checkerboard (alphabet fubcdora/lethingkymvpszjqwx. in tools/gsmg.py). Decode dbbi, the 60/61-symbol residual and faed with that board under both digit mappings (a=0 and a=1), with and without prime-position zeroing, forwards and reversed; score readability; test every decoded string and its sha256 as a password. Then try the same board with the escape rows re-keyed from the dbbi order. Report readable fragments verbatim.` },
  { key: 'primes_matrix', prompt: `Lens: numeric hints. "matrixsumlist", "yellowblueprimes", "R=18 A=1 B=2 ... could also be 21 or 1812 bit", "some characters need to be zeroed out", "at least prime number is very important". Using the real 14x14 grid and colour map (scratch/common.py MATRIX and tools/gsmg.py extract_grid), construct derivations that are NOT in the exhausted list: prime-indexed cells in each traversal order, sums restricted to prime rows/columns, A1Z26 of the hint words with primes removed, 21-bit and 1812-bit framings, and zeroing prime-position characters of the Phase 3.2 speech and of the SalPhaseIon URL hash. Turn each into concrete strings and test them.` },
  { key: 'books_sources', prompt: `Lens: the referenced books. Cosmic Duality (Time-Life, Mysteries of the Unknown, 1991; the creator called a posted page "scary specific" and named a "Life and Death" page), Jacque Fresco's writings (The Venus Project, Looking Forward), and Carroll's The Game of Logic. Using legitimate search only (archive.org full-text search API, Google Books API snippets, library catalogue descriptions, published reviews), collect chapter and section titles, picture captions and short well-known sentences, especially from the Life and Death chapter. Produce candidates (titles, captions, key phrases, yin-yang terminology) and test them.` },
  { key: 'creator_context', prompt: `Lens: the creator's own wording. View every hint screenshot listed in the brief (research/sources/maintained-hints__*.png) with the Read tool, decode the 2023-02-23 binary dump yourself and compare with the repo's decode, and study the creator messages file. Characterize habits (typos such as "hundred FOUR", "Ancient spelling", Dutch-English phrasing, acrostics like D-O-O-R). Propose concrete readings of "our first hint is your last command" and "ans too" and of the 2024 and 2026 hints, turn each into exact candidate strings, and test them.` },
  { key: 'web_osint', prompt: `Lens: public write-ups since 2024. Search the web (reddit, bitcointalk, GitHub code search for salphaseion / matrixsumlist / lastwordsbeforearchichoice, Medium, blog posts, video descriptions) for GSMG puzzle progress or claimed partial solutions that post-date this repo's sources. Collect every untested concrete candidate or decode claim with its URL, test the candidates, and list the sources.` },
  { key: 'parse_skeptic', prompt: `Lens: independent re-parse. Starting from the raw bytes of research/sources/salphaseion.html, re-derive the segmentation without trusting scratch/common.py: where the z delimiters fall, whether "shabef" attaches to the preceding or following text, why a binary run ("enter") sits inside the small blob's base64, and whether the z-words admit other base conventions. Then test the sha256 chains implied by "shabef our first hint is your last command" and "shabef ans too": sha256 of each earlier phase answer, double sha256, sha256 of the SalPhaseIon URL hash, sha256 of "enter", and sha256 of the concatenations in page order. Test everything with the oracle.` },
]

// ---------------- Stage prompts ----------------
const CHUNKS = Array.from({ length: 16 }, (_, i) => String(i).padStart(2, '0'))

function minePrompt(nn) {
  return `${COMMON} Task: mine Telegram chat chunk ${nn}. Read ${SCR}/chat_chunks/chunk${nn}.filtered.txt in full (use Read with offsets; it is large) and consult ${SCR}/chat_chunks/chunk${nn}.txt for surrounding context when a message is ambiguous. Extract: (a) every concrete string a solver proposed or tested as a password, door path, or key input, verbatim; (b) every claimed partial decode or intermediate result (decoded words, numbers, hashes, URLs); (c) every creator statement (Jrk Bgrt, SoWut, admin) with its date; (d) technical claims about SalPhaseIon, dbbi, faed, matrixsumlist or the AES blobs, with who made them and whether they were confirmed or refuted in the chat. Write the candidates from (a) and (b) to ${WF}/cands_chunk${nn}.txt (one per line, max 3000) and door-type candidates to ${WF}/cands_chunk${nn}_doors.txt (max 40). Run the oracle on both files (the doors file with --doors 40). Return the structured object.`
}

function lensPrompt(l) {
  return `${COMMON} ${l.prompt} ${LENS_TAIL.split('KEY').join(l.key)} Return the structured object with lens = "${l.key}".`
}

function enginePrompt(corpora) {
  const list = corpora.map(c => `${c.name}: ${c.path} (${c.words} words)`).join('; ')
  return `${COMMON} Task: bulk dictionary campaign. Corpora available: ${list}. For each corpus, generate candidates: every line; every clause (split on , ; : . ? !); every word window of length 1 to 8 within a line. Deduplicate, write each corpus's candidates to ${WF}/engine_<corpus>.txt, and run ${SCR}/fastcheck.py --procs 3 --label engine_<corpus> on it. Process corpora in this priority order: puzzle_texts, creator_messages, gsmg_public_site, carroll_public_domain, chat_substantive. Keep total wall time under about three hours; if you must truncate (for example limit window length for the largest corpus), say exactly what was dropped. Return the structured object.`
}

const RETEST_PROMPT = `${COMMON} Task: independent consolidated retest. Concatenate every ${WF}/cands_*.txt file (exclude engine_* files), deduplicate, and run ${SCR}/fastcheck.py --procs 4 --label retest on the merged file. Also run ${SCR}/oracle.py --selftest first and report its result in notes. Return the structured object.`

function reproducePrompt(h) {
  return `${COMMON} A previous agent reported this hit: ${JSON.stringify(h)}. Reproduce it from scratch using only the openssl command line (enc -d -aes-256-cbc -a with -md sha256 and with -md md5, password exactly as stated and as its sha256 hex) against the blob named. Do not trust any Python in the repo. If the plaintext parses as a private key, WIF or seed, derive the address locally and compare with the target; never print the key. Return refuted=true unless you independently reproduced a structured plaintext.`
}

function refutePrompt(h) {
  return `${COMMON} A previous agent reported this hit: ${JSON.stringify(h)}. Your job is to refute it. Consider: chance printable output (expected rate), padding-only artifacts, a candidate that is actually one of the already-solved blobs, a mis-specified blob, or a tool bug. Re-run the oracle on the exact candidate and inspect the plaintext structure. Default to refuted=true if uncertain.`
}

function criticPrompt(summary) {
  return `${COMMON} Task: completeness critic. Here is the JSON summary of the whole campaign: ${summary}. Identify what is missing: a modality not run, a claim not verified, a source not read, a lens whose promising_untested items were never tested. Write a human-readable ${WF}/SUMMARY.md (findings, negatives with counts, hits and verdicts, ranked next steps). Return the structured object with summary_path set.`
}

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
