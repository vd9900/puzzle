export const meta = {
  name: 'gsmg-cycle37-lenses',
  description: 'GSMG puzzle cycle 37: 7 research lenses (deductive, no guessing) execute tests, adversarial verify of leads, completeness critic',
  phases: [
    { title: 'Investigate', detail: '7 lenses design + execute novel tests with controls' },
    { title: 'Verify', detail: 'adversarial reproduction of any hit or lead' },
    { title: 'Critique', detail: 'coverage critic ranks next round' },
  ],
}

const HEADER = `You are a research agent on the public, unsolved GSMG.IO Bitcoin puzzle.
FIRST read /home/vin/bitcoin_puzzle/scratch/c37/BRIEF_C37.md, then /home/vin/bitcoin_puzzle/scratch/wf/BRIEF.md and
/home/vin/bitcoin_puzzle/research/artifacts/cycle36/findings.md. Obey every rule in BRIEF_C37.md (no tx signing, no
private-individual research, no long film/song quotes, files only under scratch/c37/<lens>/, VM work only in ~/gsmg37/).
Before running any family, grep the repo (research/*.md, research/artifacts/cycle*/findings.md, scratch/*.py, scratch/wf/)
to confirm it is not already exhausted; if it is, skip it and say so. You are expected to WRITE CODE AND RUN IT, not just
theorize: design concrete hypotheses, implement them, validate the implementation with a planted-answer self-test, execute,
and report quantitatively. Spend real effort: several hypotheses, each executed. Your final output is structured data for a
script (no prose for humans).
USER DIRECTIVE — NO HEAVY GUESSING LOOPS: the user explicitly forbids brute-force guessing. Do not generate large
password/phrase/variant lists or blind combinatorial sweeps against the AES oracle. Each password candidate you test must
follow from a stated, evidence-backed derivation; keep candidate sets small (≲ a few thousand total for your lens). Prefer
deterministic decodes and structural/statistical analysis. Parameter enumeration is acceptable only when a validated
structural detector (not the AES oracle) does the filtering and the space is ≲ 10^6 derivations. Prefer depth of reasoning
over breadth of guessing. The previous attempt at this lens was interrupted; files from it may exist in your directory —
you may reuse validated code but re-check it.`

const LENSES = [
  { key: 'vic_cipher', prompt: `LENS: full VIC cipher (Hayhanen/Sukhanov) on faed (570 symbols a-i) and dbbi (91).
Rationale: the community already calls the Phase 3.2 digit stream a "VIC cipher", but only the straddling checkerboard part was
ever used. A full VIC message = straddling checkerboard digits, then a columnar transposition, then a disrupted columnar
transposition, with all keys derived from (20-letter key phrase, 6-digit date, personal number, 5-digit keygroup inserted in
the ciphertext). The output looks i.i.d., which matches faed's verified statistics (no serial structure, no column keying
for a single transposition). The creator said "The only date I give away is the expiry date of neo's passport" (2021-12-31;
the film passport expires 11 Sep 2001) and the Phase 1 password was a lyric line from Logic "The Warning" (VIC key phrases
were the first 20 letters of a song line). 570 = 114 five-digit groups (565 + a 5-digit keygroup).
Tasks: (1) implement VIC key derivation + decryption exactly per the Wikipedia "VIC cipher" article (fetch it) and VALIDATE on
its worked example (or another published test vector) before anything else. (2) Handle the 9-letter alphabet: faed has no
zero; its 'g' is ~2x frequent (likely g covers two digits, e.g. 7 and 0 — the creator hint "some characters need to be
zeroed out"). Since VIC transpositions are pure permutations, you can un-transpose the LETTER string first and resolve g
ambiguity afterwards during checkerboard decoding (beam search with an English quadgram model: scratch/quadgrams_clean.pkl /
scratch/textmodel.py). Also score un-transposed candidates with the serial-structure statistic (scratch/serial.py hcond_z)
which was validated to detect real checkerboard streams (z ~ -5). (3) Enumerate parameters: key phrases = first 20 letters
of every line of the Phase 1 song lyrics available in the repo, of the solved stage passwords/answers, of the Architect
speech sentences in research/artifacts/phase32-beaufort.txt, of puzzle strings (thematrixhasyou..., followthewhiterabbit...,
lastwordsbeforearchichoice, theseedisplanted...) — keep this to the few dozen best-motivated phrases; dates = 11 Sep 2001
in the handful of plausible digit formats (the VIC convention takes the first 6 digits of the written date) plus the puzzle
launch date 2019-04-13; personal numbers 1..20 (note "one for one, four for one"); keygroup position per VIC rule. Filter
every derivation with the structural detector first; only decode the survivors. Use both the
VIC-derived checkerboard and the Phase 3.2 checkerboard alphabet fubcdora/lethingkymvpszjqwx. (escapes 1 and 4). Use the
azure-temp VM (8 cores) if the enumeration is large. Report the best-scoring candidates against a shuffled-faed control.` },
  { key: 'digit_codecs', prompt: `LENS: generalized "z-method" digit codecs. On the SalPhaseIon page, Z1/Z2 decode as letters->digits (a=1..i=9,o=0)
-> one decimal integer -> hex -> ASCII. dbbi (91) and faed (570) use the same letters but no 'o'. The creator hints: "primes
are required", "some characters need to be zeroed out", the speech says "reinserting the prime basics". Verified: dbbi has
'b'/'be' tokens at every prime logical position (see research/artifacts/cycle03/prime-boundary.json and scratch/exp05_prime_seg.py
for the exact segmentation; mask1017 tokenization), and the residual is 60/61 letters.
Already negative (do not repeat): single-letter zero disguise and prime-position zeroing via byte-local DFS
(scratch/c37/zero_dfs.py, zero_dfs2.py), full letter->digit substitution sweeps (scratch/c37/subst_sweep.py), plain
deletion/zeroing of markers (cycle36), base-9/10 direct conversions.
Explore NEW codec hypotheses, e.g.: markers ZEROED as tokens ('be'->'o' or 'be'->'oo', 'b'->'o') combined with the exact
tokenization variants (L83/L84, mask1017 alternatives); markers mapped to digits by colour (blue/yellow/near-white -> digits
other than 0) and reinserted; the 25 event labels inserted into the residual at different positions; interleaving dbbi
residual with the matrixsumlist bits; reading token values ('be'=25 as two digits '25' — R=18,A=1,B=2 hint "could also be 21 or
1812"); reading faed/dbbi in reverse or in 2-letter chunks as numbers 11..99; reading as base-9 with the zero-hint; applying
the z-method to the Bifid output (scratch/bifid.py) after mapping its letters to digits; concatenating dbbi+faed (661 digits)
or faed+dbbi; treating Z1+Z2+dbbi+faed as one integer. Use zero_dfs.dfs() for byte-local pruning where applicable (it lets
you test huge families of 'which positions are zero' cheaply), and printable/lowercase/hex/base58/base64 oracles.
Always include a planted self-test showing your pipeline would recover a known text.` },
  { key: 'matrixsumlist', prompt: `LENS: operational semantics of "matrixsumlist" (decoded from the binary between dbbi and faed) and the roadmap hint
"yellow blue primes matrix sumlist last words before archichoice yinyang" (2023-02-23). The 14x14 image matrix is MATRIX in
scratch/common.py; colour cells: 15 blue, 9 yellow, 1 near-white #FEFEFE at row 7 col 4 (see BRIEF.md). Poem hint: "Roses are
White but often Red, Yellow has a number and so does Blue". Creator: "fefefe square is 101 010 if you know how the array is
indexed" was a community line; creator called the text "ancient spelling" (hundred FOUR = 104).
Already exhausted: colour-prime weight sweeps -> row/col/diag sum lists as passwords (1.3M), roadmap concatenations (6.3M),
sum lists mapped to letters mod 26/27/9 etc, sum lists as transposition keys for faed, weighted image sums as dbbi.
Find NEW interpretations and execute them, for example: sum lists written as a decimal string and decoded with the page's own
z-method (decimal -> hex -> ASCII; use scratch/c37/zero_dfs.py ideas for pruning) or re-encoded with the page's letter alphabet
(1->a..9->i, 0->o) and searched for as substrings of dbbi/faed/Z1/Z2; the sum list of dbbi or faed as a matrix whose list is
itself a password under the established grammar (lowercase concatenation, sha256 hex); matrix = the 24 colour cells'
coordinates (sum of row+col per cell, in spiral/byte order) with yellow/blue/prime selection; sums of the bit matrix along
the decoding spiral per byte (24 byte values); 'list' as a Python-style string "[a, b, c]" (formatting variants matter — the
creator's earlier answers were exact strings). Produce small, principled candidate sets (not millions of blind variants)
and test them with scratch/oracle.py; also test any digit-string outputs with the z-method decoder.` },
  { key: 'bifid_body', prompt: `LENS: is the community "btcseed" Bifid decode intended, and if so what is its 563-letter body? NO password guessing in this
lens: every output must verify itself (readable text, valid checksum, valid key/address format, known structure).
Facts: scratch/bifid.py decodes faed with the 5x5 square keyed by dbbi first-occurrence order (dbifhcegaklmnopqrstuvwxyz), period
570, giving 'btcseed' + 563 letters. Because faed uses only square cells 0-8, every EVEN output position is forced into {b,c,d,e}
and each output digraph (2j,2j+1) depends only on faed[j] and faed[j+285] (a fold of the two halves). 8 of 9! first-row orders give
'btcseed'. First found in chat 2025-06-11; the creator was shown it on 2026-03-03 and did not confirm.
Tasks: (1) compute an honest p-value for the 'btcseed' prefix: probability under the null (faed = i.i.d. with its observed unigram,
or a shuffle of faed) that the natural dbbi-keyed decode starts with ANY on-theme 7+ letter token that fits the forced pattern;
enumerate the fitting vocabulary from a large English/crypto wordlist so the look-elsewhere effect is explicit. (2) Test whether the
563-letter body (and the even/odd sub-streams, and the per-digraph 100-symbol code (even in 4) x (odd in 25)) differs from the
null-model Bifid output of shuffled faed: entropy, n-gram repeats, periodicity, index of coincidence, digraph code usage.
(3) If (and only if) there is structure, derive self-verifying decodes: e.g. digraph -> two decimal digits (4x25=100), even letters
as 2-bit values and odd letters as base-25 digits -> bitstream -> bytes/hex/base58/BIP39 (checksum-verified), seed -> BIP32/BIP44
addresses compared with the prize address. Report the p-value and structure verdict even if everything is negative.` },
  { key: 'construction_forensics', prompt: `LENS: reverse-engineer the creator's construction tools, deterministically. NO password guessing in this lens.
Evidence the creator used off-the-shelf tools: openssl enc base64 blobs; the 2026-01-01 hint and others are CyberChef-style 8-bit
binary; Bifid with a keyword-generated square and full-length period (CyberChef 'Bifid Cipher Encode/Decode' uses exactly a keyword
square without J); the z-method (letters a-i,o -> decimal -> hex -> ASCII) resembles CyberChef 'Substitute' + 'From Base'/'To Hex'.
Tasks: (1) fetch the exact CyberChef source (github.com/gchq/CyberChef, src/core/operations/BifidCipherEncode.mjs, BifidCipherDecode.mjs,
FromBase.mjs, ToBase.mjs, Substitute.mjs, etc.) and re-implement precisely, including non-alphabetic handling, case, J handling and
how the keyword builds the square; check whether CyberChef's Bifid Decode on faed with keyword = dbbi (and with keyword = each other
page string: matrixsumlist, the residual, lastwordsbeforearchichoice, thispassword, Z1/Z2 raw letters) reproduces or changes the
'btcseed' output; (2) check which CyberChef operations/recipes could produce strings over exactly the letters a-i with no 'o'
(e.g. From/To Base with radix 9 and a substitution, Bifid of a restricted plaintext, A1Z26 variants) and test each deterministic
inverse on dbbi, the residual and faed with a self-verifying oracle (readable text / hex / base64 / openssl Salted__ / valid key);
(3) compare the solved stages' artifacts with tool fingerprints (base64 line widths, newline handling, binary spacing) to state what
toolchain the creator used. Report concrete reproducible findings.` },
  { key: 'grammar_model', prompt: `LENS: learn the creator's hint->answer grammar from the SOLVED stages and apply it with discipline. STRICT CAP: at most
15 AES/oracle tests in total for this lens, each with a written derivation; no lists, no variants, no casing/spacing sweeps.
Solved examples to model (see scratch/wf/BRIEF.md, tools/gsmg.py, research/pipeline.md, research/sources/maintained-*.ipynb):
the Phase 1 lyric; 'causality' (Merovingian scene); the 7-part Phase 3 preimage (SafenetLunaHSM, 11110, FEN, reversed hex
headline); 'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple'; 'theflower...' ; Beaufort key = the line after
'why am I here' in the film; checkerboard alphabet completion; HASHTHETEXT -> sha256 of the image text. For each, write down: the
hint form, the referent type (film line, person, object, phrase), how the answer string was normalised, and how pieces were joined.
Then, for the SalPhaseIon strings ('matrixsumlist', 'lastwordsbeforearchichoice', 'thispassword', 'shabefourfirsthintisyourlastcommand',
'enter', 'shabefanstoo') and the 2023 roadmap ('yellow blue primes matrix sumlist last words before archichoice yinyang'), derive
the single most grammar-consistent answer per hint and the single most consistent assembly into a password, with reasons, and
grep research/candidates.jsonl + scratch/wf/cands_* to report whether that exact string was already tested. Only test strings that
were not. Short film-line fragments only (no long quotes). Output the model and the derivations; a negative is still useful.` },
  { key: 'faed_provenance', prompt: `LENS: provenance of faed's statistics. Verified: faed (570 letters a-i) is i.i.d.-like (no lag dependence 1-30, no
column structure ≤40) with unigram g=107, i=75, e=69, h=58, f=57, a=54, c=52, d=49, b=49 (expected 57 each if 10 uniform
digits; g ≈ 2x suggests two digit values merged into g). dbbi (91) has b=25, e=18 (b/be markers at primes).
Tasks: build a likelihood comparison of generative models for faed: (a) uniform decimal digits with 0 merged into one letter
(which letter? test all, and all pairs), (b) VIC-style transposed checkerboard digits (simulate with the Phase 3.2
checkerboard on English text, then random transpositions; compare unigram shape incl. the 1/4 escape digits' excess),
(c) base-9 digits of random integers, (d) letters of hex digits mapped somehow, (e) Bifid ciphertext of a 25-letter
plaintext restricted to rows 0-1 (that would force the plaintext's structure — quantify), (f) concatenated decimal of
sha256 digests / ASCII codes (e.g. each byte written as decimal 2-3 digits — 'ASCII decimal codes' produce a strongly
non-uniform digit distribution: 1 frequent as hundreds digit of lowercase 97-122!). Compute the chi-square / likelihood of
faed and dbbi-residual under each, and position-dependent checks (e.g. period-2/3 digit patterns expected for ASCII decimal
codes; test every period 2..12 with the observed letters, including mapping hypotheses where g stands for 1). If any model
fits clearly better, derive and execute the implied decoding (e.g. split into 2-3 digit ASCII codes with the best letter->digit
map, solved via DFS/beam with a printable/English oracle) and report. Include simulations as controls.` },
]

const TEST = {
  type: 'object',
  properties: {
    hypothesis: { type: 'string' },
    why_new: { type: 'string' },
    method: { type: 'string' },
    candidates: { type: 'integer' },
    control: { type: 'string' },
    result: { type: 'string', enum: ['negative', 'hit', 'promising', 'inconclusive', 'skipped_exhausted'] },
    evidence: { type: 'string' },
    artifact: { type: 'string' },
  },
  required: ['hypothesis', 'method', 'result', 'evidence'],
}
const LENS_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    tests: { type: 'array', items: TEST },
    hits: { type: 'array', items: { type: 'object', properties: { blob: { type: 'string' }, description: { type: 'string' }, evidence: { type: 'string' } }, required: ['description', 'evidence'] } },
    leads: { type: 'array', items: { type: 'object', properties: { lead: { type: 'string' }, evidence: { type: 'string' }, next_step: { type: 'string' } }, required: ['lead', 'evidence', 'next_step'] } },
    untested_ideas: { type: 'array', items: { type: 'string' } },
    files: { type: 'array', items: { type: 'string' } },
  },
  required: ['lens', 'tests', 'hits', 'leads', 'untested_ideas'],
}
const VERDICT = {
  type: 'object',
  properties: {
    item: { type: 'string' },
    reproduced: { type: 'boolean' },
    refuted: { type: 'boolean' },
    reasoning: { type: 'string' },
    control_result: { type: 'string' },
  },
  required: ['item', 'reproduced', 'refuted', 'reasoning'],
}

const results = await pipeline(
  LENSES,
  l => agent(`${HEADER}\n\nYour lens key: ${l.key} (write files under /home/vin/bitcoin_puzzle/scratch/c37/${l.key}/).\n\n${l.prompt}`,
    { label: `lens:${l.key}`, phase: 'Investigate', schema: LENS_SCHEMA }),
  (r, l) => {
    if (!r) return null
    const items = [
      ...(r.hits || []).map(h => ({ kind: 'hit', text: `${h.blob || ''} ${h.description} :: ${h.evidence}` })),
      ...(r.tests || []).filter(t => t.result === 'promising' || t.result === 'hit').map(t => ({ kind: 'test', text: `${t.hypothesis} :: ${t.method} :: ${t.evidence} :: artifact ${t.artifact || ''}` })),
      ...(r.leads || []).slice(0, 3).map(x => ({ kind: 'lead', text: `${x.lead} :: ${x.evidence}` })),
    ]
    if (!items.length) return { lens: l.key, result: r, verdicts: [] }
    return parallel(items.map(it => () => agent(`${HEADER}\n\nYou are an ADVERSARIAL VERIFIER (write files under scratch/c37/verify_${l.key}/). Another agent (lens ${l.key}) reported this ${it.kind}:\n\n${it.text}\n\nIts files: ${(r.files || []).join(', ')}.\nIndependently reproduce the claim with your own code where feasible, then try hard to REFUTE it: is it a statistical artifact (run a shuffled/random control with the same search breadth and compare), an implementation bug, a look-elsewhere effect, or a repeat of an exhausted family? Default to refuted=true if you cannot reproduce or if a matched control achieves the same.`,
      { label: `verify:${l.key}`, phase: 'Verify', schema: VERDICT })))
      .then(vs => ({ lens: l.key, result: r, verdicts: vs.filter(Boolean) }))
  },
)

phase('Critique')
const done = results.filter(Boolean)
const summary = JSON.stringify(done.map(d => ({
  lens: d.lens,
  tests: (d.result.tests || []).map(t => ({ h: t.hypothesis, r: t.result, n: t.candidates, e: (t.evidence || '').slice(0, 400) })),
  hits: d.result.hits, leads: d.result.leads, untested: d.result.untested_ideas, verdicts: d.verdicts,
})))
const critique = await agent(`${HEADER}\n\nYou are the COMPLETENESS CRITIC for cycle 37. Below are all lens results (JSON). Do not run big searches yourself; you may run quick checks. Produce: (1) a faithful summary of what was established (negatives with sizes, any surviving leads after verification), (2) gaps: hypotheses a lens claimed but did not actually execute, controls missing, implementation doubts, (3) a ranked list of at most 8 next-round experiments, each concrete (inputs, operation, oracle, expected cost) and justified by puzzle evidence, excluding exhausted families. Write a markdown report to /home/vin/bitcoin_puzzle/scratch/c37/CYCLE37_REPORT.md and return the same content as your final text.\n\nRESULTS:\n${summary}`,
  { label: 'critic', phase: 'Critique' })
return { results: done, critique }
