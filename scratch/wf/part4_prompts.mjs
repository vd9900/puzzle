
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
