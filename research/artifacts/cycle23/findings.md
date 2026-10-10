# Cycle 23 findings — 2026-10-02

## What was examined

Three bounded interfaces were tested: direct original image-event coordinates into the source-derived 5×5 Bifid square; reconstruction of the dbbi source from residual60 and aligned event labels; and the exact sentence immediately before the encoded Architect block as password material.

## Why it matters

The architecture has 25 image events, 25 square cells and a60/23 split of the83 logical dbbi tokens. Equal dimensions suggested a possible interface, while `lastwordsbeforearchichoice`, `thispassword` and the adjacent SHA instruction made the exact preceding sentence a concrete untested password hypothesis.

## Invariants and tests

1. A direct coordinate edge must place every distinct original event coordinate inside the5×5 target domain without an invented conversion.
2. A source join must account for every logical position exactly once, preserve order, reconstruct all91 raw letters byte-for-byte and reproduce the square by the existing first-occurrence rule.
3. The sentence test may use only exact punctuation/spacing normalizations, whole-string source/lower/upper case, and raw or standard SHA256 representations. Success requires recognized downstream structure or a locally verified match to the advertised address; padding alone is insufficient.

Commands:

```bash
python3 -m tools.coordinate_interface
python3 -m tools.residual_frame_join
python3 -m tools.last_words_literal audit
python3 -m unittest tests.test_coordinate_interface tests.test_residual_frame_join tests.test_last_words_literal -v
```

## Observed evidence

- A fresh public-state check at `2026-10-01T19:20:32Z` still reports the puzzle **UNSOLVED** with advertised prize1.5 BTC. The target has125,636,967 sat chain balance,127 confirmed transactions and no mempool delta. Original PNG and SalPhaseIon bytes exactly match the preserved fixtures; the maintained community repository still points to commit `9e61693404ef74e8e681598116d371924f399ffa`. Evidence: `public-state-refresh.json`.
- Direct lookup: only events6,11 and19 fit a5×5 coordinate domain;22/25 do not. Three color labels and two bit values are not unique event identities. Status: **REJECTED** narrowly.
- Residual join:60 nonprime tokens plus23 prime-position labels reconstruct83/83 tokens and exact dbbi91 SHA-256 `71fe46259e270c113529dfaded4b59c59a9dffd826a7202ab07fc498b6a2c5ca`. The derived square exactly equals `dbifhcegaklmnopqrstuvwxyz`. Status: **CONFIRMED** under the frozen mask1017/near-white branch.
- Literal sentence:12 normalized materials,36 new password representations,216 AES/KDF trials,1 padding hit,0 structure hits,32 bounded raw-key slots and `TARGET_MATCH=false`. Ledger SHA-256 `d46e45b80b484214d4f90e528751671e2ed2f0edea0d9a6ca8552f0bb46c122f`. The exact finite interpretation fails its hard gate.
- Fourteen focused tests pass in0.071s; the full359-test suite passes in88.430s. No trial log contains password, AES key/IV, plaintext, scalar or candidate-address bytes.

## Assessment and next test

The reconstruction result strengthens the relationship between the image-event frame and dbbi tokenization, but it reconstructs a known source object. It does not prove an intended password or Bifid consumer. The next experiment must find a source-authored conversion and named consumer for ordered event identity. Pairing the25 events with25 square cells solely by index is not justified. No broader casing, dictionary, route, cipher or private-key search follows from these results.
