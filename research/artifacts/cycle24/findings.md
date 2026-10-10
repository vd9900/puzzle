# Cycle 24 findings — 2026-10-02

## Scope

This phase is non-executing structural analysis. It generated no candidate password or private key, performed no AES operation, tested no encrypted blob, and made no wallet or chain query.

## Edge classification

| Edge | Status | Evidence |
|---|---|---|
| `dbbi91 → matrixsumlist` | **UNKNOWN** | Exact adjacency and a reversible shared matrix interface exist, but no operation makes one the output of the other. |
| `matrixsumlist → 25-event prime/color` | **WEAK** | Two continued prime markers lie in the raw label; the creator-attributed order instead places `yellowblueprimes` before `matrixsumlist`. |
| `25-event prime/color → residual60` | **STRONGLY SUPPORTED** | Frozen mask1017/near-white=1 maps the first23 event labels to prime markers; the complement is exactly60 tokens. |
| `residual60 → faed570` | **UNKNOWN** | No lossless transform, operand binding, or source-authored consumer is known. |
| `faed570 → source-keyed Bifid570` | **STRONGLY SUPPORTED** | The fixed square/period transform is exact and reversible and produces the recognized prefix; its intended use is not primary-authored. |
| `Bifid570 → btcseed` | **VERIFIED** | The deterministic output begins with exact `btcseed`. |
| `btcseed → remaining Bifid body` | **UNKNOWN** | The prefix supplies no operation on the remainder. |
| `remaining Bifid body → downstream` | **UNKNOWN** | No receiving type, axis, value map, or operator is authored. |

## Highest-information structural experiment

`C24-MATRIX-WIDTH-INTERFACE` tests a fixed matrix geometry already implied by the public objects:

```text
dbbi91               = 13 × 7
raw matrixsumlist104 = 13 × 8   (13 ordinary eight-bit characters)
rowwise join195      = 13 × 15
faed570              = 38 × 15 = two 19 × 15 panels
Bifid even/odd rails = two 19 × 15 coordinate planes
Bifid body563        = 8 + 37 × 15
```

All285 Bifid digraphs were checked. Every one is the exact cellwise combination of corresponding cells in the two `19×15` FAED panels. Reshaping the output as `38×15` makes its first row `btcseeddeoemcke`: `btcseed` exactly fills the7-cell field and the remaining body is the other8 cells plus37 full rows.

This distinguishes two architectures. The linear model treats `btcseed | 563 symbols` as a header plus opaque tail, despite no separator and a cut through a natural Bifid digraph. The matrix model preserves every symbol and derives the `7|8` and width15 boundaries independently from `dbbi91` and the raw label. The matrix model is therefore **STRONGLY SUPPORTED structurally**; an intended `sum` or `list` operation remains **UNKNOWN**.

This exact join is absent from the preserved coverage. Earlier work reshaped `dbbi91` and `faed570` separately, tested width15/38 FAED grids, and padded the combined195-symbol source to14×14 with one added cell. It did not align13 seven-symbol dbbi rows with the label's13 native bytes and propagate the resulting width15 through both Bifid halves. The main caveat is that this rowwise join is inferred; no primary instruction explicitly chooses its orientation.

## Reproduction and next constraint

```bash
python3 -m tools.matrix_width_interface
python3 -m unittest tests.test_matrix_width_interface -v
```

Five width-interface tests pass. The bounded follow-up below tests only the single axis implied by the new fixed geometry; arbitrary alternative axes remain excluded.

## Fixed-axis follow-up

The width result itself supplies one bounded axis test. Use the page-adjacent `a…i=1…9` convention for the seven dbbi columns and retain the label's established `a/b=0/1` type for its eight columns. Summing across the13 rows gives the orientation-invariant list:

```text
[69, 58, 49, 59, 53, 74, 60, 0, 13, 13, 7, 6, 6, 3, 8]
```

The15 values align one-to-one with the columns of FAED38×15, both FAED19×15 halves, and both Bifid19×15 coordinate planes. The competing sum direction produces13 values and matches no downstream axis. Information accounting also closes exactly:60 residual cells +31 raw cells represented by the first23 events +2 label cells represented by the final events +102 other label cells =195.

This adds a **PROMISING** typed edge from the complete panel to a sum-list15. It does not identify whether the list should add, subtract, order, select, or otherwise operate on downstream columns. Those operations remain unlicensed and were not run. Reproduce with `python3 -m tools.matrix_sum_interface`; five focused tests pass.

## Direct-operation feasibility

A final type-only check tested whether sum-list15 directly supplies a permutation, one row or square-cell index per column, a complete partition of570 or285 symbols, or printable byte values. All direct interpretations fail:

- the values range0…74 and only13 are distinct, so they are not a permutation of15 columns;
- seven values exceed every zero-based FAED/half-panel/square selection domain, and the zero also invalidates each one-based form;
- the list totals478 rather than570 or285;
- its last eight values are outside printable ASCII.

Modulo reduction, ranking with ties, cyclic shifting, arithmetic signs, or truncation could force the list into a domain, but every such operation adds an unauthored parameter. The apparent supporting words do not resolve it: `sum of a remainder` is inherited movie dialogue, and `select` is grammatically scoped to ciphers, encryptions, and passwords. The existing411-message creator-attributed export also has zero literal occurrences of `array`, `index`, `indices`, `selector`, `select`, `choice`, `sumlist`, `column`, or `row`; this bounds literal evidence but cannot exclude synonyms or encoded instructions. Direct consumers are therefore **REJECTED**; normalized/arithmetic consumers remain **UNKNOWN** and unexecuted.
