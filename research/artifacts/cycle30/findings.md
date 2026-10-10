# Cycle 30 findings — Bifid sum-axis topology

## Correction to the post-Bifid edge

Cycle29 established that a post-Bifid reduction can produce15 items, but it treated the serialized output as an ordinary `38×15` matrix. That view does not preserve Bifid's actual dependency cells.

The natural Bifid layout is two `19×15` coordinate planes. Pairing corresponding columns of those planes creates15 groups of38 symbols. Every group depends on exactly one FAED source column and all570 output symbols are covered once:

```text
FAED upper19×15 ─┐
                 ├─ cellwise Bifid ─► even19×15 + odd19×15
FAED lower19×15 ─┘                              │
                                               └─ pair corresponding columns
                                                               │
                                                               ▼
                                                         15 groups ×38
```

By contrast, each column of the serialized `38×15` output mixes two FAED source columns. Zero of15 serialized columns retains a single source-column lineage. The plane-paired axis is therefore **STRONGLY SUPPORTED structurally**, while serialized-column reduction is **WEAK**.

## Prior-family equivalence

Each group was represented as a formal25-component letter-count vector. This describes an additive sum without choosing numeric weights.

- No plane-paired output group equals any raw-FAED width15 column.
- No plane-paired output group equals any raw-FAED width38 row.
- No serialized output group equals any of those raw-FAED groups.
- No plane-paired group equals any serialized-output group.

There are zero exact matches across all pairwise comparisons, including reorder-only comparison. Thus the post-Bifid route is not an exact formal repeat of the preserved raw-FAED sum campaign. A specially chosen numeric map could still cause collisions; none was selected or tested.

## Refined missing edge

```text
decoded matrixsumlist semantics
              +
paired columns of Bifid even/odd19×15 planes
              │
              ▼
      unknown15-item receiver
```

The unresolved interface is now the symbol weighting and receiver, rather than the matrix axis. No source evidence establishes that these groups should be numeric sums, BIP39 indices, or any other concrete format.

No numeric sum vector, candidate list, mnemonic word, checksum, seed, private key, or AES operation was generated.

```bash
python3 -m tools.bifid_sum_axis_topology
python3 -m unittest tests.test_bifid_sum_axis_topology -v
```
