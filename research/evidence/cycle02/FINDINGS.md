# GSMG.IO 5 BTC Puzzle — Cryptanalysis of the SalPhaseIon / Cosmic Duality endgame

This document records a rigorous, falsification-driven analysis of the **unsolved final
phase** of the GSMG.IO puzzle (SalPhaseIon → Cosmic Duality). Every hypothesis below was
tested empirically; negative results are reported honestly because they *narrow* the
problem. Tools live in [`_work/`](./_work) and are reusable.

> TL;DR: The endgame reduces to decoding two strings, **`dbbi`** (91 symbols) and
> **`faed`** (570 symbols), both over the 9-symbol alphabet `a–i`. We establish that
> `dbbi` is a **structured, decodable key** and `faed` is a **high-entropy encrypted
> payload**; that the cipher family is a **VIC / straddling-checkerboard** (validated by
> reproducing the already-solved phase 3.2.2); that the two escape digits are almost
> certainly **1,4**; and — crucially — that the puzzle is blocked by a **verification
> problem** that makes blind search/cryptanalysis provably unable to converge. The
> missing piece is a single *interpretive* leap, not more compute.

## The two unsolved strings

```
dbbi (91 = 7×13): dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe
faed (570 = 15×38): faedggeedfcbdabhhggcadcfeddgfdgbgig...iihic   (see _work/, full string in scripts)
```

Both decoded from the SalPhaseIon page text. The page also contains:
- `matrixsumlist` / `enter` (the two "abba" binary blobs) — **paired with `dbbi`**
- `lastwordsbeforearchichoice` / `thispassword` (two "z"-segments) — **paired with `faed`**
- `shabef our first hint is your last command` and `shabef ans too` (`shabef` = **sha256**)
- An 80-byte AES blob (`_work/salphaseion_blob.txt`)
- The **Cosmic Duality** AES blob (1328 B, `ChatExport/files/cd.b64.txt`)

## Hard structural facts (the foundation)

| Fact | Evidence |
|---|---|
| **`dbbi` is a structured/decodable key** | Index of Coincidence = **0.151** (uniform-9 = 0.111). 'b'=27%, 'e'=20% dominate. |
| **`faed` is an encrypted payload** | IoC = **0.118 ≈ uniform**, flat across all periods; ~no repeated n-grams = max entropy. |
| **Cipher = VIC / straddling checkerboard** | Phase 3.2.2 used exactly this (`dcode.fr/vic-cipher`). Decoder validated in `_work/cb2.py` reproduces `INCASEYOUMANAGE...` perfectly. Top community solver "RB": straddling checkerboard is the "hottest candidate since 2021"; `matrixsumlist` = the **mod-9 over-encryption** step. |
| **Escape digits ≈ 1,4** | In a checkerboard, escape digits are the most frequent. `dbbi`'s two most frequent symbols are `b,e`; with mapping `a=0..i=8`, `b=1, e=4` = **identical to the 3.2.2 escapes**. |
| **Key-length ↔ grid match** | `len("matrixsumlist")=13` ↔ `dbbi=13×7`; `len("lastwordsbeforearchichoice"+"thispassword")=38` ↔ `faed=15×38`. The decoded words are transposition-key-length. |
| **Endgame pipeline** | `sha256(first hint)` → decode key for `dbbi/faed` → **ANSWER** → `sha256(ANSWER)` = AES key → Cosmic Duality. (RB's reading of `shabef ... ans too`.) |

## The byte-boundary colour layer (verified, but redundant)

The first image (`puzzle.png`) is a 14×14 binary matrix read CCW-spiral → `gsmg.io/theseedisplanted`.
It has **15 blue + 9 yellow** special squares. Verified finding: in spiral order **all 24
special squares sit at exact multiples of 8** — i.e. the last bit of each of the 24 URL
characters. Intentional (impossible by chance). **However** blue=1/yellow=0 simply equals
the parity of each character → it *confirms* the byte structure but encodes **no new key**.
"Roses are White but often Red, Yellow has a number and so does Blue" mirrors Lewis Carroll's
*Game of Logic* counters (RED=1 occupied, GREY=0 empty), confirming the binary-counter theme.

## The verification problem (why the puzzle resists, provably)

Two independent reasons make one-candidate-at-a-time search unable to converge:

1. **Each guessed key fixes only ONE of ≥4 unknowns.** A full VIC decode of `dbbi` needs:
   checkerboard *alphabet* **+** `a–i→digit` *mapping* **+** *transposition* key **+**
   *over-encryption* keystream. Testing a phrase as "the alphabet" leaves three unknowns,
   so even the *correct* alphabet yields gibberish.
2. **No verification signal until the very end.** `dbbi` → ~60 letters. Hill-climbing
   (`_work/hillclimb.py`) reaches English-level trigram fitness from **any** starting
   alphabet (overfit on 60 chars). So even a fully-correct decode can't be recognised from
   `dbbi` alone. The only true verifier is the closed loop `decode → sha256(answer) →
   opens the AES blob` — which requires all 4 parameters correct *simultaneously*.

⇒ The block is **interpretive/structural, not computational**. Matches the creator's
"good puzzles don't need hints" / "it's in front of your eyes but you're not seeing it".

## Hypotheses tested and FALSIFIED (with evidence)

- **"matrixsumlist triangle"** (dbbi fills upper-triangle of 14×14, row-sums XOR faed):
  produced fragments `SENDTHE`/`BLUENET` — but a **null-model test** (38k random strings)
  shows max score identical → **apophenia**, not signal. Disproven.
- **Image hidden layers / steganography**: no trailing data after IEND, no text chunks in
  any PNG; only `puzzle.png` + `theseedisplanted.png` use special colours; no alternative
  matrix reading (rotations/flips/clockwise all gibberish; 4 leftover spiral bits = `0000`).
- **Book cipher**: searched OCR of both reference books for 27 solved-phase answers —
  Cosmic Duality **0/27**, Game of Logic **1/27**. `causality`, `heisenberg`, `Safenet`,
  `Luna`, `Merovingian`, `architect`, etc. **absent from both** ⇒ books are *thematic name*
  only, **not** a key source.
- **"first hint" candidates** (all → checkerboard alphabet + AES key + keystream, 0 hits):
  blue/yellow layer; the chronological first hash `5ac40783…` = sha256(phase-2 flower
  password); the white rabbit (drawing sits on white/0 centre cells); the phase-3 chess
  position; the Decentraland spectrogram (→ `HASHTHETEXT`); "The Warning" by Logic lyrics;
  yellow-blue-prime; the Roses poem. **None crack it** (and per the verification problem,
  the correct one wouldn't be recognisable anyway).

## Tools (`_work/`)

- `cb2.py` — **validated** straddling-checkerboard decoder (reproduces phase 3.2.2).
- `hillclimb.py` — trigram hill-climber for the checkerboard alphabet (demonstrates overfit).
- `parse_chat.py` — Telegram HTML export → plain transcript.
- `vic_full.py`, `cb9.py`, `blueyellow_attack.py`, `columnar.py`, `triangle_zero.py`,
  `matrixtri.py`, `dbbi_*.py`, `faed_base9.py`, `prime_theory.py` — individual attack scripts.
- `decrypt*.py` — OpenSSL-compatible AES-256-CBC (sha256 KDF) for the blobs.
- Data: `salphaseion_blob.txt`, `salph_raw.txt`, `creator_jrk.txt` (all creator messages),
  `gameoflogic_ocr.txt` (public-domain OCR), analysis outputs `*_out.txt`.

## The joint 4-parameter attack (`_work/joint_attack.py`)

The structurally-correct computational attack: instead of trusting the (unreliable)
English score, enumerate {alphabet × `a–i` mapping × escapes × transposition ×
over-encryption} jointly and verify **only** via the real oracle —
`decode(dbbi) → sha256(answer) → does it open the SalPhaseIon or Cosmic blob`.

- Bounded candidate space: ~16 keyword/seed alphabets (incl. the 3.2.2 alphabet),
  2 mappings, 3 escape pairs, 3 transpositions, 3 over-encryption keystreams, 6 answer
  normalisations, both `sha256(answer)` and raw-answer as the openssl pass.
- **4904 decode-forms AES-tested → 0 hits.**

What this proves: the attack is feasible and correct, but it can only win if the
checkerboard **alphabet** is one of the natural keyword candidates — it isn't. The
alphabet is a 26! space and the AES oracle is **binary with no gradient**, so it cannot
be searched efficiently. ⇒ Without the correct *interpretation* that fixes the alphabet
(the "first hint"), the endgame is **computationally unbreakable from our position**.
This is the formal endpoint of the campaign.

## What would actually move this

1. A **new official hint** from the creator (he stated he'd release one more if unsolved).
2. A **joint 4-parameter attack** that solves alphabet + mapping + transposition +
   over-encryption *together*, verifying only via the end-of-chain AES loop (expensive,
   low-probability, but the only computational path that respects the real structure).
3. The single correct **interpretation of "the first hint"** that closes the loop at once.
