# Cycle 10 — instruction construction and provenance

Date: 2026-09-30. Status: INCONCLUSIVE. Scope: offline public text/images only.

## Reproduction

`python3 -m tools.instruction_graphs`

`python3 -m unittest tests.test_instruction_graphs -v`

Nine focused tests pass in4.063 seconds. No new cryptographic trials or trial inputs. Do not run the historical broad suite for this narrowed task. Earlier experiments, including an already-present cycle10 masked-matrix result from the previous scope, are retained rather than replayed. No Git metadata exists in this workspace.

Current immutable outputs are `instruction-graphs-v3.json` and `instruction-occurrences-v3.jsonl`. Revisions1/2 preserve the initial text-only index and subsequent issue-body extension; revision3 adds typed graph edges and a visual spectrogram locator. Only revision3 is current.

## Primary layout and exact positions

All positions below refer to the first textarea of `research/sources/salphaseion.html`, line18. Normalized coordinates are zero-based, half-open, after removing whitespace. UTF-8 byte coordinates refer to the original file; source character/line/column coordinates are also preserved in JSON.

| Object | Normalized span | Original UTF-8 byte span | Verified interpretation |
|---|---|---|---|
| dbbi91 | 0:91 | 456:637 | Unresolved a–i source |
| matrixsumlist | 91:195 | 638:845 | 104 a/b symbols, ASCII with a0/b1 |
| faed570 | 195:765 | 846:1985 | Unresolved a–i source; name570 is research shorthand |
| lastwordsbeforearchichoice | 766:829 | 1988:2113 | Decimal letters -> whole integer -> ASCII |
| thispassword | 830:859 | 2116:2173 | Same verified decimal-letter codec |
| shabefourfirsthintisyourlastcommand | 860:895 | 2176:2245 | shabef + ourfirsthintisyourlastcommand |
| embedded container, first half | 895:959 | 2246:2373 | Published Base64 fragment |
| enter | 959:999 | 2374:2453 | 40 a/b symbols -> ASCII enter |
| embedded container, second half | 999:1063 | 2454:2581 | Published Base64 fragment |
| shabefanstoo | 1063:1075 | 2582:2605 | shabef + anstoo |

True z-delimiters are at normalized765/829/859. The two container fragments together have128 Base64 characters; enter is a separately encoded insertion. Internal cipher z at normalized958, immediately before enter, is not a fourth clue delimiter. All regions partition the first textarea except its three genuine delimiters; tests reconstruct every region from original bytes.

`shabef` is a mixed construction: literal sha plus b2/e5/f6. It is not a global A1Z26 substitution of the full command. The six-character operator ends at866, so the ordinary-language suffix begins with our, not four. The initial notebook observation and saved issue6 repeat the wrong “four first hint” split; the notebook later corrects it.

There is no literal SMALL in the original page. Original headings are SalPhaseIon (line16) and Cosmic Duality (line19), followed by separate textareas. Cosmic's normalized container is1792 characters. Preserved uppercase SMALL occurrences are secondary labels, including a saved issue104 comment dated2026-08-23. They do not establish that SMALL is an intended literal input or decoded output.

## Derived objects and original positions

- Residual60/61 are **not contiguous source strings**. JSON records each retained symbol's logical index, original normalized span and UTF-8 span, plus every removed prime token. Both documented masks are reused directly; no tokenization search occurs. Mask1017 yields83 logical tokens/60 residual letters; mask505 yields84/61, the same residual plus terminal e.
- The25-event frame map comes from the preserved cycle03 result. Its last two source dependencies are normalized96/104: b/a at binary-label offsets5/13, corresponding to continued logical primes89/97. Selecting residual60 depends on continuing the counter, different dbbi/binary codecs and near-white1. This is not a creator-authenticated branch choice.
- Source-keyed Bifid uses exact dbbi first-occurrence order, J=I alphabetical filler and period570. Every output letter has two mapped source-coordinate dependencies. The btcseed prefix uses only faed indices0..3 and285..288. Round-trip and all570 dependency calculations pass tests. Reproducibility establishes a transformation, not the meaning of its563-letter remainder.
- HASHTHETEXT is not literal primary-page text. It comes from human reading of the archived left-minus-right audio spectrogram, hex `48 41 53 48 54 48 45 54 45 58 54` -> ASCII. The report binds the audio hash, reproduction artifact and visual glyph rectangle153,416–1718,526. It does not invent exact audio time boundaries or a hash argument.
- The1539-letter speech fixture is verified against its saved encoded Phase3.2 fixture using the one-to-one CP273/Beaufort transformation only. Exact decoded offsets: sourcecodes1021; reinsertingtheprimebasics1089; afterwhich1114; selectfrom1143. Encoded byte spans mapped independently. There is **no literal choice occurrence** in this speech. Calling reinsertingtheprimebasics “the last words before choice” is semantic, not uniquely delimited extraction.

## Provenance and chronological distinctions

The index records2097 exact case-sensitive occurrences across66 eligible preserved public text/code/issue files, including273 issue mentions with raw JSON spans, body identifiers, author labels and record-created timestamps. Public images/audio are mapped separately. Source scripts are read, not executed; external-state JSON excluded. A mention count is not independent evidence; retrieval time is not publication time.

| Date | Evidence | Interpretation limit |
|---|---|---|
| 2019-04-22 | Creator-labeled hash supplied, later explained as website token-error aid; creator export lines26/41 | Not uniquely identified as final first-hint referent |
| 2020-01-14 | Color poem screenshot plus transcript; creator export line195 | Screenshot displays Jrk Bgrt/admin, no date; date from transcript |
| 2020-05-19 | Earliest preserved exact HASHTHETEXT chat mention, line9667, Timofey Bondarenko | Community mention, not hint creation date |
| 2021-01-08 | “my first hint might be your last command,” chat line12406 | Deleted Account, not authenticated creator confirmation |
| 2021-03-14 | Earliest preserved exact matrixsumlist chat mention, line15714 | No operation or publication-date proof |
| 2021-05-14 | Saved issue6, slonyarakmw, matrixsumlist and wrong “four first” split | Secondary issue is not a second primary instruction |
| 2021-05-19 | Decoded last-words label in chat, line18496 | Architect source unresolved |
| 2021-08-21 | Movie-Architect quotation proposal, chat line18957 | Quoted choice passage absent from verified modified speech |
| 2021-12-26 | Creator-labeled prime/zeroed-out hint, creator export line627 | No specified mask, operand, operation or index convention |
| 2023-08-04 | SHA(first hint)/SHA(answer) questions, chat line21537 | Community questions, not demonstrated construction |
| 2023-08-05 | Answer-to-Cosmic conjecture, line22488; competing inner32 proposal22491 | Both destinations speculative |
| 2023-08-06 | Creator-labeled ying-yang hint, creator export line804 | No placement after SMALL |
| 2025-06-11 | Sycorax Bifid recipe and coincidence caveat, chat122234/122269 | Community discovery; transform verified, intent unresolved |
| 2026-08-23 | Earliest timestamped uppercase SMALL match among saved issue bodies | Container shorthand, not creator-authenticated instruction |

Original HTML/image establish direct public content. Screenshots with creator labels are stronger attribution than anonymous paraphrases, but no preserved signed authorship record establishes a creator-authenticated execution graph. Chat labels, fork claims and secondary interpretations remain distinct. Filename dates are not authenticated publication times.

The May6 2021 entry-route screenshot likewise shows **Deleted Account**, not creator authentication. Earlier documented route reproduction supports HASHTHETEXT referring to image text at entry, but does not establish the later first-hint command's referent. No entry route is recomputed this cycle.

## Best-supported order and competing graphs

**Physical order established exactly:**

`dbbi -> encoded matrixsumlist -> faed -> lastwordsbeforearchichoice -> thispassword -> first-SHA command -> embedded container/enter -> answer-SHA command`, then Cosmic under a separate heading.

**Best-supported execution skeleton, still tentative:**

`SHA256(X) -> process embedded container -> SHA256(Y)`

X/Y remain unknown. Associating X with that container, Y with its answer and the resulting digest with Cosmic are progressively weaker inferences. Physical adjacency is not a verified data-flow edge.

Seven finite hypotheses and typed graphs include evidence, locations, assumptions, operation order, inputs/outputs, confidence, contradictions and next test:

| ID | Surviving construction | Confidence/critical missing edge |
|---|---|---|
| C10-G01 | Two local SHA commands bracket container processing | Medium skeleton; unknown arguments/destination |
| C10-G02 | matrixsumlist labels preceding dbbi as object/type | Medium-low; no exact list representation |
| C10-G03 | matrixsumlist commands image operation consumed by residual/faed | Medium image referent, low join confidence |
| C10-G04 | Parallel dbbi prime and source-keyed Bifid branches | Transform verified; intentional join unknown |
| C10-G05 | First-hint recalls hash operation, not chronological first-hint text | Medium-low; referent/scope unresolved |
| C10-G06 | Trailer selects Architect source before applying SHA | Choice anchor/source/word count unresolved |
| C10-G07 | b/be encode B/Y initials and weighted-color numeric data | Low; one total equality and branch conflict |

SMALL is best modeled as a **secondary label for container input**, potentially an intermediate stage label. It is not a primary command, known answer or literal creator input. matrixsumlist can remain an object label or imperative. An ordering role needs an additional explicit routing convention; the word itself chooses no axis or algorithm.

## New bounded text/image diagnostic

Primary b2/e5/f6 and prime markers b/be permit exact arithmetic `b ->2 ->B`, `be ->25 ->Y`. The color hint independently mentions Blue/Yellow having numbers. Inferring B/Y as color names is plausible; inferring **cell weights** rather than marker labels is another assumption.

One fixed diagnostic, not a palette search: keep black1/white0/near-white0 from verified binary decoding, substitute blue2/yellow25. Original86 black/15 blue/9 yellow cells give `86 +15*2 +9*25 =341`. Residual61 A1 total341; residual60 total336.

This is a **single conserved-total coincidence**, not list decoding, p-value, spatial match or intent proof. It favors61 while the conditional25-event convention favors60. It challenges silently discarding either branch. No sum-list serialization, trial input or cryptographic search is produced.

## Eliminated interpretations

- Correct command split is not “four first hint.”
- SMALL is not literal primary text, an imperative or verified output.
- Cipher-internal z is not a fourth plaintext delimiter.
- No primary instruction specifies row-first/column-first/reversals/routing merely by saying matrixsumlist.
- btcseed is not a verified complete instruction; dependent prime/Bifid evidence is not independent corroboration.
- Anonymous first-hint echo and speculative answer-to-Cosmic/inner32 edges are not creator confirmations.
- No literal choice-word anchor in verified modified speech.
- Earlier tested literal/missing-cell/numeric-routing/post-Bifid constructions are not unexplored. Saved negatives retained, not replayed; broader object/operation interpretations survive.

## Single highest-value next offline experiment

**Fixed weighted-color positional conservation audit**, not another cipher search: original14×14 palette black1/white0/near-white0/blue2/yellow25, already verified down-first counterclockwise spiral, and the two documented token-source maps only.

First require a partition/comparison order justified by preserved source boundaries. If none is supported, report that missing edge and stop rather than inventing a grouping. A useful positive must reconstruct positions and account for every symbol;341 alone is insufficient. This tests marker arithmetic, color-number wording, matrixsumlist's object/operation role and60/61 branch conflict without optimizing plaintext appearance.
