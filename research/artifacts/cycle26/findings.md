# Cycle 26 findings — 2026-10-02

## Tested edge

`upstream 13×(7|8) fields → Bifid 38×(7|8) fields`

The test traces dependency units through the already recovered full-period Bifid transform. It does not generate candidate material or execute cryptography against any protected object.

## Result

The first rendered row is `btcseed|deoemcke`, but the cut at output offset7 bisects the `dd` Bifid digraph at offsets6–7. Both sides therefore depend on the same FAED pair, index3, comprising source offsets3 and288.

Because rendered width15 is odd, the same column cut alternates behavior: it splits a digraph in19 even-numbered rows and falls between digraphs in19 odd-numbered rows. The natural even and odd19×15 coordinate planes begin `bcedeec` and `tsedomk`, not `btcseed`.

Classifications:

- Shared width15 arithmetic tiling: **VERIFIED**.
- `btcseed` as serialized prefix: **VERIFIED**.
- `btcseed` as an independent seven-column Bifid field: **REJECTED**.
- Direct preservation of the upstream7|8 fields through Bifid: **REJECTED**.
- Any parameterized cross-field consumer: **UNKNOWN**.

The strongest surviving structural fact is shared width15, not a field-preserving data-flow edge. The missing edge still requires an authored cross-field action and downstream receiver.

```bash
python3 -m tools.bifid_field_boundary
python3 -m unittest tests.test_bifid_field_boundary -v
```
