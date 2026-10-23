# matrixsumlist (cycle 37) — saved by main loop (agent could not write the file)
All negative; deterministic decodes/structure tests only, planted self-tests + shuffled/random controls; no AES oracle.
T1 dbbi (+,-,mask,zero) its own label bit-matrix -> z-method, 372 decodes: best printable 0.667 vs control max 0.684.
T2 row/col sum lists of faed/dbbi/res60 at every width as bytes / decimal z-method / mod 10: real = control.
T3 580 image "matrix sum" sequences (neighbour counts, window sums, prefix sums, spiral counts, colour coords) vs page strings by LCS: <= control median.
T4a Bifid/body/faed sum lists as BIP39 indices: 3 checksum passes vs 3.4 expected.  T4b Bifid pairs as base-100 (detector bug fixed): matched by controls.
T5 faed as 190 COO (row,col,value) triples summed into 9x9 -> letters: below control p99.
T6/T6b dbbi/res60 as digit-reduced sum lists of faed at widths 2..285: chance (res60 run 8, p~0.18).
T7/T7b split at 285: p=0.019 driven by the 538 tail (p=0.144 without it) — not a Bifid split.
T8 prime-marker scheme continuing into faed: p=0.68.  T9 Minesweeper-number inversion (bug fixed): 0/1 fraction below control.
T10 image sum lists (weights for yellow/blue/near-white) via z-method, 6332 decodes: at control level.
T11 colour-cell coordinate lists via z-method, 696 decodes: negative; "fefefe square is 101 010" matches no indexing.
Untested: T9 for non-invertible shapes (ILP/lattice); sum list as AES password (skipped per user directive).
