# Known pitfalls and prior investigations

## Forum claims are not confirmations

- Issue #108's claimed ciphertext corrections are already present in the live primary source and 2021-pinned walkthrough. Its MD5 output is reproducible but neither direct candidate matches the scoped addresses.
- Issues #104 and #111 explicitly retract the claimed 1327-byte Cosmic Duality/CADEIA chain foundation. Issue #111 also retracts its colored-grid “new bits” argument after using the documented spiral direction.
- Issue #109 links a purported solution; the discussion disputes it. Do not run third-party scripts that claim a solution without inspection and a target-match test.
- Issue #105 identifies the maintained fork with executable notebooks. The notebooks are archived here as data and have **not** been executed.

## Common invalid success criteria

- Most random 32-byte values fall inside the valid secp256k1 scalar range. Deriving an address from random bytes is not evidence that a puzzle layer decoded correctly.
- For uniformly random AES final plaintext blocks, valid PKCS#7 padding occurs with probability `sum(256**(-length), length=1..16)`, approximately **1/255**. This is why OpenSSL success can occur with a wrong password.
- Hashing an unverified output and later reproducing the same hash confirms only reproducibility, not creator intent.
- High entropy alone cannot disprove an encrypted binary intermediate step. The issue is the lack of independent structure, a justified derivation, or a target match.
- Arbitrary Base64 edits, byte slicing, XOR combinations, or made-up layer names do not gain validity merely from producing reproducible bytes.

## Previous finite dead ends to preserve

- Maintained `unverified/phase3.2_1141.md`: speech suffix beginning at 1141 and SHA-256 slice attempts reportedly found nothing. Treat this as a community negative result; inspect its actual tested range before repeating/extending it.
- Original grid colors lie at counterclockwise spiral positions 7,15,…,191: they encode the already-known URL's least significant bits. The single dominant near-white cell `(254,254,254)` at zero-based row 7/column 4 is an observed anomaly, **not** a proven hidden message.
- This session's 732-trial finite password experiment yielded only inconclusive padding hits. Keep the exact candidate-set hash and artifacts.

## Attribution limits

The saved July 2026 and older chat screenshots are dated/attributed by the maintainer; sender identity and dates were not independently authenticated by an original message export. Do not convert quoted speculation into “official” puzzle rules.

## Cycle 02 corrections to secondary claims

- PR #93's frequencies do **not** prove a cipher family, a key/payload relationship, or computational impossibility. Its broad negative conclusions exceed the evidence; inspect exact scripts/parameter spaces.
- Prime/color alignment is **not** a perfect unedited full match. Our exhaustive test finds 20/24 ordinary-color prefix, or 23/25 special-frame prefix with near-white=1, leaving two bits. The two complete prime-marker parses are retained; none was silently chosen as a confirmed solution.
- The conditioned 10000-shuffle null is reproducible; it is not the transcript's unverified “300 million shuffles” result and not a universal probability of accidental alignment.

## Cycle 03 evidence refinements

- Previous23/25 result applies to dbbi alone. A separately tested continuous-counter interpretation reaches into the intact binary clue: positions89/97 supply1/0 and complete25 events for mask1017/near-white=1. Do not rewrite the earlier result as erroneous or claim this proves a final key. The two new bits contribute limited evidence on top of the strong earlier prefix.
- The transcript's anomaly-axis deletion claim yields13x13 image sum89 and26 axis totals; independently reproduced. However, **23 of196** possible row/column deletions give89, and the reduced image has **8 yellows/13 blues**, not the original9/15. Numerical fit is not an independent decoding oracle.
- Cycle03 families overlap prior candidate sets:225234 ledger records represent220626 distinct target/KDF trials. Do not promote record count to a unique-space claim.

## Cycle 04 Bifid claim limits

- The archived btcseed output is reproducible with exact source key/period570 and matches full bytes. That establishes a transform, not an intended final stage. Simply quoting1/26^7 is wrong: coordinates, source-symbol multiset, fixed prefix and extensive post-selection matter.
- Fixed-key exact-multiset probability is4.41167743e-7; conditioning on observed faed firstfour letters gives0.000758644874, with7/10000 seeded control hits. Separate9! constrained-square control yields8 prefixes, including source key. None is a universal creator-intent probability.
- Even-offset bcde-only Bifid output is algebraically forced: input occupies firstnine square cells and period570 is even. It does not independently justify null-letter deletion, XOR, a second cipher or a seed encoding.
- Newly captured PR prime scripts use raw b-position/reset/gap hypotheses; they do not implement the independently reproduced b/be full-color scaffold. Joint checkerboard script contains duplicate-symbol alphabets and silent truncated-prefix handling; its reported negative space cannot prove exhaustive impossibility. Files preserved as secondary evidence, never executed.

## Current-state corrections — cycles 05–06

- A frozen plan's historical UNTESTED label is not authoritative evidence that it still needs execution. The cycle04 literal sum-list plan now has saved/audited5184 results; the cycle05 missing-cell plan has saved/audited3456 results. Repeating either creates no new evidence.
- Five23-event subsequence witnesses admit both prime branches. The continuous-counter25-event checkpoint remains conditional on its separate region/boundary rule; do not claim color matches alone prove L83 or L84.
- A new public fork's large negative search counts are secondary reports. Only exact locally reproduced families enter local cumulative totals. Its false-chain control/claimed Cosmic password is not a verified puzzle stage simply because a hash calculation agrees.
- New research outputs deliberately omit secret bytes/addresses and use local `TARGET_MATCH` Booleans. Existing historical evidence is retained; it is not uploaded, published or reclassified as recovered reward-key material.
