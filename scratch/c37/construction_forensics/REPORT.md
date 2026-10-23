# construction_forensics (cycle 37) — CyberChef toolchain reproduction

Source: gchq/CyberChef master, fetched 2026-10-13 into `cc_src/` (BifidCipherEncode/Decode.mjs, lib/Ciphers.mjs
genPolybiusSquare, Utils.mjs Array.prototype.unique, FromBase/ToBase/ToCharcode/Substitute/A1Z26/FromDecimal).
`cc_bifid.js` executes the VERBATIM run() bodies (extracted by brace matching, no rewrite) under node v22.

## Tests
| # | hypothesis | method | size | control | result | evidence | file |
|---|---|---|---|---|---|---|---|
| T1 | CyberChef Bifid Decode (exact impl) changes what faed decodes to vs scratch/bifid.py | verbatim CyberChef dec+enc on faed/dbbi/res60 x 14 keywords (none, dbbi, res60, faed, matrixsumlist, lastwordsbeforearchichoice, thispassword, shabefour..., enter, shabefanstoo, Z1/Z2 letters, causality, roadmap string) | 84 | python reimpl equality; planted round-trip; 100 shuffled-input decodes per (op,input,key) | negative | 0/84 mismatches vs bifid.py; Decode(faed,key=full dbbi) == bifid.BIF ('btcseed...'); square DBIFHCEGAKLMNOPQRSTUVWXYZ identical; best other z=+3.6 ('bifndthcbebp...', not text), BIP39 coverage <=0.14 (planted 0.95) | t1_cc_bifid.py, t1_indep_out.txt, t1_results.json |
| T1b | the btcseed BODY is English-like (z=+22..+24 vs shuffled controls) | quadgram score of body vs shuffles / half-rotations / joint perms / block shuffles / 200 random a-i-first squares | ~1000 | independent Carroll-only quadgram model | ARTIFACT -> negative | z=+22 with scratch/quadgrams.pkl AND quadgrams_clean.pkl, but both models are CONTAMINATED: chat transcript contains the btcseed decode 19x ('emck','oemc','deoe' scored like common English). With independent model: body z=+1.5, no control family separates | t1b_body_check.py, t1c_body_source.py, quad_indep.py |
| T1d | creator typed a LITERAL label as keyword (dbbi, faed, z, salphaseion, cosmicduality, gsmg) | verbatim CyberChef decode of faed | 6 | 100 shuffles per key | negative | max z=+0.12; literal 'dbbi' gives square DBIACEFGH... (differs from full-string key) | t1d_literal_keys_out.txt |
| T2 | CyberChef quirks could alter decode | node quirk probes | 5 | n/a | no effect on page strings | J->I uses JS String.replace (FIRST J only): key with 2 J's puts J in the square and drops Z/Y; 2nd+ J in input passes through literally; case preserved per letter; non-letters pass through and consume no coordinates; period = whole message (no period arg). faed/dbbi/res60 have no j, no non-letters, all lowercase -> CyberChef == textbook full-period bifid. A CyberChef-made faed implies an all-letter lowercase plaintext with <=1 j | t2_quirks_out.txt |
| T3 | faed/dbbi/res60 are CyberChef 'To Base r' output (a..i = digits 10..18) | From Base r=19..36 (radix<=18 -> NaN in CyberChef), fwd+reversed, -> To Hex -> bytes | 108 | planted round-trip 36/36 | negative | max printable 0.53 (random ~0.37+-0.07; max-of-108 expectation ~0.55); no Salted__/hex/base64 charset. Prior also ~0: (9/19)^570 for a To-Base-19 output to avoid 0-9 | t3_frombase.py, t3_out.txt |
| T4 | faed = 'To Charcode' base 9 (no delimiter) + Substitute 0-8 -> a-i | map-free sorted-frequency profile vs simulated charcode streams of English, lowercase hex, base64 | 3 models | uniform base-9 null (500 sims) | negative | chi2(faed|english)=249, hex=158, base64=30 (null 99%=18): charcodes force a dominant top digit (27-33%) vs faed's 18.8% | t4_charcode9.py, t4_out.txt |
| T5 | toolchain fingerprint of blobs | layout of cosmic textarea | 1 | n/a | informative | Cosmic blob = 28 lines x 64 chars = `openssl enc -a` wrapping; CyberChef To Base64 never wraps and CyberChef AES has no OpenSSL 'Salted__'/EVP_BytesToKey output, so AES blobs came from openssl CLI (or compatible), not CyberChef | (inline check) |
| — | To Base 9 + any Substitute 0-8 -> a-i | — | — | — | skipped_exhausted | main loop subst_sweep.py covers all 9! maps on dbbi/res60/faed | — |

## Conclusions
- The Bifid step is fully consistent with CyberChef 'Bifid Cipher Decode' (full-length period, keyword square, J merged
  into I) using the ENTIRE dbbi string as keyword; textbook bifid gives byte-identical output, so the tool choice changes
  nothing. No other page string (incl. literal labels) as keyword, and no Encode direction, yields text.
- dCode's implementation is server-side (not fetchable); its bifid has an explicit period parameter, while the btcseed
  decode needs period = 570 (CyberChef's only mode) — weak evidence for CyberChef over dCode.
- CyberChef number-base recipes that emit only a..i (To Base 19+, To Charcode base 9) are ruled out by deterministic
  inverse or profile tests; To Base 9 + substitution is already exhausted by the main loop.
- METHOD WARNING for all lenses: scratch/quadgrams.pkl and scratch/quadgrams_clean.pkl both contain puzzle-derived
  strings (the btcseed decode appears 19x in the source transcript). Any scoring of puzzle-derived letter strings with
  them is inflated (here: fake z=+22). Use c37/construction_forensics/quad_indep.py (Carroll-only) or another clean corpus.
