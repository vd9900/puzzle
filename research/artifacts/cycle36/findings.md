# Cycle 36 — executing phase: new facts, exhausted families, remaining leverage

Date: 2026-10-08. Scope: hands-on testing (local AES/KDF trials, statistical analysis of `dbbi`/`faed`, polite public GET/POST probes of gsmg.io, Wayback Machine archives). Working scripts: `scratch/` (`common.py` = shared parser/KDF/oracle; `exp01`–`exp23`, `doors*.py`, `bifid.py`, `serial.py`, `textmodel.py`). No key recovered; no transaction.

## New verified facts

1. **Site state.** gsmg.io is live. Unknown paths return HTTP 404 with body `Hello :-)`. The hidden form `POST /phase1verification` (field `password`) returns `302 Location: /choiceisanillusion…` for the exact lowercase joined lyric and the generic 404 otherwise; no CSRF token today. Uppercase or spaced forms of the known password are rejected.
2. **Original first piece.** Wayback copies of `app.js` (2019-04-28 and 2020-11-09) show the Vue route `/puzzle` rendered only `<h1>GSMG MEGANIGMA || 5 BTC</h1>` and `<img src="/img/follow_the_white_rabbit.png" alt="Follow the white rabbit">`. The small PNG (350×350, still served) has the identical 14×14 matrix and the same five colours, including the deliberate `#FEFEFE` cell at (7,4). The QR in the large image decodes to `https://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`.
3. **dbbi marker structure.** Reproduced: with one-based logical positions, every prime position holds `b` or `be`; two segmentations exist (L84: 16 `b` + 7 `be`; L83: 15 + 8). 0/5000 letter-shuffles admit any segmentation; zero-based indexing admits none. Independently, dbbi contains exactly 15 lone `b` and 10 `be` digraphs = 15 blue + 9 yellow + 1 near-white cells; `b`=2=B and `be`=25=Y in a1z26. The physical-order token sequence matches no natural grid traversal (best 18/25); only the prime-logical order gives the 20-bit spiral prefix match. L84's 16/7 split equals the speech's "sixteen encryptions / seven intertwined passwords".
4. **faed statistics.** Digit unigram g=107, i=75, e=69, h=58, f=57, a=54, c=52, d=49, b=49. Mutual information at lags 1–30: all |z|<2 (control: Phase 3.2.2 stream lag-1 z=5.9). No per-column non-uniformity for widths 2–40 (max z 1.3 vs shuffled median 1.5). No pair-level homophonic signature. Two halves differ in distribution (`8`: 19 vs 39; `9`: 29 vs 46), lag-285 pairs independent.
5. **Song.** Phase 1's song is Logic, "The Warning" (1990, Strictly Rhythm), spoken word in phases; phase three asks "red rose or black rose, no in-between". The first official hint "Roses are White but often Red" echoes it. The community had already tried the Phase 3 lines on the form (2023).
6. **Creator context recovered.** "Correct / No / Can't say anything about this" (2023-06-10) answered: tail blob unsolved (yes), tail blob is the SalPhaseIon hint (no), Phase 2 table useless (can't say). The table reads `X [2,32,−42,4] Y [0,Q,−16,15]` (Decentraland coordinates; −42,−16 ≈ the audio parcel). barrystyle's "very specific hint" (2022-12-10) is the Time-Life *Cosmic Duality* book cover (archive.org copy is access-restricted). Keymaker's final lines before the Architect: "It was meant to be. That door will take you home. You'll know which door. Hurry, Neo."

## Negative results (do not repeat)

| Family | Size | Oracle |
|---|---|---|
| Prime-position zeroing/deletion in dbbi/faed (both bases, both directions) → decimal→hex→ASCII and as passwords | 36 variants | printable ratio, AES padding ×3 blobs ×2 KDF |
| Keyed columnar transposition of dbbi/faed by `matrixsumlist`, `lastwords…+thispassword`, 4 conventions | 24 | decimal→ASCII |
| Serial-structure detector (H(next\|prev) z vs shuffles; validated: 3.2.2 stream −5.4, transposed −1.1, right key −6.1, wrong +0.3) applied to: additive keys (dbbi, residual60/61, markers, image sums, a1z26 phrases) mod 9/10 ± at offset 0 and reversed; per-column keys; keyed irregular columnar for 90 keywords, Myszkowski, double transposition; plain k-column 2–285; spirals/boustrophedon/diagonals on all 14 factor grids and 100+ padded grids; rail fence k=2–60 all offsets; numeric-key columnar; lag-difference autokeys k=1–119; long running keys (dbbi 91, residual, 1539-letter speech a1z26/a0z25, matrix bits, faed reversed) at **all** offsets | ≈38,000 candidates | best non-artifact z ≈ −4.4 at 400 shuffles, inside the extreme-value floor |
| Calibrated simulated-annealing over column permutations of faed, widths 5–40, vs 3 shuffled controls | 36 widths | no real-vs-control gap (|gap| ≤ 0.07 bits) |
| Word-level a1z26 digital roots / sums / lengths of Architect speech, Phase 2/3 texts, VIC message vs faed/dbbi/residual | 6 modes × 8 texts | LCS ≤ 7, alignments at chance |
| dbbi as letter-wise function of the 91-letter VIC message | — | 4/21 letters consistent (chance) |
| Residual-56 (dbbi minus all b/be; 8 symbols) as octal (all 8! maps), decimal→ASCII, 4×14/7×8 sum lists vs image sums | 80,640 | nothing printable, no sum identity |
| Weighted colour sums of the 14×14 image as the 91-digit dbbi (any weights, 9 orderings, exact DFS) | exhaustive | none |
| Colour-prime weight sweep → row/col/diag sum lists (5 formats) + speech word selection → sha256/raw passwords | 1,324,942 forms | 31,131 padding hits = chance (1/42.5); 0 structured |
| Roadmap-ordered token concatenations (yellow/blue numbers × primes × matrix × sum list × last-words × yinyang) → sha256 | 6,327,271 | 0 structured |
| Phrase batteries: Architect/Keymaker lines, Roses poem exact formattings, Mr. Robot HSM strings (z1on0101, 022350), MEGANIGMA/alt-text strings, page tokens, numeric sums, puzzle-password chains and digest combinations; alternate hash encodings (trailing newline, uppercase hex, double sha256, md5/sha1/sha512) | ≈5,600 forms | 0 structured |
| Brainwallet keys sha256/sha256d of ≈100 thematic phrases vs both addresses | 498 | none |
| Hidden-door GETs `gsmg.io/<sha256(text)>` for curated texts (page tokens, Architect lines, roadmap, first-piece text variants incl. QR URL and MEGANIGMA headline) and 56 plain paths | 339 | all 404 |
| Hidden form POSTs (all song lines, rose variants, door words, Keymaker lines, roadmap tokens) | 178 | all 404 |
| Base-9/base-10 integer conversions of faed/dbbi/residual → bytes; 32-byte windows vs both addresses | 36 | none |

## Interpretation

- faed is indistinguishable from an i.i.d. source with a skewed unigram. Its unigram fits a straddling checkerboard with escapes `g`,`i` and a rare letter in column 0, but no keyed or geometric transposition in the tested families restores serial structure, and no long key from the puzzle's own objects decrypts it. Either the key is external, or faed is filler ("raising the stakes without extra chances of winning").
- dbbi is designed: the marker layer is certain. Its residual (56/60/61 symbols) still decodes to nothing under every digit→text map tried.
- The creator's "really close" (Jan 2023, README state) and "hardest part is done" (Aug 2023) imply the final password is assembled from visible tokens, yet 6.3M roadmap-ordered concatenations and all natural phrase candidates fail under the established sha256-hex/EVP-SHA256 grammar.

## Remaining leverage

1. The semantic identity of "lastwordsbeforearchichoice" (Keymaker/Architect readings exhausted under standard normalizations).
2. The Cosmic Duality book: the creator called it "scary specific"; its text is access-restricted online.
3. The "close friends" hint points to personal-context vocabulary; this repository does not research private individuals.
4. A hidden door remains plausible (creator, Dec 2021) but no candidate text produced one.

## Addendum (2026-10-08): creator's on-chain breadcrumb trail, fully resolved

Wallet `3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK` is creator-controlled: its "Halving" dust (tx a798905f…) was consumed by the
creator's own 2.5 BTC halving spend (tx 2aa9a4a9…) in the same block on 2020-05-11. Its OP_RETURN dust recipients are
brainwallet addresses of stage answers (compressed P2PKH unless noted):

| message | recipient | preimage / construction |
|---|---|---|
| Good job, Neo! (×2, 2020-04-03) | 148XH2…, 13HGhj… | raw key = 8 zero bytes + ASCII `gsmg.io/theseedisplanted`; and the same bits reversed |
| GSMG.io: are you sure? | 1AD2wf… | sha256(phase-1 lyric) |
| GSMG.io: Right, this is causality | 1Jqq37… | sha256("causality") |
| GSMG.io: You are here because 227 chars were correct | 1M5ypv… | sha256(227-char Phase 3 preimage) |
| GSMG.io: phase3.2 pass OK | 1K23RS… | sha256(Phase 3.2 preimage) |
| GSMG.io: part of the cipher | 18Cchr… | sha256(Phase 3.2.2 checkerboard digit stream) |
| GSMG.io: do you beleive me you need it? | 1GyT5W… | sha256("1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe") |
| (none, 2020-04-07, unspent) | 1NULY7… | tips address hard-coded in keyjoke/vs-kangaroo-hybrid (uploaded 2020-04-05) — a donation, not a puzzle key |
| GSMG.io neighbors, half and double (2021-07-18) | 4 addresses | 2P, P/2, P+G, P−G of the prize public key, uncompressed |

Consequences: (1) the trail confirms the sha256(answer) convention but contains no unsolved-stage oracle; (2) the creator
ran a GPU Pollard-kangaroo tool in April 2020 and revealed the prize public key by spending in May 2020, which makes a
bounded-interval key search a plausible intended finish ("note that also brute forcing might be required"). Prize spends:
2020-05-11 (5 → 2.5 to 17ucy…) and 2024-04-24 (→ 1.25 to 17ucy…), both at halvings; balance ≈ 1.2537 BTC.
Other new facts: Decentraland estate 955 metadata (2019-05-29) = "gsmg.io magic puzzle piece" / "White Rabbits everywhere";
scene code is a cube question mark + text "GSMG.IO 5 BTC PUZZLE CHALLENGE"; puzzlepiece.mp3 was exported from Logic Pro X 10.4.1.
Negative: all of the above strings and the estate metadata as AES passwords, doors and form inputs; all dbbi/faed
zeroed/residual integer readings (bases 2/9/10, mod n) as private keys.

## Addendum (2026-10-09): creator statements re-read, more negatives

New creator facts (from hint screenshots and chat): 2026-07-12 "The '5' btc was never the actual prize. That was only a tiny
fraction." and "I held quite a secret in my head which I seriously wanted to share with the planet"; 2024-04-19 the prizes
are "a private key, some 'obscure' intel"; 2023-08-06 "Has anyone passed the salvation part?" → "Partly."; 2023-08-03 "the
hardest part is done"; 2023-01-12 "I checked a certain GitHub yesterday ... You guys are really getting close"; 2021-05-21
"First or zero" answers "the answer to another door from the 1st piece?" (so the extra door's answer is in the first image);
2026-03-03 the creator mentions rewatching Mr. Robot "episode 3.5". The 2026-01-01 binary hint reads "Happy new year! Make
the best of everything. Oh, and here's a "tiny hint" <3." preceded by five messages of 1..5 dots one minute apart.
Decentraland: the GSMG deployer owns only estate 955 (parcels -41,-16 / -41,-17); no GSMG scene at any Phase-2 table pair.
Negatives: 7-bit/8-bit decodes of the matrix in all traversals; all 218,812 substrings of dbbi/faed/residual as AES passwords
and all prefixes/suffixes as brainwallet keys; row/column sum lists of dbbi/faed/residual at every width mapped to letters
(mod 26/27/9, digital root, cumulative) and whole-number base-26/27/36 conversions; Neo's passport dates; the GSMG slogan;
first-hint/last-command literal readings; checkerboard decode of dbbi with the Phase 3.2 board (a=0 and a=1); arithmetic and
hash combinations of the known stage keys (4,420) against both prize addresses; Phase-2 table readings (workflow lens, 736
candidates). Kangaroo cheap tier (dbbi residual prefixes, ≤60-bit intervals): running, no key in the first 11 intervals.
