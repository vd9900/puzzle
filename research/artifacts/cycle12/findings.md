# Cycle 12 — source-join preflight and attribution limits

Date: 2026-09-30. Status: INCONCLUSIVE construction. Offline public text/image analysis only. No new cryptographic trials, trial-material generation, external access or puzzle-source changes.

## Reproduction

```bash
python3 -m tools.source_join_preflight
python3 -m tools.selector_evidence
python3 -m tools.literal_occurrence_control
python3 -m tools.cover_reference
python3 -m unittest tests.test_source_join_preflight tests.test_selector_evidence tests.test_literal_occurrence_control tests.test_cover_reference -v
```

Current artifacts are `source-join-preflight-v2.json`, `selector-evidence.json`, `partial-literal-control.json`, `cover-reference.json`. Initial source-join revision remains historical. The v2 report adds exact source paragraph/encoding-clue roles and corrects the recipe locator. Prior cycle10/11 evidence is unchanged.

## What was tested

The cycle11 next task required a source-backed selector before extracting anything. The preserved corpus already contains a specific community recipe: March3 2026 20:39:06 UTC−05, Denis Golovkin, full-transcript line168601. Its longer explanation appears at20:57:30, line168664.

That recipe aligns the **91 raw dbbi characters** with the already-decoded **91 checkerboard letters**. It selects the physical character positions occupied by logical-prime b/be tokens, including **both physical letters** for be. This is a bounded reproduction of published analysis, not a newly generated dictionary or arbitrary route. Only documented masks505/1017 are reused.

| Existing branch | Logical dbbi tokens | Logical prime positions | Raw selected positions | Raw complement | Exact published31-letter quote |
|---|---:|---:|---:|---:|---|
| mask505 | 84 | 23 | 30 | 61 | No |
| mask1017 | 83 | 23 | 31 | 60 | Yes |

All selected/complement positions reconstruct the original91-letter text, without omitted/wrapped/reordered indices. Raw and logical indexing are distinct: directly selecting the23 logical positions does **not** reproduce the published quote. Every selected dbbi token maps back to original HTML spans, and every checkerboard output letter maps to its encoded numeric-byte span.

Neither unchanged selected branch contains literal yin, ying, yinyang or yingyang. Both contain one yang at the same raw source indices **6,10,11,13**. The unchanged complements contain none of those literals. The branch matches are dependent, not independent evidence. No anagrams, rearrangements, hashes or cryptographic processing are performed.

**Result:** the published31-letter selection is reproducible, but it does not reconstruct the complete literal yin-yang checkpoint. It also does not perform a matrix sum or identify an Architect source/choice boundary. Those are missing graph edges, not solved steps.

## Exact partial-occurrence control

Do not dismiss a partial word solely because the output is otherwise unstructured. The fixed projection contains an uncommon yang under a deliberately narrow null. Hold the published selected positions and literal fixed; uniformly permute the complete91-letter source multiset. The counts are y3/a10/n7/g2.

Because yang has no proper prefix equal to its suffix, overlapping occurrences are incompatible. Exact finite inclusion-exclusion over nonoverlapping start sets gives:

-30 selected positions: probability at least one yang = **6677547/37771954220 ≈0.000176785849128**.
-31 selected positions: **2077457/11331586266 ≈0.000183333290789**.

Arithmetic is verified against exhaustive small synthetic multisets, with zero puzzle shuffles sampled. This is **not a discovery-wide p-value**: English text is not a random shuffled multiset; source/selector/literal were selected during prior community investigation; upstream trials are unknown; both branches share the same four indices. Do not multiply these probabilities by prime/Bifid controls or infer a full construction from them.

## Original source objects are different branches

The saved2422-byte public Phase3.2 fixture has six exact CRLF paragraphs:

| Paragraph | Original byte span | Role |
|---|---|---|
| 0 | 0:332 | Public introductory text |
| 1 | 336:443 | Encoding/classical-transform clue |
| 2 | 447:1986 | Encoded1539-byte Architect speech |
| 3 | 1990:2139 |149-digit checkerboard source |
| 4 | 2143:2288 | Checkerboard-alphabet clue immediately before container |
| 5 | 2292:2422 | Public encoded container |

The91-letter proposed selection source comes from paragraph3, **not** paragraph2's Architect speech. Paragraph4 intervenes before the container, so “last words before the next container” does not literally select paragraph3 by adjacency. No literal choice appears in these source paragraphs.

`One for one, four for one.` is an encoding clue in paragraph1; it contains no literal1141 index/slice instruction. Historical1141 speech-suffix experiments were already tested and are not replayed. An encoding-associated number is not automatically a character selector.

## Creator confirmation versus community recipe

March3 2026 original chronology, UTC−05:

| Time | Source role |
|---|---|
|20:27:00 | Creator-labeled “Looks at gnomad” |
|20:27:47 | gnomad refers to the “in front of your eyes” comment |
|20:28:55 | Another participant's social joke |
|20:29:05 | Creator-labeled “Bingo” |
|20:39:06 | Denis publishes the31-letter extraction |
|20:57:30 | Denis publishes the longer source/selector interpretation |

Bingo precedes the extraction by**601 seconds** and the full recipe by**1705 seconds**. No preserved reply identifier binds it to either later message. It cannot be claimed as creator confirmation of this later recipe from chronological adjacency alone. The precise earlier target remains unknown.

Other selector claims have bounded attribution:

- “if you know how the array is indexed ofc,” March1 2021, full-transcript line13996, is **Janusz Baran**, not creator instruction. The later creator-labeled “Ancient spelling…many typos” response identifies a spelling issue, not an index convention.
- The creator-labeled April8 2020 movie quote about hope/source is immediately followed by **“not a hint btw, just fooling around.”** Do not silently promote it to a source-selection command.
- The creator-labeled export has411 message headers. A literal keyword audit finds no array/index/indices/selector/select/choice/sumlist/column/row words. This is **not** a complete semantic proof that no selector is encoded elsewhere.
- Relevant SalPhaseIon HTML tags carry no hidden id/name/data-selector; no comment/script is present. This eliminates a simple markup-based selector in this specific source, not all image/encoded interpretations.

## New-year timing correction

The screenshot/archive label says January1 2026; the preserved transcript uses **December31 2025 UTC−05**, corresponding to January1 UTC. Its five dot messages and binary greeting occur at22:15:02,22:16:15,22:17:05,22:18:07,22:19:05,22:20:03. Exact intervals are **73,50,62,58,58 seconds**, not five exact one-minute intervals.

Direct MSB-first ASCII decodes77 octets to the preserved New Year greeting. Its “tiny hint” wording, dot counts and `<3` do not explicitly identify an Architect source, axis or character selector. No speculative timing/dot operation is executed. Screenshot timezone is not independently preserved.

## Cover reference: stronger image attribution, unresolved mapping

The preserved December10/11 2022 screenshot shows barrystyle's attachment thumbnail, creator-labeled “That is very specific,” and “If the puzzle is solved you'll see how scary specific that is.” The full transcript lacks the attachment thumbnail metadata, so it cannot independently establish file identity.

On **January8 2023**, creator-labeled export line669/full transcript20070 says barrystyle “provided a very specific hint already.” This supports the earlier contribution being hint-relevant more directly than an incidental title match, but the exact attachment hash is missing.

The saved553×651 Cosmic Duality cover visibly has two interlocking contrasting curved star fields, with a bright pale point in the upper warm field and a yellow/orange point in the lower blue/pale field. This is qualitative observation, not an exact star count, palette, bit mapping or mathematical decoding. The primary page separately names Cosmic Duality; the February23 2023 hint names yinyang. Neither specifies how cover geometry consumes residual60/61, faed570 or image-axis sums.

No book-text cipher, page number, new color weights, image transforms or star-count operation follows this source-reference audit.

## Surviving hypotheses and next experiment

### Best-supported ordering, not a complete execution graph

The primary source physically places `thispassword` before `shabef` + `ourfirsthintisyourlastcommand`, then the small encoded container, then `shabefanstoo`. The `f` completes `shabef`; interpreting the following text as “four first hint” is a segmentation error. This supports separate text-hashing and answer-hashing roles around the container, but does not identify the exact text object or bind the earlier audio `HASHTHETEXT` to that position. `SMALL` is a secondary label for the encoded input object, not a literal primary command or a verified plaintext output.

Separately, the exactly reproduced February23 2023 creator-attributed hint lists `yellowblueprimes → matrixsumlist → lastwordsbeforearchichoice → yinyang` in that order. These arrows represent **clue order**, not verified data-flow edges. This is stronger evidence than a community paraphrase, but is preserved attribution rather than cryptographic authentication. It does not specify where residual60/61, faed570 or the source-keyed Bifid transformation enter the graph. The verified Bifid prefix constrains its source/square transformation, not the placement of hashing or the identity of the eventual text object.

- Published raw-prime selection is a reproducible partial relation between two91-character public objects; intended source/selector/join remains INCONCLUSIVE.
- matrixsumlist can still be an object label, an image operation or an intermediate before Architect words; the published recipe does not distinguish them.
- The complete literal yin-yang checkpoint is **not** present in either unchanged selected half/complement. A source-backed additional operation would be required; no anagram expansion is justified.
- Cover/image relevance has PROMISING preserved attribution, but exact file identity and spatial/data correspondence remain unknown.

**Single next offline experiment:** source-constrained visual correspondence audit of the preserved Cosmic Duality cover, original puzzle image and color-wording hint. First inventory what relationships are actually shared, establish image-reference provenance and identify any explicit correspondence rule. Require a source-backed mapping before decoding; do not invent palettes, rotate images, count arbitrary stars or restart cipher searches.

## Validation notes

Source-join focused suite:8 tests pass0.288s. Selector-evidence:5 tests pass2.997s. Exact-occurrence control:5 tests pass0.013s. Cover-reference:4 tests pass1.565s. Initial community quote locator assumed a fixed blank-line count; corrected to locate the exact quote **within its original dated message**, with no source changes. Current v2 join artifact retains the earlier immutable revision.

Final combined public-analysis suite: **52 tests pass in9.358s**, including cycle10/11 source-map/order/conservation regressions and all22 new tests. Verified88 eligible original public-source hashes and12/5/18 separate evidence hashes, four cycle12 ledger records with every required hypothesis field and exact artifact hashes, and14 prior cycle10/11 linked artifact hashes. External-state snapshots are excluded. The integrity check initially expected a top-level trial counter; the join report intentionally nests its zero counters under `search_space`, and the corrected checker verifies that schema without changing evidence. No historical search suite is executed.
