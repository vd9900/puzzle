# Cycle 33 — original matrix instruction audit

Date: 2026-10-02. Scope: deterministic public-source parsing and counting only.

## Result

The original PNG fixes a `14×14` oriented grid and exactly 24 visibly colored cells: 15 blue and 9 yellow. Under the already verified counterclockwise spiral, each of the 24 decoded URL octets has exactly one colored cell at bit offset 7. Their coordinates and order are therefore **VERIFIED**.

The source does not complete a `matrixsumlist` operation:

| Interface | Classification | Evidence |
|---|---|---|
| Original grid/orientation | VERIFIED | Exact PNG and prior spiral decode |
| 24 visible yellow/blue cells | VERIFIED | Exact dominant palette and coordinates |
| Prime-marker correspondence | STRONGLY SUPPORTED/PROMISING | Reproducible conditional cross-artifact match |
| Near-white as a selected 25th event | WEAK/CONDITIONAL | Not named; image bit 0 is reassigned semantic 1 |
| Colored cells as the exclusive sum mask | UNKNOWN | No instruction says to sum only colored cells |
| Blue/yellow binary values | VERIFIED for the earlier URL encoding | Unique among all 32 per-color binary assignments |
| Blue/yellow arithmetic weights for summation | UNKNOWN | Encoding type is not bound to the later sum operation |
| Summation axis | UNKNOWN | Square grid makes rows/columns dimensionally indistinguishable; no axis word appears |

## Cell selection

The exact palette is black 86, white 85, blue 15, yellow 9, near-white 1. Blue/yellow cells occur at spiral indices `7,15,…,191`, one terminal bit per decoded byte. The near-white cell is at zero-based `(7,4)`, spiral index 163 and bit offset 3 of byte 20; it is not yellow or blue.

The ordinary 24-color/dbbi comparison has maximum prefix 20 and zero complete matches. The full 25-event match requires the specific optional-`be` tokenization mask 1017, one-based primes, `b=1/be=0`, addition of the unmentioned near-white cell as semantic 1 despite its verified image bit 0, continuation across the dbbi/label boundary, and `b/a=1/0` for the final two markers. This is strong structural evidence for a relationship, but it does not make the 25-event set a source-complete summation mask.

## Numeric values

Checking every one of the 32 binary assignments to the five observed palette classes gives exactly one assignment reproducing `gsmg.io/theseedisplanted`:

```text
black=1, blue=1, yellow=0, white=0, near-white=0
```

Those values are fixed for the earlier binary encoding. The source also exposes other numbers—blue/yellow population counts `15/9`, initials `B/Y = 2/25`, and RGB triplets—without identifying any as matrix-sum weights. The near-white image-bit/semantic-label conflict proves that label bits and source bits cannot silently be treated as one numeric type.

## Axis

Using the verified binary matrix gives:

```text
rows:    6,10,8,7,6,6,5,4,9,9,7,8,7,9
columns: 8,10,8,10,8,7,3,6,7,5,9,6,6,8
```

Both lists contain 14 values, cover all 196 cells once and total 101, but their ordered values differ. The relevant creator hints contain no row, column, horizontal, vertical or axis directive. The verified spiral supplies an order for the earlier URL, not a summation axis.

## Missing source bindings

1. Cell domain: all 196 cells, the 24 visible colored cells, or the conditional 25-event frame.
2. Numeric type: binary encoding bit, color count, letter ordinal, RGB value, or another weight.
3. Axis: rows, columns, both, or the earlier spiral/octet grouping.

No parameter-free operation on the original square matrix can recover these choices. Continue only if an authored source supplies at least one missing binding.

Reproduction:

```bash
python3 -m tools.original_matrix_audit
python3 -m unittest tests.test_original_matrix_audit -v
```

Seven focused tests pass. No image variants, numeric-weight sweep, candidate material, private-key operation or AES operation occurred. Machine-readable evidence: `original-matrix-audit.json`.
