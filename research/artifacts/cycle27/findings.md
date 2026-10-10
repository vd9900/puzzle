# Cycle 27 findings — 2026-10-02

## Architecture discriminator

The proposed chain incorrectly assumes that `residual60` must produce `faed570`. Existing exact dependencies instead form two branches:

```text
residual60 + first23 event labels
              │
              ▼
            dbbi91 ──► source-keyed square25 ─┐
                                              ├─► Bifid570 ─► btcseed + body
                                   faed570 ───┘

raw matrixsumlist104 ─► decoded instruction ─► UNKNOWN
full Bifid570 ────────────────────────────────► UNKNOWN receiver
```

The frozen residual/event join reconstructs all91 dbbi letters. Seven first-occurrence square symbols come from residual tokens and two from event labels; the remaining16 square symbols are the fixed alphabet supplement. FAED supplies all570 text symbols, and the Bifid transform round-trips exactly.

`residual60 = 4×15` is true but does not create a source axis. Its row-major reflow appears nowhere as a complete substring or exact row in FAED, rendered Bifid, or either coordinate plane. Zero of15 reflow columns preserve a logical/raw width15 source column, and only one accidentally preserves an original dbbi width7 column.

## Classification change

- Serial `residual60 → faed570`: **WEAK and unnecessary**; direct identity/row/axis-preserving forms are **REJECTED**, broader authored transform remains **UNKNOWN**.
- Parallel convergence at Bifid: **STRONGLY SUPPORTED**.
- `matrixsumlist` semantics → consumer: **UNKNOWN**.
- Full Bifid570 → downstream receiver: **UNKNOWN**.

The missing data flow is therefore downstream of the decoded instruction and full Bifid output. It is not a required residual-to-FAED conversion. No further parameter-free transform is licensed by the preserved objects.

```bash
python3 -m tools.residual_faed_topology
python3 -m unittest tests.test_residual_faed_topology -v
```
