# GSMG puzzle — cycle 37 agent briefing (read this, then scratch/wf/BRIEF.md for full background)

You are one agent in a multi-agent campaign on the public, unsolved GSMG.IO Bitcoin puzzle
(prize address 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe, ~1.25 BTC left). Repo: /home/vin/bitcoin_puzzle.
Read `/home/vin/bitcoin_puzzle/scratch/wf/BRIEF.md` (structure, tools, exhausted families) and
`/home/vin/bitcoin_puzzle/research/artifacts/cycle36/findings.md` (latest negatives) before you design anything.

## Corrections since BRIEF.md (IMPORTANT)
- The on-chain OP_RETURN "breadcrumb" trail from 3GSMG24… is NOT the creator's. On 2026-10-12 the community
  maintainer (Naddiseo, puzzlehunt/gsmgio-5btc-puzzle issue #114) said the OP_RETURN messages "are red-herrings posted by
  other community solvers… confirmed by jrk". Ignore every conclusion drawn from them (incl. "creator ran kangaroo").
  `bw_oracle.py` remains useful only for the PRIZE address check.
- The same maintainer: "it's highly likely that the passwords required for Salph and Cosmic can be derived from within
  that page itself (just as every other section of the puzzle has)."
- Community issue #115 (Oct 2026): "BYTENPHASE…" from mod-26 sums of 9-letter groups of faed after dropping "fae" —
  judged coincidence by maintainers (monoalphabetic fishing). Don't build on it.

## New negatives from cycle 37 (main loop, do not repeat)
- faed / dbbi as decimal expansion of text with zeros disguised as any single letter (each occurrence independently
  zero-or-not), lowercase and printable charsets: no solution (`scratch/c37/zero_dfs.py`; self-test recovers Z1).
- Same with zeroing allowed at any letter but only at prime positions (1/0-based, from left/right, string reversed),
  charsets lower/print/hex/HEX/base64/base58/alnum: no solution (`scratch/c37/zero_dfs2.py`).
- Every injective letter→digit map for base 10 (byte-local pruning) and base 9, on dbbi, residual60, faed
  (`scratch/c37/subst_sweep.py`; results appended to scratch/c37/RESULTS.md when done).
Useful fact behind those tools: in base 10, the low k bytes of an integer depend only on its lowest 8k decimal digits
(10^p ≡ 0 mod 256^k for p ≥ 8k), so "is this digit string the decimal form of text?" can be tested byte by byte from
the right with exponential pruning. Reuse `zero_dfs.dfs()` for any new digit-reading hypothesis.

## Oracle facts
- `cd /home/vin/bitcoin_puzzle/scratch && python3 oracle.py --file C.txt --label L` (system python3; NOT .venv).
  `python3 fastcheck.py --file BIG.txt --procs 4 --label L` for >10k candidates. `from common import *` gives
  DBBI, FAED, Z1, Z2, MATRIX, BLOBS, try_pw, evp, letters_to_digits, primes_upto, sha256hex.
- Blob sizes: inner 80 B and small 80 B ciphertext ⇒ plaintext 64–79 bytes (a 64-char hex key + full padding block
  gives exactly 80). A real decrypt is very likely printable (hex/WIF/base58/text). Cosmic 1328 B ⇒ long text/data.
- Every solved stage used: password = lowercase-hex sha256 of a lowercase, space-free concatenation of answers;
  openssl enc -aes-256-cbc -a, EVP_BytesToKey(sha256, 1 iteration). Phase 1 answer: song lyric; Phase 2: "causality",
  then 7 joined parts; Phase 3: "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple".

## Compute
- Local: 4 threads, shared with other sessions — keep local jobs ≤ 2 processes.
- Remote VM: `ssh azure-temp` (8 cores, 62 GB, no GPU, Ubuntu). Work ONLY inside `~/gsmg37/` there (create it);
  do not touch other directories on the VM. Copy code with scp; python3 is available (pip install --user pycryptodome
  if needed). Use it for anything over ~10 CPU-minutes.

## Rules
- USER DIRECTIVE (2026-10-13): NO heavy guessing loops. Do not brute-force password/phrase/variant lists or
  enumerate large blind combinatorial families. Allowed: deterministic decodes, structural/statistical analysis, and
  small principled candidate sets (≲ a few thousand) that each follow from a stated, evidence-backed derivation.
  Parameter enumeration is only OK when a validated structural detector (not the AES oracle) does the filtering and the
  space is ≲ 10^6 derivations. Stop any running job that violates this.
- Never sign/broadcast transactions. If something decrypts to key-like material, write it ONLY to
  scratch/wf/HITS.log and report "HIT: blob=… kdf=… candidate=…" plus the first 40 printable bytes.
- Do not research private individuals (the creator's real identity, friends, family). Public puzzle material only.
- Do not quote film/song dialogue at length in your outputs (content filters kill long verbatim quotes); refer to lines
  by short paraphrase or ≤ 12-word fragments.
- gsmg.io probes: ≤ 40 per agent, ≥ 0.5 s apart, via oracle.py --doors/--forms only.
- Put all files you create under scratch/c37/<your-lens>/. Do not edit files outside that directory.
- Be quantitative: every test needs a stated oracle, candidate count, and a control (e.g. a planted-answer self-test
  or a shuffled-input baseline) so a negative result is trustworthy.

## Main-loop findings to build on (read scratch/c37/RESULTS.md "Main-loop deterministic checks")
- faed is mildly NON-stationary: unigram change point at offset 538 (max-scan p=0.004); the last 32 letters
  'bccahhbiibibbibdcbahaidhfahiihic' contain no e and no g; windowed dispersion w=30 p=0.004 (row 18 of 19x30 is the outlier),
  other windows p~0.02-0.03. Any generative model for faed must explain this (uniform-digit/ciphertext models predict
  stationarity; columnar transposition smooths composition).
- digit_codecs lens proved a length-feasibility rule: a 91-digit decimal can never be lowercase text, a 570-digit one never
  lowercase or hex, under ANY letter->digit map (top byte interval fixed by length). Use scratch/c37/digit_codecs/h7_length_feasibility.py
  and h4_topdown.py (top-down interval DFS) for any decimal->bytes hypothesis.
- First image, QR, page formatting, new-year binary hint: no hidden channels (closed).
- WARNING (construction_forensics lens): scratch/quadgrams.pkl and quadgrams_clean.pkl were partly built from puzzle chat that
  contains the btcseed decode (19x) and other puzzle strings; they inflate scores of puzzle-derived strings. Use
  scratch/c37/construction_forensics/quad_indep.py (Carroll-only model) for any readability scoring.
