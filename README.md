# GSMG Bitcoin puzzle research

## Current checkpoint — cycle 36

Executing phase (2026-10-08). Hands-on testing replaced the non-executing audits: ~38k transposition/key candidates on `faed` scored with a validated serial-structure detector, a calibrated column-permutation hill-climb (widths 5–40), 7.7M sha256 password forms (colour-prime sum lists, roadmap-token concatenations, phrase batteries), 339 hidden-door URL probes and 178 hidden-form submissions. All negative. New verified facts: live-site behaviour, the original 2019 puzzle page text (`GSMG MEGANIGMA || 5 BTC`, alt `Follow the white rabbit`), the QR content, dbbi's 15/10 `b`/`be` colour counts and the 16/7 marker split matching the speech numbers, faed's i.i.d. statistics, the Phase 1 song's phase structure, and the Keymaker's last lines. Findings: `research/artifacts/cycle36/findings.md`; scripts in `scratch/`.

```bash
python3 scratch/common.py            # parses SalPhaseIon, verifies decodes, exposes AES/KDF oracle
python3 scratch/exp05_prime_seg.py   # dbbi prime segmentation + shuffle null
python3 scratch/exp14_lags.py        # faed lag mutual information vs controls
```

## Current checkpoint — cycle 35

The receiver audit finds no recovered object that independently consumes a `matrixsumlist` output. There is no exact14-item object. The original grid is upstream, while FAED/Bifid expose15-column geometry without a14-value input contract or an authored operation; Bifid's real inputs are already FAED and the dbbi-derived square. Generic SHA/password APIs are variable-length but non-discriminating. `lastwordsbeforearchichoice` remains the strongest semantic successor from mention order, with its source, boundary, count and mapping all unknown. The independently specified-receiver hypothesis is **REJECTED**; the actual consumer remains **UNKNOWN**. Findings: `research/artifacts/cycle35/findings.md`.

```bash
python3 -m tools.matrixsumlist_receiver_audit
python3 -m unittest tests.test_matrixsumlist_receiver_audit -v
```

## Preserved checkpoint — cycle 34

The requested wording/formatting audit found no explicit source binding for the `matrixsumlist` cell domain, numeric interpretation, or axis. Across411 creator-attributed messages, the relevant records contain no cell/pixel/grid/row/column/axis language. The color hint says only that Yellow and Blue each have a number and points to the first piece; prime hints establish relevance without defining values or positions. Even the authored `R=18,A=1,B=2` notation does not bind B/Y as matrix weights. Primary and official-hint formatting supply concatenated order without verbs or argument syntax. **Seven focused tests pass.** Findings: `research/artifacts/cycle34/findings.md`.

```bash
python3 -m tools.matrixsumlist_wording_audit
python3 -m unittest tests.test_matrixsumlist_wording_audit -v
```

## Preserved checkpoint — cycle 33

The original-matrix audit now separates source facts from the proposed `matrixsumlist` operation. The PNG fixes the oriented14×14 grid and24 yellow/blue cells, one terminal cell per decoded URL byte. Exhausting all32 per-color binary assignments shows that blue=1/yellow=0 is uniquely fixed for the earlier URL decode. The source does not say to sum only those cells, does not bind encoding bits as arithmetic weights, and does not choose rows or columns. The full25-event prime correspondence remains conditional on the unmentioned near-white cell being semantic1, mask1017 and counter continuation into the binary label. **Seven focused tests pass; zero cryptographic material was generated.** Findings: `research/artifacts/cycle33/findings.md`.

```bash
python3 -m tools.original_matrix_audit
python3 -m unittest tests.test_original_matrix_audit -v
```

## Preserved checkpoint — cycle 32

A bounded receiver audit closes the only apparent internal15-slot match. None of the14 frozen recovered objects has size15. The image does contain15 blue events, but they are exactly the terminal-one bits of the previously decoded24-byte URL and occupy only10 distinct image columns; pairing their ordinal with Bifid columns would add an unauthored rule. The direct blue-event receiver is **REJECTED**. BIP39 remains only an external dimensional match, with no source binding. **Six focused tests pass; zero numeric or cryptographic material was generated.** Findings: `research/artifacts/cycle32/findings.md`.

```bash
python3 -m tools.fifteen_receiver_audit
python3 -m unittest tests.test_fifteen_receiver_audit -v
```

## Preserved checkpoint — cycle 31

The shared width15 is now separated from actual data flow. Every paired Bifid group depends locally on FAED column `c` and globally on the same `dbbi`-derived square. Zero groups depend exclusively on the corresponding column of the inferred upstream `dbbi|matrixsumlist-bits` panel, and the eight raw label-bit columns are not Bifid inputs. The direct upstream-panel→Bifid column edge is **REJECTED**. The surviving missing edge is semantic: decoded `matrixsumlist` may instruct an operation on the paired Bifid planes, but neither the operation nor receiver is specified. **Six focused tests pass; zero numeric or cryptographic material was generated.** Findings: `research/artifacts/cycle31/findings.md`.

```bash
python3 -m tools.matrix_bifid_dependency_join
python3 -m unittest tests.test_matrix_bifid_dependency_join -v
```

## Preserved checkpoint — cycle 30

The post-Bifid axis is now structurally resolved. Treating the serialized output as `38×15` makes every column mix two FAED source columns. Pairing corresponding columns of Bifid's natural even/odd `19×15` coordinate planes instead gives15 complete38-symbol groups, each preserving exactly one FAED column through all285 Bifid cells. Formal letter-count comparisons show zero group matches against either previously tested raw-FAED15-item layout, so this is not an exact repeat of that campaign. The remaining missing edge is `matrixsumlist semantics + paired Bifid-plane columns → unknown15-item receiver`. **Six focused tests pass; zero numeric sums or cryptographic material were generated.** Findings: `research/artifacts/cycle30/findings.md`.

```bash
python3 -m tools.bifid_sum_axis_topology
python3 -m unittest tests.test_bifid_sum_axis_topology -v
```

## Preserved checkpoint — cycle 29

The missing data-flow edge is now narrowed to a possible join of the two unknown exits: decoded `matrixsumlist` semantics may act on the recovered `38×15` Bifid output, reducing it to15 column items. Fifteen is an allowed BIP39 word count, while cycle28 rejected the literal Bifid text as an already serialized seed. The preserved raw-FAED BIP39 script did not test this post-Bifid operand. This is only dimensional compatibility: all nine canonical symbol maps fit the BIP39 index range by bounds, so no mapping is selected. **Five focused tests pass; zero values, mnemonic words, checksums, seeds, private keys, or AES operations were generated.** Findings: `research/artifacts/cycle29/findings.md`.

```bash
python3 -m tools.bifid_sumlist_bip39_preflight
python3 -m unittest tests.test_bifid_sumlist_bip39_preflight -v
```

Further discrimination would require an authored numeric mapping or receiver. Concrete mnemonic/checksum execution is outside the active phase.

## Preserved checkpoint — cycle 28

A direct-format check using the official BIP39 and BIP32 structural contracts rejects `btcseed`, body563, and full Bifid570 as already serialized standard seed objects. They are single unseparated tokens of7/563/570 ASCII bytes; BIP39 requires12/15/18/21/24 words and BIP32 accepts16–64 seed bytes. Any seed interpretation therefore needs an authored codec, segmentation, or extraction rule. **Six focused tests pass.** Findings: `research/artifacts/cycle28/findings.md`.

## Preserved checkpoint — cycle 27

The latest non-executing test distinguishes serial and convergent architectures. `residual60` plus23 event labels reconstructs `dbbi91`, which deterministically supplies the Bifid square; `faed570` independently supplies the Bifid text. The branches converge at Bifid, so a direct `residual60 → faed570` conversion is not required. The tempting `residual60=4×15` reshape has no exact downstream substring/row identity and preserves no width15 source axis. The remaining missing interfaces are `matrixsumlist` semantics → consumer and full Bifid570 → receiver. **Six focused tests pass.** Findings: `research/artifacts/cycle27/findings.md`.

```bash
python3 -m tools.residual_faed_topology
python3 -m unittest tests.test_residual_faed_topology -v
```

## Preserved checkpoint — cycle 26

The remaining direct-field hypothesis is now rejected. In the rendered `38×15` Bifid output, the first `7|8` cut gives `btcseed|deoemcke`, but it bisects one Bifid digraph: both fields depend on FAED pair3 at offsets3 and288. Across all38 rows the same cut splits19 digraphs and falls between19, while neither natural19×15 coordinate plane begins with `btcseed`. Width15 remains an exact tiling; it is not a field-preserving data-flow edge. **Five focused tests pass.** Current findings: `research/artifacts/cycle26/findings.md`.

```bash
python3 -m tools.bifid_field_boundary
python3 -m unittest tests.test_bifid_field_boundary -v
```

Further structural execution requires an authored cross-field operation and downstream receiver.

## Preserved checkpoint — cycle 25

The non-executing follow-up corrects cycle24's strongest interpretation. Its15 values are two fields on different scales: seven `dbbi` rank sums and eight raw-label bit counts. A bounded test compared that vector with36 canonical coordinate marginals from the fixed FAED/Bifid width15 representations, using both coordinate origins. There are zero ordered or reorder-only matches, while four Bifid conservation controls pass. The direct downstream marginal edge is **REJECTED**; the exact `7|8` geometry survives, but its consumer remains unknown. **Six focused tests pass.** Current findings: `research/artifacts/cycle25/findings.md`.

```bash
python3 -m tools.matrix_marginal_identity
python3 -m unittest tests.test_matrix_marginal_identity -v
```

No AES, encrypted-blob test, candidate generation, private-key operation, or network request is part of this phase. Further execution requires a source-backed target, action, and normalization.

## Preserved checkpoint — cycle 24

The active phase is non-executing structural analysis. Cycle24 identifies a previously unrecorded width15 interface across the public objects: `dbbi91 = 13×7`, the raw `matrixsumlist` encoding is `13×8`, their rowwise join is `13×15`, and `faed570 = 38×15 = 2×19×15`. All285 full-period Bifid digraphs reproduce as a cellwise fold of the two19×15 FAED panels. In the corresponding38×15 output view, `btcseed` fills the first7-cell field and the former body563 is exactly `8 + 37×15`. The fixed mixed-type panel then yields one15-value sum list aligned with every downstream15-column representation; the opposite13-value direction matches no downstream axis. Direct permutation, selection, partition, and text readings all fail their target domains, leaving the downstream action genuinely unspecified. **Sixteen focused tests pass.** Current findings: `research/artifacts/cycle24/findings.md`.

```bash
python3 -m tools.matrix_width_interface
python3 -m tools.matrix_sum_interface
python3 -m tools.matrix_operator_feasibility
python3 -m unittest tests.test_matrix_width_interface tests.test_matrix_sum_interface tests.test_matrix_operator_feasibility -v
```

No password/private-key candidates, AES operations, encrypted-blob tests, or cryptographic searches are part of this phase. The next structural step requires an authored axis and operand binding for `matrixsumlist`; arbitrary sums would repeat prior families.

## Preserved checkpoint — cycle 23

The verified outer decoding pipeline remains reproducible, but no private key matching the advertised address has been recovered. Cycle 23 closes three narrow questions: direct 14×14 event coordinates do not index the 5×5 Bifid square; the frozen residual60 plus the first 23 event labels exactly reconstructs all 83 logical tokens, the original 91 letters, and the fixed square; and the exact sentence `One for one, four for one.` fails as bounded password material. The latter tested 36 previously untested forms in 216 AES/KDF trials, with no structural plaintext or target match. **14 focused and 359 full-suite tests pass.** Current findings: `research/artifacts/cycle23/findings.md`.

```bash
python3 -m tools.gsmg reproduce
python3 -m tools.coordinate_interface
python3 -m tools.residual_frame_join
python3 -m tools.last_words_literal audit
python3 -m unittest tests.test_coordinate_interface tests.test_residual_frame_join tests.test_last_words_literal -v
python3 -m unittest discover -s tests -v
```

The next useful step must bind the ordered 25 event identities to a source-authored selector or permutation with a named consumer. Equal list lengths alone are insufficient. Do not expand the rejected literal sentence into casing/spacing brute force, rerun completed password families, or search arbitrary private-key space. All verification remains local; no transaction is signed or broadcast.

## Preserved checkpoint — cycle 08

The requested literal-sum-list path and later missing-cell/numeric routes are completed negatives, not outstanding work. Current instruction-order audit,18-trial residual-keyword negative, prime-conditioned Bifid controls and exact baseline-inclusive overlap accounting are in `research/progress.md`. No final target recovered. **80 tests pass**.

```bash
python3 -m tools.baseline_coverage
python3 -m tools.instruction_order
python3 -m tools.prime_bifid_controls
python3 -m tools.secret_safe_aes audit --family residual-bifid
python3 -m tools.audit_cycle08
python3 -m unittest discover -s tests -v
```

Current work is strictly offline; do not refresh sources or rerun completed searches. Candidate/key/plaintext material remains local; new outcomes use fingerprints and Boolean verification. Frozen next operation-order experiment: `research/artifacts/cycle08/next-post-bifid-routing-plan.json`,46 new passwords/276 prospective AES trials, not executed.

Evidence-first local investigation of the publicly advertised GSMG puzzle. **The puzzle is not solved by this workspace.** No private key matching the advertised target has been recovered, and no transaction has been signed or broadcast.

## Start here

- `research/scope.md`: target, source provenance, current snapshot balances, and limits.
- `research/architecture.md`: reconstructed stages and confirmed decoding path.
- `research/attack-surface.md`: small, prioritized unsolved research tasks.
- `research/hypotheses.md`: hypotheses, tests, evidence, and statuses.
- `research/known-issues.md`: misleading claims and already-explored dead ends.
- `research/test-results.md`: commands, observed results, and limitations.
- `research/log.md`: session history; continue this before starting new work.
- `research/sources/manifest.json`: public-source URLs, retrieval timestamps, sizes, and SHA-256 hashes.

## Toolchain

Use **Python** for this investigation: image extraction, text/number transforms, finite candidate generation, and reproducible experiments. PyCryptodome provides AES, `hashlib` provides hashes, Pillow reads the original PNG, and cryptography verifies secp256k1 public keys. OpenSSL independently checks the legacy KDF. FFmpeg reproduces the audio spectrogram.

The available host has Python 3.12.3, four logical CPU threads, and approximately 5.7 GiB RAM. No NVIDIA GPU, Hashcat, or John executable was detected. No paid infrastructure or new system packages were installed.

Rust/C++ and GPU tools are optional **later**, only after a justified finite candidate space and correctness oracle exist. This puzzle is not a known restricted-range Bitcoin key search. Arbitrary 256-bit private-key brute force is not the research plan.

## Run locally

The required Python libraries are already available on the current host. For a separate environment, use Python 3.12 and install `requirements.txt` in a virtual environment. FFmpeg/OpenSSL are separate system tools.

```bash
python3 tools/gsmg.py reproduce
python3 tools/gsmg.py search
python3 tools/gsmg.py audio
python3 -m unittest discover -s tests -v
```

These commands use saved inputs, produce artifacts under `research/artifacts/`, and make no network requests. `search` is a short, finite clue-based experiment, not an open-ended cracking job. Padding-valid output is recorded as **INCONCLUSIVE**, never treated as proof of success.

To refresh the initial public sources separately:

```bash
python3 tools/collect_sources.py --initial
```

The collector makes only public HTTPS GET requests. Existing changed snapshots are retained under content-hash filenames. The source collection includes copyrighted third-party material for local research; do not publish the whole cache without checking licenses. GitHub notebooks were saved as evidence, **not executed**.

## Success criterion

A final candidate must have a source-grounded derivation, be a valid secp256k1 scalar, and produce the advertised address under the relevant public-key serialization. A valid-looking WIF, valid PKCS#7 padding, a self-published output hash, or an arbitrary valid Bitcoin address is insufficient. Keep any recovered reward key out of public logs. No production transaction is needed to prove the address match.

## Continued research

Cycle 02 results and strongest remaining hypothesis: `research/progress.md`. Exact parameter map: `research/pipeline.md`. Append-only hypothesis ledger: `research/candidates.jsonl`. Original sources remain unchanged; newly captured linked PR material lives under `research/evidence/cycle02/`.

```bash
python3 -m tools.analyze_salphaseion
python3 -m tools.prime_markers --shuffles 10000
python3 -m tools.audit_cycle
python3 -m tools.verify_btc
python3 -m unittest discover -s tests -v
```

Cycle 02 finite search modules have separate `plan` and `run` commands: `tools.derive_inner_aes`, `tools.salphaseion_experiments`, `tools.joint_derivation`, `tools.prime_gap_sums`, `tools.paired_digit_derivation`, `tools.residual_coordinates`. Detailed existing ledgers are preserved rather than overwritten; use the audit command to reproduce completed results. That cycle's prime/color scaffold is **partial**, not a claimed solution. `python3 -m tools.plan_zeroed_residual` regenerates the historical zeroing plan; its later execution is recorded separately in cycle 03.

## Cycle 03 checkpoint

The historical zeroing plan is now executed. Continuing the prime index into the intact binary clue completes all25 special-color events for one explicit branch; this is **structural evidence, not a final key**. Current results and exact next experiment are at `research/progress.md`.

```bash
python3 -m tools.prime_boundary
python3 -m tools.audit_cycle03
python3 -m unittest discover -s tests -v
```

`tools.zeroed_residual` runs/audits frozen source-derived plans; `tools.image_sum_derivation` has separate plan/run commands. Existing ledgers are intentionally not rerun/overwritten. The ranked-alphabet plan shown here is executed in cycle04; its historical plan remains unchanged. Original source files remain unchanged; no network transactions.

## Cycle 04 checkpoint

Source-keyed Bifid reproduces the archived btcseed prefix/full output but not a validated next stage. Conditional probability controls and forced parity constraints prevent treating that prefix as final proof. Ranked-alphabet, Bifid material and bounded paired-hash trials all fail the downstream gate.

```bash
python3 -m tools.audit_cycle04
python3 -m tools.bifid_evidence --shuffles 10000
python3 -m tools.bifid_square_controls
python3 -m unittest discover -s tests -v
```

`tools.zeroed_residual` supports `--family ranked`, `bifid` and `composition` audits. Binary-format results reproduce through `python3 -m tools.audit_binary_key_pairs audit --group ranked` (also `bifid`/`composition`). `python3 -m tools.plan_literal_sumlist` regenerates the next **UNTESTED** plan only. Current results/next step: `research/progress.md`.

## Current checkpoint — cycle 06

The historical literal sum-list plan **has executed**:5184 trials/17 padding hits/no validated output. The later actual-anomaly-hole/axis-sum construction also fails:3456 new trials/13 hits/no recognized structure, `TARGET_MATCH=false`. Do not relaunch either from its creation-time UNTESTED plan label.

```bash
python3 -m tools.secret_safe_aes audit
python3 -m tools.audit_cycle06
python3 -m unittest discover -s tests -v
```

Current work is offline saved-artifact analysis only. New runner results retain transformation provenance, crypto/plaintext fingerprints, structure scores and local Boolean verification, not secret key/plaintext bytes or candidate addresses. No wallet/RPC/mempool access or transaction operations. Current findings and next numeric-routing direction: `research/progress.md`.

## Current checkpoint — cycle 07

Numeric image-sum column routing, optionally before the exact source-keyed Bifid, is also completed:414 new passwords/2484 AES trials/9 padding hits/no structures/`TARGET_MATCH=false`. It does not validate the `btcseed` prefix as a decoded answer. Current totals and the remaining instruction-order derivation gap are in `research/progress.md`.

```bash
python3 -m tools.secret_safe_aes audit --family numeric-routing
python3 -m tools.audit_cycle07
python3 -m unittest discover -s tests -v
```

Completed ledgers are preserved; `run` refuses to overwrite them. No arbitrary private-key range or password dictionary search is introduced.
