# Cycle 11 — fixed conservation, preserved hint order, and trailer referents

Date: 2026-09-30. Status: construction remains INCONCLUSIVE. Strictly offline public text/image analysis; no new cryptographic trials or trial-material generation.

## Reproduction

```bash
python3 -m tools.weighted_conservation
python3 -m tools.hint_order_audit
python3 -m tools.trailer_referents
python3 -m unittest tests.test_instruction_graphs tests.test_weighted_conservation tests.test_hint_order_audit tests.test_trailer_referents -v
```

Immutable outputs: `weighted-conservation.json`, `hint-instruction-order.json`, `trailer-referents.json`. Do not run the historical broad suite under the present scope. Existing source/cycle10 artifacts remain unchanged.

## Fixed weighted-color path: finite negative

The cycle10 hypothesis used original black1/white0/near-white0/blue2/yellow25 values. Its341 total equals residual61's A1 total, while residual60 totals336. This is one equality, not a list or positional reconstruction.

No primary text specifies an axis or residual grouping. Three diagnostic partitions are grounded in existing source geometry: original rows, original columns, and the already verified24 spiral ASCII octets plus the four-bit tail. No new image variant, route, reverse ordering, arbitrary partition or palette is introduced.

For each partition and each existing residual branch, test three exact relations: atomic sum-list identity, literal decimal concatenation, and consecutive nonempty additive groups of untouched positive residual values. The last is a necessary conservation diagnostic, **not a creator-instructed grouping**. Six cases/three protocols =18 exact comparisons, all negative.

| Partition | Groups | Decimal-total digits | First target boundary | Residual boundaries surrounding failure |
|---|---:|---:|---:|---|
| Original rows | 14 | 25 | 32 | 30 then33 |
| Original columns | 14 | 24 | 9 | 4 then13 |
| Verified spiral octets/tail | 25 | 34 | 6 | 4 then13 |

Both residual branches fail the first cumulative boundary for every partition. Rows+columns double-count cells and total682, so cannot conserve either positive residual total without an additional unexplained transform.

The25 byte groups are **not** in one-to-one correspondence with25 special-color events:20 groups have one event, group20 has two (near-white and a colored cell), three later groups have one, and the tail has none. A matching count25 does not imply an event/partition identity.

Reject only these18 unchanged-source realizations. Do not reject every possible numeric role, fit a new grouping to341, or enlarge a cipher search. Secondary fork-ENDGAME lines358–369 claim broader weighted row+column coverage, but linked reports/scripts are not preserved; that claim is not local execution evidence.

## Stronger instruction-order evidence found in the preserved corpus

Cycle10's order assessment omitted the February23 2023 binary hint, already present in the source corpus. This is a **new local provenance/transform verification**, not a newly discovered external hint.

- Original creator-labeled export: `research/evidence/cycle02/_work__creator_jrk.txt:711`, header February23 2023 18:20:03 UTC−05, Jrk Bgrt.
- Full transcript: `research/evidence/cycle02/_work__chat_transcript.txt:20386`, identical161 octets. Four later identical reposts are attributed separately, not counted as independent creator corroboration.
- Screenshot: `research/sources/maintained-hints__2023-02-23.png`, visible February23/Jrk Bgrt/admin. The year comes from archive/transcript; screenshot label/prefix/suffix reviewed, not a claim of independently OCR-verifying every octet.
- Secondary spaced transcription: `research/sources/maintained-README.md:343`, exactly matches after removing its inserted whitespace.

Reverse the **complete1288-bit stream** and read MSB-first ASCII. Equivalently reverse octet order and reverse the bits of each octet. Identity, octet-order-only and intra-octet-bit-only controls do not produce the hint. Encode/decode round-trip reconstructs every original octet; all161 decoded symbols map back to original UTF-8 source spans.

| Exact decoded substring | Zero-based decoded span | Original source octet span, read in reverse |
|---|---|---|
| yellowblueprimes | 0:16 | 145:161 |
| matrixsumlist | 16:29 | 132:145 |
| lastwordsbeforearchichoice | 29:55 | 106:132 |
| yinyang | 55:62 | 99:106 |
| wewontgiveawaythepassword | 62:87 | 74:99 |
| itsinfrontofyoureyesbutyourenotseeingit | 87:126 | 35:74 |
| verylaststepisatruegiveawaypromised | 126:161 | 0:35 |

The strongest directly supported **clue sequence** is now:

`yellowblueprimes → matrixsumlist → lastwordsbeforearchichoice → yinyang`

This explicit co-occurrence/order is stronger than independently assembling scattered labels. It supports a possible sumlist-to-Architect-words join. It still contains no executable arrows, verbs, axes, word counts or index conventions. A clue list may recap solved steps rather than specify strict dependencies. Bifid/faed/SMALL/thispassword/HASHTHETEXT are not named in this hint.

The primary page's local first-SHA/container/answer-SHA skeleton remains separately plausible, with unknown arguments and destination. The binary hint does **not** establish SMALL→Cosmic or place yin-yang after a specific container. Creator attribution in screenshot/transcript is not signed authorship authentication.

## enter: strong formatting referent

The binary enter insertion occurs exactly between two64-character Base64 fragments. Five existing public container blocks use64-character nonfinal lines: both phase2 textareas, Cosmic textarea, the embedded phase3 block and the embedded phase32 block. Both fragments reconstruct the same96-byte public Salted__ container with or without a newline; only Base64 parsing is used.

Formatting is therefore the best-supported immediate role of enter, not a new processing stage or an instruction to insert its literal word into an operand. A secondary role is not mathematically excluded, but currently has no independent evidence.

## Architect source binding

The spaced community walkthrough's full1539-letter speech normalizes **exactly** to the verified decoded fixture. It supports the word boundaries `REINSERTING THE PRIME BASICS` before AFTER WHICH/SELECT FROM, with exact source spans. Those25 letters/four words do not prove that they are the intended “last words”; the count and boundary remain unspecified, and this phrase was already used in earlier experiments.

The preserved community movie quotation at full-transcript line26070 contains “There are two doors,” “The door to your right leads to the source,” and “the problem is choice.” Those exact anchors are absent from the verified modified puzzle speech. Conversely the pre-select prime-basics phrase is absent from that quoted passage. These are different source objects and must not be substituted silently.

Three finite referent hypotheses survive, with all requested evidence/assumption/order/input/output/confidence/contradiction/next-test fields in `trailer-referents.json`:

- `C11-T01`: semantic choice/select boundary in verified modified speech. Source identity strong; selected boundary/count low confidence.
- `C11-T02`: literal choice-bearing movie quotation. Thematic link plausible; source authority/exact selection unresolved.
- `C11-T03`: earlier prime/sumlist object supplies a selector or intermediate operation leading to Architect words. Hint order directly supported; executable join still unknown.

No phrase dictionary, word-window enumeration, text scoring or cryptographic processing follows this audit.

## Next single offline experiment

**Source-coordinate join preflight** for `prime/color → matrixsumlist → Architect words`. Inspect preserved primary/hint formatting for one explicit source selector or positional alignment that fixes the Architect source, choice anchor and index/count convention **before** extracting anything. If none is supported, preserve the unknown edge; do not invent a route or enumerate word windows. This targets the relation named in the verified hint rather than the unsupported341 coincidence.

## Validation notes

Eight weighted-conservation tests pass0.918s; seven hint-order tests pass2.281s; six referent tests pass0.383s. Initial hint test wrongly assumed a single binary occurrence in the full transcript; fixed by binding the original dated header and logging four identical later reposts. One synthetic source-map test used the wrong half-open end offset; corrected. These failures and corrections do not change the public source data.

Final combined focused suite: **30 tests pass7.362s**. Six cycle11 ledger entries have all required hypothesis fields and exact linked artifact hashes. Public source integrity verifies88 original files (external-state snapshots excluded),12/5/18 separately preserved evidence files and both encoded-fixture Base64 byte spans. Construction remains unverified.
