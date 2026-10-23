# bifid_body lens (cycle 37): is the "btcseed" Bifid decode intended?

Setup: 5x5 square keyed by dbbi first-occurrence order (dbifhcegaklmnopqrstuvwxyz), period 570, Bifid decrypt of faed
gives 'btcseed' + 563 letters. faed uses only cells 0-8, so every even output letter is in {b,c,d,e}, and output digraph
(2j,2j+1) is a bijective function of the faed pair (faed[j], faed[j+285]). Only 81 of the 100 possible
(even x odd) digraphs can occur.

## Tests

| # | Hypothesis | Method | Size | Control | Result | File |
|---|---|---|---|---|---|---|
| P1 | The decode's prefix is unlikely to be an on-theme word by chance | Exact union probability over the prefix-minimal set of vocabulary strings that fit the forced pattern. Three nulls: iid (faed unigram), half-iid, exact multiset shuffle | 374k vocab strings (109 theme words, theme compounds of 1-3 words, 363k English words, BIP39, 2-word compounds), 6275 fit, 2669 minimal | Monte Carlo with 2e6 iid and 1e6 shuffle draws: shuffle 233 hits vs 230.9 expected; iid 431 vs 463+-21 (1.5 sd low). Planted check: real faed registers 'btcseed' | see the p-value table below | p1_vocab_pvalue.py, p1_results.json, p1.log |
| P3 | The dbbi cell order is special | Enumerate all 9! orders of a-i in cells 0-8 and decode a 16-letter prefix | 362,880 orders | Reproduces the community count: exactly 8 orders give btcseed, and dbbi is one of them | The only on-theme prefix over all 9! orders is btcseed (8 orders). The ALL tier hits 48 orders against 84 expected under iid, which is chance-level | p3_keyorders.py, p3_results.json |
| P4 | On-theme or English words are over-represented anywhere in the decode | Scan every offset of the real decode and of 1000 shuffled-faed decodes for theme words of 5+ letters, theme compounds of 7+, and English words of 8+ | 1000 nulls | Shuffle null | Real decode: 1 theme hit (btcseed at offset 0), **0 in the body**, 0 English words of 8+. Null mean is 0.01 hits per decode, so P(at least one theme hit anywhere) is about 0.008 | p4_anywhere.py, p4_results.json |
| P2 | The 563-letter body has structure beyond Bifid of a structureless faed | 13 statistics: odd-stream IoC and entropy, even-stream entropy, body IoC, number of distinct digraphs, largest digraph count, 9x9 chi2 of (faed[j], faed[j+285]), repeated 3-, 4- and 5-grams, maximum lag-match z over lags 1-60, odd-stream English quadgram score, odd-stream repeated 3-grams | 30,000 nulls for each of whole shuffle, half shuffle and iid | Planted English in the odd stream (20 plants, Bifid-encrypted, a-i verified) is detected at 100% by S1, S2, S7, S8, S12 and S13 | **All null-consistent.** Minimum p = 0.023 (even-stream entropy, whole shuffle), which drops to p = 0.19 under the half-shuffle null, so it comes from faed's known first-half/second-half composition shift. Bonferroni over 13 stats x 3 nulls gives 0.90. Pair chi2 = 57.0 vs null 64+-11 (p = 0.53). 75 of 81 digraphs used vs null 77.4+-1.7 | p2_structure.py, p2_results.json, p2.log |
| P5 | The detectors would catch a code-like payload | Plant 'btcseed' plus a body drawn uniformly from K of the 81 reachable digraphs; Bifid-encrypt; measure rejection at p<0.01 against the whole-shuffle null | K = 10, 16, 32, 58, 64, 81; 30 plants each | Same detectors as P2 | Any detector after Bonferroni rejects 100% of plants for K = 10, 16, 32, 58 and 64, and 90% for K = 81 (uniform digraphs conflict with faed's skewed unigram) | p5_code_controls.py, p5_results.json |
| (3) | Self-verifying decodes of the body | Not run: gated on structure, and none was found | - | - | Skipped by design | - |

### P1 p-values for the natural configuration (dbbi key, period 570, decrypt). Shuffle null; the iid null is about the same

| Event | Strings that fit | p, full string | p, first 7 letters match |
|---|---|---|---|
| exactly 'btcseed' | 1 | 4.4e-7 (half-iid 5.8e-7) | |
| one or two theme words (109 terms) | 43 fit / 14 minimal | 2.5e-6 | 8.8e-6 |
| one to three theme words | 34 minimal | 2.8e-6 | 2.1e-5 |
| any English word of 7+ letters (64k dictionary / 363k big list) | 46 / 137 | 8.2e-6 / 2.0e-5 | 2.5e-5 / 9.2e-5 |
| theme + English compounds | 1970 minimal | 1.5e-4 | 8.1e-4 |
| everything (374k strings) | 2669 minimal | 2.3e-4 | 1.1e-3 |

Other on-theme strings that fit equally well include 'encoded' (p 1.2e-6, more likely than btcseed), 'codebtc', 'decoded',
'btchere' and 'endseed'.

## Honest p-value

For the single most natural configuration, an on-theme prefix has **p of about 3e-6** (exact theme compounds of 1-3
words) to **2e-5** (counting a match on the first 7 letters). Two kinds of search widen this:
- Trying other configurations: multiply by K, the number of (key source, period, direction, input string) settings tried
  before btcseed was noticed. K is unknown; a value of 100-1000 is plausible for a community that tried many settings over
  years. That gives **p of about 3e-4 to 2e-2**.
- Looking at any position instead of only the start: an on-theme word somewhere in the decode has p of about 0.01 (P4).
  The prefix is the most visible spot, so this is an upper bracket.

So the prefix is surprising only if one configuration was tried, and roughly 1e-3 to 1e-2 once the search is counted.
That is not strong enough on its own.

## Verdict: btcseed is probably NOT intended

It is not refuted, and it is not actionable either way.
1. If it were intended, the creator would have had to write the plaintext so that every even letter is in {b,c,d,e} and
   every digraph lands in 81 reachable codes. That is a machine code built around this particular square, not text.
2. The body has no detectable structure on 13 statistics x 3 nulls, while code-like payloads from 10 to 64 symbols and
   English are detected 100% of the time (P2, P5). It is also free of any further theme or English words (P4).
3. The body's digraph statistics are exactly what you get from pairing independent faed letters. That includes faed's
   skewed unigram (g about double, which fits a uniform 10-digit source with one letter used twice). The "intended"
   model therefore needs a high-entropy payload that happens to reproduce a digit-like unigram. The simpler model is that
   faed is a digit-like a-i encoding and the Bifid reading is incidental; it explains everything without extra
   assumptions.
4. The creator was shown btcseed on 2026-03-03 and did not confirm. This is weak evidence.

## Next steps
- Pin down K from the 2025-06-11 chat log: how many Bifid keys, periods and inputs were tried before btcseed. That turns
  the per-configuration p into a global one. This is cheap and needs no compute.
- Stop decoding the btcseed body. The only form of the hypothesis that survives is "btcseed + high-entropy payload",
  and that cannot be decoded from within the page without an outside key.
- Put the effort into the digit-model provenance of faed (the doubled g and the change point at offset 538). See the
  faed_provenance lens.
