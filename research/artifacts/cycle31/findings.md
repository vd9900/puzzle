# Cycle 31 findings — matrix/Bifid dependency join

The exact shared width15 does **not** create a columnwise data-flow edge from the inferred upstream `13×15` panel into the post-Bifid groups.

## Dependency result

- `dbbi91` contributes the nine first-occurrence symbols used to build the global Bifid square. Those positions occur in upstream dbbi columns0–5; column6 contributes no first occurrence.
- Every one of the15 FAED source columns contains all nine input symbols `a`–`i`. Consequently every paired Bifid output group uses the same global square dependency.
- FAED source column `c` maps locally to paired Bifid group `c` for all15 columns.
- The eight raw `matrixsumlist` bit columns have zero data dependencies in the recovered Bifid transform.
- Zero downstream groups have an exclusive same-index dependency on the corresponding upstream `dbbi|label` panel column.

The graph is therefore:

```text
dbbi91 ─► one global square ───────────────┐
                                           ├─► all15 paired Bifid groups
FAED column c ─► Bifid group c ───────────┘

raw label104 ─► literal matrixsumlist ──?──► unknown semantic operation
```

The rowwise `13×15` join remains a verified reversible geometry. Its direct column-to-column promotion is **REJECTED**. The decoded label may still control a later operation, but that would be a semantic instruction edge rather than inherited numeric data.

## Exact blocker

The public objects do not specify:

- which matrix `matrixsumlist` names;
- how its symbols become numbers;
- whether a sum is actually required;
- which receiver consumes a resulting15-item object.

No further parameter-free operation follows from width or dependency alone. No numeric sum, mapping trial, candidate list, mnemonic word, checksum, seed, private key, or AES operation was generated.

```bash
python3 -m tools.matrix_bifid_dependency_join
python3 -m unittest tests.test_matrix_bifid_dependency_join -v
```
