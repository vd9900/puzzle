# Exact pipeline map — cycle 02

The parameter-complete machine-readable map is `artifacts/cycle02/pipeline.json`. It records 13 stages: 8 VERIFIED, 1 LIKELY, 4 UNKNOWN. VERIFIED applies to observed intermediate outputs, **not** to a final Bitcoin solution.

## Main route

`gsmg-puzzle.png` → dominant-cell color bits → counterclockwise down-first spiral → MSB-first ASCII URL → hidden-form page → documented lyric password (**POST not replayed**) → primary `phase2.html` → SHA256(causality) hex password → AES-256-CBC text → exact seven-component password preimage → SHA256 hex → AES-256-CBC Phase 3 → exact Fresco/Alice/Heisenberg preimage → SHA256 hex → AES-256-CBC Phase 3.2 → raw byte encoding repair → Beaufort speech / checkerboard clue → **inner AES UNKNOWN**.

## Alternate route

Archived Decentraland MP3 → left minus right channel → logarithmic spectrogram → hex transcription → HASHTHETEXT → normalized initial image title + target address → SHA256 lowercase-hex route → primary SalPhaseIon page → binary tokens / decimal-to-hex tokens → **91/570-letter segments and small/Cosmic AES UNKNOWN**.

## Confirmed AES parameters

All three confirmed layers use AES-256-CBC, 16-byte PKCS#7 padding, OpenSSL `Salted__` framing, an 8-byte salt, **EVP_BytesToKey SHA-256 with count=1**. Passwords are the **ASCII lowercase hexadecimal SHA-256** of the preimage, **not** the raw 32-byte digest. No trailing newline is added.

`D_i=SHA256(D_(i-1)||password||salt)`, `D_0=empty`; concatenate until 48 bytes; take the first 32 as AES key and next 16 as IV. There is no integer-endian conversion. Exact KEY/IV values are emitted only for already-solved public stages in the JSON map.

| Stage | Salt | Ciphertext Bytes | Plaintext Bytes |
| --- | --- | ---: | ---: |
| Phase 2 | `06286612d43ed7ed` | 656 | 648 |
| Phase 3 | `9fbc451d13d071f4` | 4096 | 4090 |
| Phase 3.2 | `eefc4c5befc1656a` | 2432 | 2422 |

Phase 3.2 plaintext is **not UTF-8**. Preserve exact bytes/CRLF. The 1539-byte symbol block converts from Latin-1 characters to cp273 bytes, yielding a-z; this observed alphabet is consistent with the documented cp1141 mapping. The transformation is verified on these bytes, not asserted as universal equivalence between encodings. Beaufort uses `P=(K-C) mod26`, repeated keyword THEMATRIXHASYOU. Checkerboard decoding uses the exact 28-symbol alphabet `fubcdora/lethingkymvpszjqwx.`, prefixes 1/4, and round-trips 149 digits exactly.

## Unsolved cryptographic parameters

| Target | Verified Salt | Ciphertext Bytes | Unproven Assumptions |
| --- | --- | ---: | --- |
| Phase 3.2 inner | `b45a5e3d827593ca` | 80 | AES-256-CBC/legacy EVP/PKCS#7 inferred by precedent; password/digest/IV UNKNOWN |
| SalPhaseIon small | `3ab585348552415d` | 80 | Same; reproducing random-looking MD5 output is not a verified intended decrypt |
| Cosmic Duality | `2d3f6fe06dc950e6` | 1328 | Same; no intended successful decryption established |

Tests explicitly try MD5/SHA256 EVP count=1, observed salts, CBC and PKCS#7. This is a bounded hypothesis family, not proof that the original construction must use those parameters.

## Cycle 03 structural branch

`SalPhaseIon dbbi91 → optional be tokenizer(mask1017) →83 one-based logical positions →prime b/be markers` continues into the unedited104-letter binary `matrixsumlist` clue. Its a=0/b=1 encoding supplies primes89/97 =1/0; all25 special image-color events match under near-white=1. Source bytes, mappings, positions, exhaustive alternatives and reset controls: `artifacts/cycle03/prime-boundary.json`. This branch is PROMISING, not a solved cipher/key; the parameter-complete13-stage cycle02 map remains preserved unchanged.
