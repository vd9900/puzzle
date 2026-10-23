# GSMG puzzle — ideation brief (cycle 42). Read fully before proposing anything.

Public, unsolved Bitcoin puzzle (gsmg.io, 2019; prize 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe, ~1.25 BTC). Creator "Jrk Bgrt" (@SoWut).
Repo /home/vin/bitcoin_puzzle. Puzzle data: `scratch/common.py` (DBBI, FAED, Z1, Z2, BIN1, MATRIX, BLOBS, try_pw, evp; run with
system `python3`, not -I). Texts: research/artifacts/phase2.txt, phase3.txt, phase32.txt, phase32-beaufort.txt (speech),
phase32-checkerboard.txt. Image: research/sources/gsmg-puzzle.png. Page: research/sources/salphaseion.html.

## Solved chain (verified)
Phase 0: 14x14 black/white grid read in a counter-clockwise inward spiral (down first) = ASCII "gsmg.io/theseedisplanted"; the 24
coloured cells (15 blue, 9 yellow) sit exactly on the LSB of each byte (blue=1, yellow=0); one near-white #FEFEFE cell at (7,4).
Phase 1: song lyric (Logic "The Warning") -> Phase 2 (AES, password sha256("causality")) -> Phase 3 (7-part answer concatenation,
sha256 hex) -> Phase 3.2 (sha256("jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple")): Architect speech in a
Beaufort block (key THEMATRIXHASYOU, cp1141), a VIC straddling-checkerboard digit stream ("in case you manage to crack this the
private keys belong to half and better half and they also need funds to live"), and an UNSOLVED 80-byte AES blob ("inner").
SalPhaseIon page (sha256 of the first image's text "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9...") contains, in order:
`dbbi…`(91 letters a-i) | binary a/b (104 bits) = "matrixsumlist" | `faed…`(570 letters a-i) | z "lastwordsbeforearchichoice"
z "thispassword" z "shabefourfirsthintisyourlastcommand" + UNSOLVED 80-byte AES blob (binary "enter" embedded at its base64 line
break) + "shabefanstoo". Second textarea "Cosmic Duality": UNSOLVED 1328-byte AES blob. (Z1/Z2 decode by letters a=1..i=9,o=0 ->
one decimal integer -> hex -> ASCII.)
All AES: openssl enc -aes-256-cbc, EVP_BytesToKey(SHA-256,1 iter), password = lowercase sha256 hex of a lowercase answer.
Creator (screenshot DM): "Same software was used in every phase."

## Verified structure
- dbbi: tokenizing 'be' as one token, every prime logical position holds 'b' (=2=B, blue) or 'be' (=25=Y, yellow); these markers
  reproduce the image's colour sequence ("yellow blue primes"). Removing them leaves a 60-letter residual
  R60 = difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea. pi(91)=24 = #coloured cells; pi(570)=104 = #label bits.
- faed: letter counts g107 i75 e69 h58 f57 a54 c52 d49 b49; i.i.d.-like (no lag dependence); mildly non-stationary (change point
  at 538; last 32 letters contain no e/g). Bifid with a dbbi-keyed 5x5 square (full period) gives "btcseed…" — judged a
  coincidence (body indistinguishable from noise).
- Length feasibility: a 91- or 570-digit decimal number can never be lowercase text (top byte fixed by length).
- Cosmic Duality book (Time-Life 1991): cover yin-yang of two stars, one BLUE and one YELLOW ("scary specific" per creator).

## Creator hints (key ones, verbatim-ish)
Roses poem 2020: "Roses are White but often Red. Yellow has a number and so does Blue. Go back to the first puzzle piece…
the rabbits nest may contain a whole lot more. Hush hush." | 2021: "There is Another DOOR" | "prime numbers… required… some
characters need to be 'zeroed out'" | 2023 roadmap (binary, reversed): "yellow blue primes matrix sumlist last words before archi
choice yinyang — we won't give away the password, it's in front of your eyes but you're not seeing it, very last step is a true
give away, promised" | "once you hit yinyang, solved same day / 2 hours max" | "theory of everything is a valid path" |
2026: "My close friends have the best chance of solving it… NOTE: that is a hint"; SalPhaseIon "100% solvable"; asked whether
dbbi/faed are decoded or only an ingredient: 🤐; "our first hint is your last command": 🤐. Speech edits: "reinserting the prime
basics, after which you will be required to select from over twenty three ciphers, sixteen encryptions and/or seven intertwined
passwords to find the actual private key. note that also brute forcing might be required."

## EXHAUSTED (do NOT propose these or trivial variants)
z-method/decimal readings of dbbi/faed/residuals (all maps, zero disguise/insertion/deletion, prime zeroing, marker reinsertion,
bases 2-251, base-9/bijective, concatenations, prime-split streams); VIC (1.2M keys); single/double/keyed columnar, rail, spiral,
grille (coloured cells) transpositions; additive/running keys incl. all puzzle texts; Phase 3.2 checkerboard on dbbi/R60/faed;
Bifid/Trifid (all periods, many keys, CyberChef exact); Polybius sum/diff; 3x3 ternary regrouping; SalPhaseIon-letter substitution;
melodies (note names/scale degrees); digital-root known-plaintext vs 12M letters; book cipher vs Cosmic Duality; image forensics
(colours, QR raw codewords, PNG metadata) and page formatting; page versions (identical 2023-2026); btcseed body; matrix product
dbbi x label; sum lists (rows/cols, image/page blocks, 1.3M colour-prime + 10k block variants) as passwords; 6.3M roadmap token
concatenations; ~16k phrase passwords (Architect/Keymaker/Neo lines, speech end 'ciaobellao', roses poem, Fresco, Mr Robot,
book titles); door URLs; brainwallets; all community "decrypts" (padding false positives, ~1/256).

## Added after cycle 42 (also EXHAUSTED now)
- dbbi-style a1z26 tokens at prime positions replayed on faed (exact Viterbi, planted 98-100% recovery): negative.
- faed as windows of pi/e/phi/sqrt2/sqrt3/ln2 digits to 1e8 (g = 0|7): negative. faed as decimal printout of 48 puzzle byte objects: negative.
- Linear/affine recurrences (Berlekamp-Massey GF(3), orders 1-12 over GF(2/3/5)): random level.
- k, n-k, 2k, k/2 (x-coordinate oracle) of 508 chain-derived keys vs the prize public key: negative.
- Lo Shu magic-square ternary readings (all 8 symmetries): gibberish. Morse/Pollux/Morbit, Grandpre, homophonic digit-sum, Nihilist: negative.
- Conclusion so far: faed behaves like i.i.d. uniform decimal digits written a-i with g = {0,7} => ciphertext-like; its key is not derivable
  from the page by any tested method.
## Facts relevant to new ideas
- The prize address 1GSMG… is a VANITY address: creator: generating the GSMG vanity addresses took "few seconds", "Only 4 chars".
  So the prize private key is random (not a brainwallet/seed derivation); it must be stored somewhere (e.g. as a 64-hex plaintext:
  each 80-byte blob holds a 64-79-byte plaintext — a bare 64-hex string fits exactly).
- The creator is Dutch-speaking (he wrote "in Dutch its called 'geestverruimend'"). Language/cultural conventions are fair game; his
  identity/private life is NOT.
- The Phase 3.2 Architect speech text came from a 2003 fan transcript (jaced.com / onebee.com style), not the film audio.
- Creator: puzzle built in "a couple of hours", "I rushed (t)it", "Same software was used in every phase".
