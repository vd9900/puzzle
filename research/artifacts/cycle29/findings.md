# Cycle 29 findings — post-Bifid sum-list preflight

## Missing data-flow edge

The remaining untested relationship is:

```text
decoded matrixsumlist instruction
              │
              ▼
recovered Bifid570 as 38×15 ── column reduction ──► 15-item receiver
                                                        │
                                                        └─ possible seed interface
```

This is more specific than the old `matrixsumlist → UNKNOWN` and `Bifid570 → UNKNOWN` exits: it proposes that the two exits join. It also differs from the preserved secondary campaign, which summed **raw FAED570**, not recovered Bifid570.

## Requested edge classification

| Edge | Status | Evidence |
|---|---|---|
| `dbbi91 → matrixsumlist` | **UNKNOWN** | They form an exact reversible `13×7 + 13×8 → 13×15` rowwise interface, but no operation establishes a causal edge. |
| `matrixsumlist → 25-event prime/color` | **WEAK** | Two continued prime markers occur in the raw label, while creator-attributed instruction order places prime/color work before the decoded label. |
| `25-event prime/color → residual60` | **STRONGLY SUPPORTED** | The frozen first23 event labels occupy the prime positions and their complement is exactly60 logical tokens. |
| `residual60 → faed570` | **REJECTED** as a direct serial edge | The residual/event branch reconstructs `dbbi91` and the Bifid square; FAED is an independent Bifid text input. Direct identity, row, and inherited-axis forms failed. |
| `faed570 → source-keyed Bifid570` | **STRONGLY SUPPORTED** | The fixed square and full-period transform are exact and reversible and produce the recognized prefix. Primary authorship of the operation remains unproved. |
| `Bifid570 → btcseed prefix` | **VERIFIED** | The deterministic output begins with literal `btcseed`. |
| `btcseed prefix → remaining Bifid body` | **UNKNOWN** | The prefix is a recognition/type marker; it provides no demonstrated operation on the remaining563 symbols. |
| `remaining Bifid body → unknown downstream interface` | **UNKNOWN** | No receiver, numeric map, orientation, normalization, or checksum instruction is authored. |

## Single highest-information structural experiment

`C29-BIFID-SUMLIST-BIP39-PREFLIGHT` compares two architectures without computing any candidate values:

1. **Direct serialization:** literal prefix/body/full output is a standard seed object. Cycle28 rejects this by BIP39/BIP32 format contracts.
2. **Post-Bifid reduction:** `matrixsumlist` acts on the complete `38×15` Bifid matrix, producing one item per column. This yields exactly15 items, a valid BIP39 mnemonic length, and joins both previously unknown exits.

The second architecture is **dimensionally compatible**, but remains **INCONCLUSIVE**. Nine canonical public-symbol encodings all have theoretical 38-row sum bounds inside the BIP39 index domain `0..2047`. Range analysis therefore cannot choose a mapping or establish BIP39 intent.

The related secondary script `solver/faed_matrix_sum_attack.py` was inspected as source only. Its BIP39 branch uses raw FAED split into fifteen rows of38 and then performs checksum/wallet operations. It does not use recovered Bifid570 as the sum-matrix operand. The post-Bifid stage is therefore genuinely untested, although it belongs to the same high-level matrix-sum/BIP39 family.

## Exact stopping point

The next discriminator would have to instantiate the fifteen numeric values and evaluate a receiver constraint such as a BIP39 checksum. That would create/test mnemonic candidate material, which this phase explicitly prohibits. It is also underdetermined because the source does not choose:

- raw FAED versus recovered Bifid as operand;
- symbol-to-number mapping;
- coordinate origin or matrix orientation;
- direct indices versus normalization;
- BIP39 versus another 15-item receiver.

No candidate list, mnemonic word, checksum test, seed derivation, private-key operation, or AES operation was performed.

```bash
python3 -m tools.bifid_sumlist_bip39_preflight
python3 -m unittest tests.test_bifid_sumlist_bip39_preflight -v
```
