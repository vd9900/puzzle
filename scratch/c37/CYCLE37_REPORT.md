# Cycle 37 report (2026-10-13) — deductive, no-guessing round

Status: UNSOLVED. No key, password, or readable hidden message found. All work under scratch/c37/; per-lens REPORT.md files;
main-loop checks in RESULTS.md; briefing BRIEF_C37.md.

## Corrections to earlier cycles
- The 3GSMG24… OP_RETURN "breadcrumb" trail is NOT the creator's (maintainer Naddiseo, issue #114, 2026-10-12, citing jrk); the
  dust-sweep inference in cycle 36 was invalid. Drop "creator ran kangaroo" etc.
- "Only date I give away is neo's passport expiry" was a joke deflecting personal questions; the 2026-03-03 "Bingo" confirmed a
  South Park quote. btcseed was shown to the creator (2026-03-03) and not confirmed.
- scratch/quadgrams.pkl and quadgrams_clean.pkl are contaminated by puzzle chat (btcseed decode 19x): they made the btcseed body
  look English (z=+22 -> +1.5 with a clean Carroll model). Re-check any older "English-like" claim scored with them.

## Closed this cycle (all with planted self-tests and controls)
1. Full VIC cipher on faed/dbbi residual (~1.2M structurally-filtered key derivations, forward/reversed/gap variants): faed within
   shuffled-control range; detector power 83-100%.
2. Page z-method (letters->decimal->bytes): length-feasibility proof that 91- and 570-digit strings can never be lowercase text
   under ANY map; exhaustive top-down/bottom-up DFS over zero disguise, zero deletion/insertion, prime-position zeroing,
   marker re-insertion (853k class assignments), all 9!/10P9 maps, merged-zero permutations, prime bases, label bit-masks,
   binary magics (gzip/WIF/Salted__), concatenations, faed[:540] (224 B) and the tail: 0 solutions.
3. First image (colour census, QR codeword-level decode with ECI/padding/RS check), page HTML formatting, robots.txt, the
   2026 new-year binary hint: no hidden channels.
4. dbbi vs the 91-letter checkerboard sentence: 40 masks + 36 element-wise sums: nothing readable ("yang" selection n.s.).
5. btcseed: honest p ~3e-6 per setting, ~1e-3..1e-2 after search; 563-letter body indistinguishable from shuffled-faed Bifid
   output on 13 statistics that detect English and 10..64-symbol codes at 90-100%. Verdict: probably coincidence; stop decoding it.
6. Toolchain: CyberChef's exact Bifid reproduces bifid.py; AES blobs are openssl CLI; CyberChef number-base recipes ruled out.
7. matrixsumlist: 11 families of deterministic sum-list/matrix readings (image sums, COO triples, Minesweeper inversion,
   BIP39 checksums, z-method decodes): all at control level.
8. Grammar model: every best-justified per-hint reading and natural assembly was already in the candidate ledgers; 4 new
   derivation-backed tests negative.

## New structural facts
- faed is mildly non-stationary: change point at 538 (max-scan p=0.004); final 32 letters have no e/g; w30 dispersion p=0.004.
  Stationary models (uniform digits, VIC, any transposed checkerboard) fail this; untransposed checkerboards fail lag-1.
  Best surviving model: piecewise — mostly raw decimal digits (g = two digit values) + a short different-makeup tail. Weak.
- Hint grammar: solved stages chain answers (Phase 3 starts with "causality"). If SalPhaseIon chains too, the small blob's
  password may depend on the unsolved Phase 3.2 inner-blob answer — consistent with every page-only assembly failing.

## Remaining options (none is a guaranteed path)
- Inner blob first: if chaining holds, effort belongs on the Phase 3.2 inner blob ("raising the stakes…", "half and better half").
- faed as a NUMBER (not text): e.g. decimal private-key windows vs the prize address (~3k readings) — blind-ish; not run per
  user directive.
- T9 non-invertible grid shapes via ILP; meet-in-the-middle to close the last truncated faed zero-reinsertion runs.
