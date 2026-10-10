# GSMG Architectural Reconstruction v1

2026-10-01. **STATUS: UNSOLVED.** This is an architectural reset, not a new password or cipher search. Existing results are authoritative as reproducible transformations, not proof of intended construction. Analysis remains offline and limited to public source text, images, encoded objects and metadata. The terminal object is uninstantiated and outside this analysis.

Current machine-readable report: `architecture-reconstruction-v3.json`; first two snapshots preserved. Mathematical counterexample: `sumlist-information.json`. Reproduce with `python3 -m tools.architecture_reconstruction` and `python3 -m tools.sumlist_information`.

## A. Verified pipeline

The proposed single serial chain is **not established**. The known graph branches:

```text
original PNG14x14
  |-- verified192-bit ASCII +4-bit tail -> source route
  |      -> hidden form [existence verified; acceptance only documented]
  |      -> Phase2 envelope ->648-byte instructions
  |      -> Phase3 envelope ->4090-byte instructions
  |      -> Phase3.2 outer envelope ->2422-byte raw plaintext
  |                   |-- paragraph2 encoded1539 -> CP273/Beaufort -> speech1539
  |                   |-- paragraph3 digits149 -> checkerboard -> public text91
  |                   |-- paragraph4 alphabet clue145
  |                   `-- paragraph5 Base64 -> inner envelope96 [unresolved]
  |
  `--25 ordered special-event tuples [24 octets +extra near-white event]
          <-> conditional prime-marker correspondence in SalPhaseIon

preserved audio difference/spectrogram -> HASHTHETEXT [argument unknown]
  -> documented original-source text entry -> SalPhaseIon/Cosmic source

SalPhaseIon first textarea1075
  |--dbbi91 + binary104
  |      |--conditional prime parse ->23 dbbi markers +2 binary-label markers
  |      |--complement ->residual60
  |      `--binary104 ->matrixsumlist label [operand/operator unknown]
  |--raw dbbi91 ->first-occurrence square25
  |      +faed570 ->full-period Bifid570 [exact inverse verified]
  |                     |--recognized prefix7 [community-selected cut]
  |                     `--body563 [no known fixed-size consumer]
  `--lastwords / thispassword / first-shabef / container / answer-shabef
         ->conditional local hash-input ->SMALL ->answer-hash skeleton
           [all operand and destination assignments unresolved]

Cosmic: separate heading / separate envelope [unresolved]
```

There is no verified speech→prime parsing, matrixsumlist→dbbi derivation, residual→Bifid input, Bifid→inner input, SMALL→inner or answer-hash→Cosmic edge. Physical adjacency and hint mention order are not execution edges.

The frozen February23 2023 decoded hint supports **prime/color → matrixsumlist → Architect last words → yin-yang** as mention order. Locally, the primary first-shabef/container/answer-shabef sequence supports a conditional hash/input→container→answer-hash skeleton. These are the strongest ordering constraints, but no source-bound edge joins them into a complete graph.

Earlier AES stages use AES256/CBC, legacy EVP_BytesToKey/SHA256 and PKCS7, producing byte-identical archived fixtures. These are frozen controls; not decrypted again here. Server form acceptance is not independently reproduced by the local cryptographic chain. The separate audio entry is documented, not re-entered externally.

## B. Object inventory

Exact bytes stay in their existing public fixtures. JSON records supply fingerprints, full alphabets and mapped spans; no candidate input or sensitive terminal object is generated. Creator-authenticated means independently authenticated authorship, not a transcript label: **none of these sources has a preserved creator signature**. P denotes primary source content, D reproducible derivation, C community interpretation. These are separate from intended-role confidence.

| Object | Size / alphabet / encoding | Exact source locator | Derivation and upstream | Known consumer / unexplained information |
|---|---|---|---|---|
| Original grid |196 cells; five color classes |`research/sources/gsmg-puzzle.png` |P; frozen original traversal |ASCII route verified; full event metadata retained |
| Phase2 plaintext |648 raw bytes |`research/artifacts/phase2.txt` |D; earlier salted envelope |Local seven-part entry recipe; no later carry assignment |
| Phase3 plaintext |4090 raw bytes |`research/artifacts/phase3.txt` |D; earlier entry recipe/envelope |Outer Phase3.2 envelope; not a global door numbering |
| Outer plaintext |2422 raw bytes |`research/artifacts/phase32.txt` |D; earlier entry recipe/envelope |Six separately authored paragraph objects |
| dbbi |91 letters; a–i |SalPhaseIon line17, compact[0:91], source characters[456:637] |P; exact slice |Prime parse and square derivation; repeated order not explained by square alone |
| Matrix clue |104 a/b symbols,104 bits,13 ASCII octets |line17, compact[91:195] |P/D; a=0,b=1 |Decoded label and two continued markers; no implicit104-cell matrix |
| matrixsumlist |13 letters |same104 source symbols |D; fixed ASCII decoding |Label/operation/metadata unresolved; does not instantiate a list |
| Event frame |25 tuples; row/column/color/spiral/octet/bit |frozen cycle15 event map |D; original image +conditional marker correspondence |Alignment control;25 bits are not the full event information |
| Prime complement |60 letters; a–i |cycle10 mask1017 residual source map |D; nonprime tokens of dbbi |No verified consumer; alternate61 branch remains preserved |
| faed |570 letters; a–i |line17, compact[195:765], source characters[846:1985] |P; exact slice |Frozen Bifid transform; intended role unknown |
| Bifid square |25 letters, i/j merged; `dbifhcegaklmnopqrstuvwxyz` |cycle10 keyword-first-occurrence map |D/C; raw dbbi first occurrences +conventional alphabet completion |Frozen Bifid; loses keyword multiplicity/later ordering |
| Bifid full |570 letters; 25-letter alphabet |`research/artifacts/cycle04/bifid-evidence.json` |D/C; square25 +faed570 +period570 |Exact inverse verified; no next-input assignment |
| Recognized prefix |7 letters |same object[0:7] |C; recognition of `btcseed` |No independently assigned technical input/output role |
| Bifid body |563 letters; same25-letter alphabet |same object[7:570] |C; recognized cut only |No same-length peer or authored consumer; variable-length inputs still possible |
| Edited speech |1539 lowercase letters; a–z |`research/artifacts/phase32-beaufort.txt:1` |D; raw paragraph2 bytes[447:1986] +fixed CP273/Beaufort |Mapped selection/reinsertion references; source/count unknown |
| Checkerboard |149 decimal digits |raw paragraph3 bytes[1990:2139] |P; exact outer plaintext paragraph |Frozen prefix code decodes91 public letters |
| Checkerboard output |91 letters;21 observed symbols |`research/artifacts/phase32-checkerboard.txt:1` |D; frozen observed codebook |A public narrative instruction, not dbbi despite equal length |
| SMALL |128 Base64 characters;96-byte envelope;80 ciphertext |line17, compact[895:959]+[999:1063] |P/D; join64+64, exclude separate enter40 |Unresolved envelope; SMALL itself is a secondary label |
| Inner envelope |128 Base64 characters;96-byte envelope;80 ciphertext |raw paragraph5 bytes[2292:2422] |P/D; whitespace-only wrapping removal |Unresolved; distinct from SMALL despite equal size |
| Cosmic envelope |1792 Base64 characters;1344 bytes;1328 ciphertext |SalPhaseIon line20 |P/D; second textarea |Unresolved separate object; destination not confirmed |
| HASHTHETEXT |11 ASCII letters |frozen cycle10 spectrogram/audio map |D; preserved audio difference/hex transcription |Command identified, argument still unknown |
| first/answer SHA descriptors |first-command35;answer-command12; operators6 each |compact[860:895]/[1063:1075] |P/D; suffix bef→256 locally |Recognizable SHA operation; no selected object/representation |
| Instantiated SHA argument/result |UNKNOWN |none for unresolved construction |Uninstantiated |32-byte digest,64-character hex and KDF password are different typed nodes |
| Terminal object |UNKNOWN |none recovered |Uninstantiated; outside current analysis |No recovery or verification attempted |

## C. Dependency and information-flow graph

| Transform / edge | Information preserved | Information lost / absent |
|---|---|---|
| Raw slice/source map |Every source character and position |No loss; role not automatically assigned |
| Binary104→ASCII13 |All104 bits under fixed a/b/MSB convention |No bit loss; label-only view omits continued-marker interpretation |
| dbbi→first-occurrence square |First occurrence order of nine observed letters; conventional completion |91-letter multiplicity and most later order; not reversible alone |
| Prime split |Residual60 +23 marker tokens +frozen positions reconstruct91 raw letters |Residual alone omits31 raw characters;60+23=83 logical tokens, not91 raw symbols |
| Full Bifid |All1140 row/column source coordinates;570 output letters |No loss with square/period; split prefix is not a proof of intended encryption |
| Prefix recognition |14 coordinates supporting7 letters |1126 body coordinates excluded by projection; no authored discard |
| Speech substitution/Beaufort |Observed1539 symbols and frozen inverse mapping |No loss under known alphabet/key; word segmentation/selection still inferred |
| Checkerboard |149 digits↔91 letters under fixed observed prefix code |Neither encoding nor equal91 size creates dbbi identity |
| Row/column sums |Marginal totals |Interior arrangements and original-source order are generally lost |
| Hash |Fixed32-byte result for a selected byte input |Non-reversible; accepts arbitrary input lengths; cannot identify its argument by size |
| Envelope parsing |Header8/salt8/ciphertext partition and exact bytes |Does not encode cipher mode, key length, digest, IV or plaintext type |

**New mathematical result:** even *both* original axis-sum vectors plus all25 fixed event tuples fail to determine the matrix uniquely. There are657 existing non-event alternating2×2 rectangles among8281 source-coordinate rectangles. A four-cell signed balance certificate preserves every row/column sum and all event values/coordinates/identities while allowing a distinct assignment of ordinary binary cells. No altered image, matrix or trial string was created. This rejects a direct lossless sums+frame codec, not a metadata/selector role or additional constraints.

## D. Unknown interfaces and the inner-envelope contract

Distinguish the **known encrypted-data input** from the **unknown password/KDF input**. The former is exactly the Base64 of outer plaintext paragraph5, not Bifid output.

| Parameter | Classification | Evidence / missing interface |
|---|---|---|
| Source/encrypted input |VERIFIED |Exact raw paragraph5 canonical bytes equal inner fixture |
| Base64 / Salted header |VERIFIED |128 chars→96 bytes; `Salted__`8 +salt8 +ciphertext80 |
| Salt |VERIFIED |`b45a5e3d827593ca`, exact header bytes |
| Ciphertext |VERIFIED |80 bytes /5 blocks; exact fingerprint in JSON |
| AES256/CBC |STRONGLY SUPPORTED, not verified for inner |Earlier three verified layers share it; envelope does not encode it |
| Legacy EVP_BytesToKey |STRONGLY SUPPORTED |Earlier layers; no inner plaintext validates it |
| KDF SHA256 digest |STRONGLY SUPPORTED |Earlier layers use SHA256; MD5 alternate coverage does not validate MD5 |
| Exact password bytes |UNKNOWN |No source-bound argument/serialization assignment |
| Password64-hex versus raw digest32 |WEAKLY SUPPORTED precedent versus UNKNOWN choice |Earlier layers use hex as password, not direct AES key |
| KDF formula under that model |CONDITIONAL |`D_i=SHA256(D_(i-1)||P||salt)`, concatenate to48 bytes; key32 +IV16 |
| Iterations |UNKNOWN inner; conditional legacy count1 |Do not promote prior-layer convention into verified inner parameter |
| IV |UNKNOWN |Derived only after password/KDF known; not separately present in envelope |
| PKCS7 |STRONGLY SUPPORTED |Earlier layers; under CBC this implies plaintext length64..79 |
| Expected plaintext schema |UNKNOWN |Five ciphertext blocks do not define a payload type |
| Bifid/residual→password input |UNKNOWN |Hash/password APIs accept variable lengths; dimension compatibility alone cannot choose input |
| SMALL→inner or answer→Cosmic |UNKNOWN |Distinct objects; both directions remain speculative |

Both small envelopes have the same sizes but different salts, blob bytes and ciphertext fingerprints. This rejects identical-container hypotheses only; it does **not** reject identical plaintexts encrypted under different parameters.

## E. Strongest structural evidence and dimensional controls

- Exact570→570 reversible Bifid is the strongest complete mathematical transform in the unresolved branch. Period570 was selected as full ciphertext length by community recipe, not independently specified by an author command. Output length570 follows from one output letter per coordinate pair: it is not a separate clue.
- Prefix7 uses source positions0..3/285..288. Frozen dependency map shows source symbols3 and288 split across the seven-letter cut: the cut retains their row coordinates and leaves their column coordinates for output7. No primary delimiter or full-period block boundary selects7.
- Eight exact full-output references are mapped. Detailed June11/June25 Sycorax bodies are identical reposts1167552 seconds apart, not independent discoveries. June11 line122258 explicitly says rest to be solved, without a consumer. Discovery caveat remains intact. A June15 community rewrite replaces dbbi+binary104+faed with Bifid570 and omits matrixsumlist: **that presentation is not the primary puzzle layout**. Earlier C10 already located June11 discovery; the present work adds full-object/referral/boundary accounting, not a new discovery date claim.
- dbbi91−31 raw prime-marker characters=60 residual; at token level83−23=60. Eight `be` tokens are two-character markers. Frame25=23 dbbi prime markers+2 markers borrowed from the intact binary label. The near-white semantic bit remains an assumption and the last two markers do not independently select the residual branch.
- Original grid14×14=196; dbbi91+binary104=195 was already tested as missing-cell construction. Do not reopen it because its equation is attractive.
- Binary104=13×8 exactly explains its ASCII label; it does not describe the original196-cell matrix. 25 event tuples and25 square positions differ in type/domain and are not automatically a permutation.
- 570=2×285=19×30;563 is prime. 1539=19×81;ratio1539:570=27:10. These factorizations supply no source-defined reshape, alignment or reversible consumer.
- No known fixed-size public object equals563. This rules out direct same-length identities only; variable-length hashing/password/encoding remain possible but unconstrained.
- Exact repeated-tile construction fails all15 proper-divisor tile lengths for full570 and the one proper divisor for563. This is not a statistical autocorrelation analysis or a new cipher-period search. Forced even-position alphabet/parity and prior conditional statistical controls are reused unchanged.

## F. Failed interpretations: do not repeat

These are finite negative families, not global cipher exclusions. Reopen only with **new source evidence that changes a specific edge/parameter**, checking exact previous identities first.

| Frozen family | Existing coverage / why closed |
|---|---|
| Direct full/suffix/parity Bifid passphrases |C04 six materials,324 AES trials; no justified structure |
| First-hint/answer hash compositions |C04 fixed120 forms/720 prospective trials; ledger results already preserved |
| Literal image-axis sums |C05 24 lists×4 representations×3 compositions,864 passwords/5184 trials |
| Coordinate/parity rails |C05 two rails/fixed serializations,84 passwords/504 trials |
| Missing-cell placement |C06 576 passwords/3456 new trials;195→196 placement already closed |
| Numeric routing before/around Bifid |C07 24 axis lists,414 passwords/2484 trials |
| Prime residual as Bifid square keyword |C08 one distinct square/18 trials; not a new independent architecture |
| Post-Bifid numeric routing of body |C09 46 passwords/276 trials; seven-letter preserved-header assumption already tested |
| Spiral ring sums |C09 432 trials; original complete rings retained |
| Direct residual/sumlist codec identity |C09 600 exact comparisons; no identity |
| Complementary masked missing-cell sums |C10 fixed family executed; no justified downstream result |
| Source/selection/word-number variants already mapped |Cycles10–21 frozen controls; do not rerun to inflate evidence |

This cycle runs zero AES/KDF/password trials. Earlier public-object score/parity/null controls are not recomputed.

## G. Five competing architectures

| ID / architecture | Central disputed edge | Supporting evidence | Evidence against / unknown |
|---|---|---|---|
| C22-ARCH-SERIAL |Bifid570→specified matrix transform→local hash/container |Exact reversible full object; nearby instruction syntax |No matrix transform/input binding; tested direct/routed material negative; inner destination unbound |
| C22-ARCH-COORDINATE |25 event/prime tuples→typed coordinate metadata; Bifid parallel |Exact cross-source correspondence, metadata fits label semantics |Image14×14 versus square5×5;25 binary labels not alphabet; direct sums+frame are lossy |
| C22-ARCH-SPEECH-SELECTOR |Matrix metadata→exact speech selection→thispassword/SMALL |Named Architect-related selection and local label grammar |No exact selector/count/choice boundary; Bifid body role unexplained |
| C22-ARCH-MULTIDOOR |Independent inner and SMALL outputs→later convergence or separate continuation |Two distinct sources/envelopes; original multi-door warning |No output/join/consumer; distinct containers do not prove parallel plaintext flows |
| C22-ARCH-RECOGNITION |Prime/Bifid are recognizers; earlier-source recall feeds local hash/container |Separates complete transforms from unsupported downstream uses; name/context clues |No authored discard; under-explains residual/matrix/body unless other roles assigned |

All five remain INCONCLUSIVE as intended complete architectures. Strongest supported *partial* graph is main-path sibling objects plus a separate SalPhaseIon branch, raw-dbbi square/faed Bifid in parallel with prime/residual derivation, and conditional local hash/container/hash syntax. Do not privilege a serial Bifid→inner graph.

## H. Assumption challenge

| Assumption | Support | Contradiction / alternative | Distinguishing observable |
|---|---|---|---|
| Prefix names intended technical material |Recognized seven-letter prefix |Community caveat; no primary assignment; could recognize theme/source |Exact independently defined consumer, not another plausible prefix |
| Bifid is final faed interpretation |Complete reversible recipe |Reversibility is generic; rest explicitly unresolved |Full downstream object explained without optimized alphabet/period |
| matrixsumlist is numeric payload |Literal operation name |No list instantiated; direct families fail |A typed source→metadata→consumer edge accounting for preserved information |
| Residual60 is a passphrase |Byte stream fits variable input |No destination; direct bounded uses negative |Source-assigned password role versus exact coordinate/selection role |
| Body must be consumed immediately |Long deliberate source object |No next-edge instruction; recognition/multi-door alternative |A complete body consumer, not merely length compatibility |
| Inner immediately follows Bifid |Both unresolved within research |Distinct source branch; known inner encrypted input is paragraph5 |Authored cross-stage binding, not physical source adjacency |
| Phase3 current order is global |Earlier verified local sequence |Multi-door hints, local reused labels/numbering |Explicit shared namespace/consumer or an independently reproduced joined graph |

## I. Experiments and graph effects

Each experiment discriminates a finite claim and has an observable/falsification condition in JSON:

1. Equal-size identity: distinct inner/SMALL bytes and dbbi/checker output eliminate identity edges. Other relations survive.
2. Prefix-source boundary: coordinates cross the cut and only community recognition supplies it; eliminate authored/disjoint-source-cut promotion.
3. Direct size/type consumers: eliminate104→196 and570/563→32/80 direct identities; variable-length input compatibility remains nondiagnostic.
4. Exact tiling: no shorter whole-block repetition; eliminate only exact repeated-tile edges.
5. Axis-sums+frame losslessness:657 counterexample certificates eliminate unique reconstruction from these objects alone; metadata and constrained roles survive.

These reduce concrete uncertainty rather than produce another generic no-consumer audit. No solution-producing edge is discovered. If three future experiments fail to distinguish a claim, stop that track and compare architectures instead of adding audits.

## J. Single highest-information next experiment

**Static coordinate-interface test for the25-event/25-square hypothesis.** Test whether the original ordered event tuples already specify a complete25-entry square lookup, rather than silently turning equal cardinality into an alphabet or routing instruction.

Expected observable: a source-defined, total, single-valued bijection in the existing coordinate/symbol domains that uses every event once and preserves an inverse. Falsification: coordinates lie outside the existing5×5 domain, collide under the only authored conversion, or require unlicensed conversion/ranking/normalization. A failure closes the **direct** lookup edge, not all metadata architectures. No source-defined conversion means an explicit missing interface, not authorization to invent one.

This is higher-information than further passphrases: it attacks the one remaining equal-cardinality interface without cryptographic optimization. The new losslessness result makes a simple matrix reconstruction insufficient; coordinate metadata remains worth a strictly typed preflight.

## K. Exact implementation plan

1. Load frozen `cycle15/frame-object-audit.json` event tuples and `cycle10/instruction-graphs-v3.json` prime-marker/square maps. Verify source hashes; do not traverse/extract the image again.
2. Define only existing domains: original14×14 source coordinates,25 ordered event identities,25 ordered prime markers, keyed-square5×5 coordinates. Keep color identity and repeated symbols separate from coordinate uniqueness.
3. Check direct domain membership, exact25 coverage, duplicates, and single-valued inverse for explicitly sourced mappings only. No modulo5, coordinate rescaling, sorted rank, free alphabet, transposition or candidate string.
4. Record expected observable, falsification condition and graph change. If no licensed conversion exists, stop at that missing edge rather than enumerate conversions.
5. Add only a small domain/bijection test if implementation proceeds; no AES/password/terminal-material operations.

External searches: none performed. Missing historical source or creator explanation could resolve a concrete binding, but current offline scope does not authorize retrieval. A query would need question→specific source→exact binding evidence→graph effect before any future scope change; broad internet search is not the next step.

| Deferred question | Specific missing source | Required evidence | Effect on graph |
|---|---|---|---|
| Does the historical recipe explicitly choose full period, or inherit a decoder default? |Exact contemporaneous `BifidCipherDecode.mjs` revision used by the preserved recipe |Argument/default semantics and version, not a new output search |Separates a selected parameter from an automatic full-object transform |
| Does any original creator instruction bind SMALL's answer to inner or Cosmic? |Original creator explanation or preserved reply-target metadata for that exact claim |Explicit named input/output assignment |Selects a destination edge, not a password dictionary |
| Was original first-piece source ever authored HTML rather than the preserved PNG response? |Contemporaneous original `/puzzle` response archive |Exact response bytes and authored resource ownership |Changes the source-domain inventory, not a decoder alphabet |

These are missing-evidence questions, not network actions or prerequisites for the current report.

## Validation / preservation

Initial generator failed closed because it expected two exact full-output references; exhaustive exact-object matching found eight. The assertion was corrected to retain all eight, not suppress the additional evidence. First report snapshots remain. Review also corrected phrase spans from record-relative to original-file coordinates; a synthetic location test verifies that distinction. Final focused15 tests pass1.652s. These are implementation controls, not the research objective.

Full scoped regression: **251 tests pass63.993s**,236 prior public-analysis tests plus15 new. Run the exact cycle21 findings command with `tests.test_architecture_reconstruction tests.test_sumlist_information` appended before `-v`; output `/tmp/gsmg-cycle22-public-regressions.txt`.

Integrity PASS: two current reports regenerate byte-identically;11 new complete ledger rows/source/artifact links;124 prior cycle10–21 links unchanged;201 unique IDs.88 eligible original public files and12/5/18 evidence files match manifest lengths/hashes. Five external-state snapshots not opened. No old search replay, original-evidence edit, external access or recovered terminal object.
