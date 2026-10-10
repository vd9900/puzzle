# Cycle 25 findings — 2026-10-02

## Question

Does the cycle24 list15 directly equal a canonical column marginal of an existing downstream FAED/Bifid object, without guessing an operator?

## Type correction

The list is not one homogeneous measurement. It is the concatenation of two fields:

```text
dbbi rank sums7 = [69,58,49,59,53,74,60]
label bit counts8 = [0,13,13,7,6,6,3,8]
```

The left field sums source symbols on the `a=1…i=9` scale. The right field counts binary ones. Its leading zero is forced by the zero most-significant bit of every lowercase ASCII byte in `matrixsumlist`. Their common row count and `7|8` width are exact; a common numeric scale is not authored.

## Structural experiment

The fixed source-keyed square supplies canonical row and column coordinates for six existing width15 objects: full/upper/lower FAED, rendered Bifid output, and the even/odd Bifid planes. For each object, the test computed row-coordinate, column-coordinate, and coordinate-pair column totals using both zero- and one-based coordinates: 36 fixed signatures.

No signature equals list15 in order, and none has the same multiset. Four expected Bifid coordinate-conservation identities pass, providing positive controls for the representation.

## Result

- Shared width15 geometry: **STRONGLY SUPPORTED**.
- Homogeneous sum-list15: **WEAK**.
- Direct downstream coordinate-marginal edge: **REJECTED**.
- Two-field `7|8` interface: **STRONGLY SUPPORTED dimensionally; consumer UNKNOWN**.
- Parameterized downstream action: **UNKNOWN**.

The remaining missing edge is now exact: no public instruction binds either the rank-sum7 field or bit-count8 field to a target plane, action, normalization, or field-wise consumer. Any further transform would add an unauthored rule. No AES, encrypted-blob test, candidate material, or private-key operation occurred.

Reproduce with:

```bash
python3 -m tools.matrix_marginal_identity
python3 -m unittest tests.test_matrix_marginal_identity -v
```
