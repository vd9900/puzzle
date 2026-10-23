== DBBI
full lower 0 full print 0
b9 print>0.8 0
== RES60
full lower 0 full print 0
  b9 RES60 (0, 3, 2, 5, 4, 1, 7, 8, 6) 0.83 b'.V?\x88ILEPC|P_o%`WHLy\xd5\xb7\r\xa3P'
  b9 RES60 (1, 5, 2, 6, 0, 4, 7, 3, 8) 0.83 b'8\x89\n!\xdf,ogd\xd3<%*\x9aL{+#EuG4Q;'
  b9 RES60 (1, 8, 0, 7, 6, 3, 2, 4, 5) 0.83 b"=\xdf0Yp-}3I@P_CF,\xfd\\'+f\xfd#(\xf6"
  b9 RES60 (2, 7, 8, 4, 1, 6, 5, 3, 0) 0.92 b'!8[J[`h"|\xed%di \t\xealS5HwZW$'
  b9 RES60 (6, 0, 3, 5, 2, 4, 8, 1, 7) 0.83 b'/wl\x15FHg%+\xcfupzJRx\rP\x96|?\x879u'
  b9 RES60 (8, 4, 6, 1, 5, 3, 7, 0, 2) 0.83 b'\nC<7s\xfcJV\xf7zM\x1cU2\n@OsX*{\x88;L'
b9 print>0.8 6

## Main-loop deterministic checks (2026-10-13)
- First image: 5 grid colours; extra near-whites are (254,254,254) the known cell and (250,250,250) an identical texture in all three
  QR finder rings (generator artifact). QR fully decoded at codeword level (scratch/c37/image/qr_decode.py): ECI 26 (UTF-8) + byte
  segment (73 B, the blockchain.com URL) + terminator + standard EC 11 EC padding; RS syndromes zero. Nothing hidden.
- SalPhaseIon HTML: every separator a single space; no zero-width/non-ASCII, no comments, no trailing whitespace. robots.txt is
  figlet art "Follow the white rabbit". No formatting channel.
- Bit lengths of dbbi/residual/faed under decimal, base-9, bijective base-9: no meaningful sizes.
- Bifid in ENCRYPT direction at periods 5..570: nothing readable.
- dbbi (91) vs the 91-letter checkerboard sentence: 40 deterministic masks + 36 element-wise sums, quadgram z vs random controls:
  nothing readable (marker-letter selection 'ncsyang...' z=1.5, n.s.). scratch/c37/mask91/mask91.py
- Creator chat: the 2026-03-03 "Bingo" confirms a South Park quote, not a puzzle step; btcseed was shown to the creator on
  2026-03-03 and not confirmed; "yingyang" (the next phase) is unreached per creator (2025-04-28, 2026-03-03).
- faed change-point (scratch/c37/changepoint/cp.py): best unigram split k=538, G=33.3, max-scan p=0.004 (look-elsewhere included).
  The final 32 letters 'bccahhbiibibbibdcbahaidhfahiihic' contain no e and no g (longest e/g-free run elsewhere: 11).
  Fully corrected (any letter pair, suffix) p=0.019; any pair anywhere: faed also has a 49-run avoiding d,h at offset 63 (p~0.05).
  Windowed stationarity vs shuffles: w30 p=0.004 (0.006 without tail), w15/38/57/95 p~0.02-0.03 => faed is mildly
  NON-stationary; in a 19x30 view only row 18 (offset 540-569, chi2=22.8) is a strong outlier. Phase 3.2 board on the tail: gibberish.
- Length feasibility (from digit_codecs h7): lowercase z-method output is impossible for lengths 91, 61, 83, 570, 285, 538, 565;
  possible for 60, 56, 84, 104, 540 (540 digits -> 224 bytes = 7x32). faed[:540] (faed minus the anomalous final row) and cuts
  531-548 tested exhaustively top-down (scratch/c37/faed540/run.py): identity map with any single letter possibly 0 (240 runs,
  lower/lowsp/printnl/textish) and all bijections with zero merged into g/i/e: 0 solutions, 0 truncated; planted self-test OK.
- faed tail windows faed[s:570], s=520..544, z-method with 0-4 reinserted zeros or single-letter zero disguise, charsets
  lower/lowsp/printnl/textish/hex: 0 solutions, 0 truncated (scratch/c37/faed540/tail.py). The tail anomaly is not z-method text.
- Caveat: scratch/c37/mask91/mask91.py scored with the contaminated quadgram model; conclusion unaffected (real vs random masks of
  the same sentence share the bias, and all outputs are visibly non-text), but re-score with quad_indep.py if revisited.
