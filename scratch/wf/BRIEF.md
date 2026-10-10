# GSMG 5 BTC puzzle — agent briefing (read fully before acting)

You are one agent in a multi-agent campaign to solve a public, unsolved Bitcoin puzzle
(https://privatekeys.pw/puzzles/gsmg-puzzle, creator "Jrk Bgrt"/@SoWut, launched April 2019).
Repo: /home/vin/bitcoin_puzzle. Your working dir for outputs: /home/vin/bitcoin_puzzle/scratch/wf/.
Shared Python tools live in /home/vin/bitcoin_puzzle/scratch/ (run them from that directory).

## Hard rules
- Never sign or broadcast a transaction. If any tool prints a private key or a decrypted plaintext that
  looks like a key, do NOT paste it into your report; it is already written to scratch/wf/HITS.log.
  Report only "HIT: blob=<name> kdf=<x> candidate=<text>" and the first 60 printable bytes.
- Website probing (gsmg.io): small curated sets only, max 60 per agent, 0.5 s spacing. Use oracle.py
  `--doors N` / `--forms N` rather than hand-rolled loops. Never probe other people's sites.
- Do not research private individuals (the creator's friends/family). Public puzzle material only.
- Do not re-run the exhausted families listed below; they have been done at scale.
- Return raw data, not prose for a human. Your final text (or StructuredOutput) is consumed by a script.

## Puzzle structure (all verified by reproduction)
1. **Phase 0**: puzzle.png = 14×14 black/white bit matrix read in a counter-clockwise inward spiral → ASCII
   `gsmg.io/theseedisplanted`. 24 coloured cells (15 blue, 9 yellow) sit on the last bit of each byte
   (blue=1, yellow=0); one near-white (#FEFEFE) cell at row 7 col 4. A QR encodes the target address URL.
2. **Phase 1**: page shows 8 icon tiles; hidden form POST /phase1verification; password =
   `theflowerblossomsthroughwhatseemstobeaconcretesurface` (lyric of Logic "The Warning", 1990).
   Redirects to /choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself
3. **Phase 2** page: AES-256-CBC (openssl `enc -aes-256-cbc -a`, password = sha256-hex of the answer, EVP_BytesToKey sha256 KDF by default).
   Blob 1 password sha256("causality") → text with a riddle table `# X 2 S H 4 Y 0 Q B 15 #` whose letters
   resolve (community) to S=32, B=25? /-42?, H=42, Q=82 (Mr Robot: SafeNet Luna HSM, eps3.4 runtime-error, Blowfish/Swordfish).
   Blob 2 password = sha256 of concatenated answers "causality" + "SafenetLunaHSM11110" + chess FEN + hex string (exact string in
   tools/gsmg.py PHASE3_PREIMAGE) → Phase 3 text.
4. **Phase 3** text (Merovingian/causality, Jacque Fresco, "giveit", Heisenberg) → password
   sha256("jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple") → **Phase 3.2** plaintext:
   Architect speech, "One for one, four for one.", a Beaufort-ciphered block (key THEMATRIXHASYOU, cp273/EBCDIC
   normalization) giving the long "yourlifeisthesumofaremainder..." speech (saved:
   research/artifacts/phase32-beaufort.txt), a VIC/straddling-checkerboard digit stream (alphabet
   `fubcdora/lethingkymvpszjqwx.`, escapes 1 and 4) giving
   `INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE`,
   a chess clue "Raising the stakes... fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as the first one seen",
   and an **UNSOLVED 80-byte AES blob** ("inner").
5. **SalPhaseIon page** gsmg.io/89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32
   (= sha256 of `GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`, found via the Decentraland audio hint
   HASHTHETEXT). Page text (letters a–i etc.) parses into:
   - `dbbi…` 91 symbols over a–i  (research: `scratch/common.py` DBBI)
   - binary `abba…` 104 bits → ASCII `matrixsumlist`
   - `faed…` 570 symbols over a–i (FAED)
   - z-delimited digit words → `lastwordsbeforearchichoice`, `thispassword` (via a=1..i=9, o=0, decimal→hex→ASCII)
   - `shabef our first hint is your last command` (shabef = sha256), an **UNSOLVED 80-byte AES blob** ("small"),
     binary → `enter`, then `shabef ans too`.
   - Second textarea "Cosmic Duality": **UNSOLVED 1328-byte AES blob** ("cosmic").
   Community-found: Bifid decrypt of FAED with square keyed by DBBI's first-occurrence order
   (`dbifhcegaklmnopqrstuvwxyz`, period 570) starts `btcseed...` then 563 noise-like letters. Not validated further.
6. **Target**: 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe (P2PKH; 5 BTC originally; ~2.5 BTC remain after creator spent some).
   Secondary: see tools/gsmg.py SECONDARY_ADDRESS.

## Creator hints (chronological, verbatim where known)
- 2019-04 (chat): sha256 hash of phase-2 password posted so people can test offline.
- 2019-05-29 on-chain: Decentraland estate 955 metadata set to name "gsmg.io magic puzzle piece",
  description "White Rabbits everywhere" (NEW, tested negative as password/door/form).
- 2020-01-14 hint image: poem "Roses are White but often Red, Yellow has a number and so does Blue" + grid.
- 2020-02-20: Decentraland screenshot at parcel -41,-17 (scene: cube question mark + text "GSMG.IO 5 BTC PUZZLE CHALLENGE",
  click plays puzzlepiece.mp3; stereo-invert spectrogram → hex 48 41 53 48 54 48 45 54 45 58 54 = HASHTHETEXT).
- 2021-03-01: "You are at the prime part already???" / "Ancient spelling. One of the many many typos."
- 2021-04-01: "R=18 A=1 B=2 ... Could also be 21 or 1812 bit".
- 2021-12-02: "There is Another D O O R" (acrostic). 2021-12-25: "prime numbers ... required to proceed ... some characters need to be 'zeroed out'".
- 2021-12-31: "The only date I give away is the expiry date of neo's passport" (Sept 11 2001 in The Matrix).
- 2022-12-11: a solver posted a page from the Time-Life book *Cosmic Duality* (Mysteries of the Unknown, 1991) — creator: "If the puzzle is solved you'll see how scary specific that is". 2023-01-08: "@barrystyle provided a very specific hint already (Cosmic Duality Book Page - Life and Death)".
- 2023-01-09: "At least prime number is very important to get any further." 2023-01-12: "Focussing on the theory of everything is also still a valid path to reaching the private key."
- 2023-02-23: a long binary dump posted by creator (see research/sources/maintained-hints__2023-02-23.png) — decoded by community (see repo).
- 2023-08-03: "Are you really looking for just the btc...?" 2023-08-06: creator said something was solved "rather remarkable" around then.
- 2024-04, 2026-01-01, 2026-07-12 hints: see research/sources/maintained-hints__*.png (2026-07-12: "My close friends have the best chance of solving it (a few tried). But they don't have the skills some of you do. NOTE: that is a hint.")
- Speech in Phase 3.2 says the solver must "return to the source codes ... reinserting the prime basics, after which you will be
  required to select from over twenty three ciphers, sixteen encryptions and or seven intertwined passwords to find the actual
  private key. note that also brute forcing might be required".

## Verified facts from this campaign (Oct 2026)
- dbbi: at every prime logical position (1-based) there is a `b` or `be` token; 0/5000 shuffles allow this. 15 lone `b` + 10 `be`
  = 15 blue + 9 yellow + 1 near-white. First 20 marker bits equal the image's blue/yellow spiral bits. Residual after removing
  markers: 60/61 symbols `difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea(e)` — undecoded.
- faed: statistically i.i.d. (no lag MI 1–30, no column keying ≤40, no pair structure); unigram peaked at g (18.8%), i (13%).
- gsmg.io: unknown paths → 404 body "Hello :-)". Phase 1 form: 302 on exact lyric, 404 otherwise.

## Exhausted families (negative; do not repeat)
Prime-position zeroing; keyed/spiral/rail/double columnar transpositions of faed (~38k, scored by a serial-structure detector
validated on the solved VIC stream); additive/running keys at all offsets; colour-prime matrix sum lists as passwords (1.3M);
roadmap-token sha256 concatenations (6.3M); ~11k phrase passwords (Architect/Keymaker lines, Roses poem formats, Mr Robot
HSM codes z1on0101/022350, MEGANIGMA, page tokens, PBKDF2 and sha1/sha512/md5 KDF variants); 544 door URL hashes; 316 form posts;
brainwallet sha256 of ~100 thematic phrases vs both addresses; ECDSA nonce reuse (community); Bifid/Trifid follow-ons on btcseed body.

## Tools
- `cd /home/vin/bitcoin_puzzle/scratch && python3 oracle.py --file CANDS.txt --label NAME [--doors 40] [--forms 40]`
  one candidate per line; tries raw + sha256hex + normalizations × 3 blobs × 2 KDFs. Prints `!!! STRUCTURED HIT` on success.
- `python3 fastcheck.py --file BIG.txt --procs 4 --label NAME` for ≥10k candidates (≈800k forms/min).
- `python3 -c "from common import *; ..."` exposes DBBI, FAED, MATRIX, BLOBS, try_pw(pw), letters_to_digits, primes_upto.
- `python3 bifid.py` reproduces the btcseed Bifid decode. `python3 serial.py` has hcond_z(digitstring) serial-structure score.
- Chat transcript: research/evidence/cycle02/_work__chat_transcript.txt (181k lines, 2019-04 → 2026-03).
  Pre-split chunks: scratch/chat_chunks/chunkNN.txt (raw) and chunkNN.filtered.txt (substantive messages only).
- Creator-only messages: research/evidence/cycle02/_work__creator_jrk.txt. Community README: research/sources/community-README.md,
  maintained README: research/sources/maintained-README.md. Hint screenshots: research/sources/maintained-hints__*.png (view with Read).
- Decentraland artifacts: scratch/wf/game.js, scene.json, gsmg_entity.json, txs.json.
- Internet access is available (curl, WebFetch, WebSearch).

## NEW (Oct 8 2026): creator's on-chain breadcrumb oracle — USE IT
The creator's wallet 3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK sent dust + OP_RETURN messages in 2020/2021 to the
*brainwallet addresses of stage passwords* (private key = sha256(password string), compressed P2PKH). Verified:
- "GSMG.io: Right, this is causality" -> 1Jqq37… = brainwallet("causality")
- "GSMG.io: are you sure?" -> 1AD2wf… = brainwallet(phase-1 lyric)
- "GSMG.io: You are here because 227 chars were correct" -> 1M5ypv… = brainwallet(227-char Phase 3 preimage)
- "GSMG.io: phase3.2 pass OK" -> 1K23RS… = brainwallet("jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple")
- "GSMG.io neighbors, half and double" -> 2P, P/2, P+G, P-G of the prize pubkey (no key leak)
UNEXPLAINED recipients (preimage unknown): 1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9 (2020-04-07, UNSPENT — nobody has found it),
1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff ("do you beleive me you need it?"), 18CchrjA3Uzfrzy4DFqao9ric6YfK4hjdc ("part of the cipher"),
13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp and 148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ ("Good job, Neo!", 2020-04-03).
Tool: `python3 bw_oracle.py --file CANDS.txt --label NAME` (same input format as oracle.py) checks sha256 / double-sha256 /
sha256-of-hex / hex-as-key derivations, compressed and uncompressed, against all of these. Run it on EVERY candidate file
you create, in addition to oracle.py. A match on 1NULY7… or the prize address is a solve-class event: stop and report.

## Added 2026-10-09
- Creator hint 2021-04-01 (creator_jrk.txt line 534): "another door might be found on {1 },{4} ,{21}" — same day as the R=18/A=1/B=2 joke; still unexplained.
- The Phase 2 table "# X 2 S H 4 Y 0 Q B 15 #" has exactly 10 tokens; the Phase 3.2 chess clue says "as wide as the first one seen" — a 10-column straddling checkerboard whose key row may be this table (numeric tokens at columns 1,4,6,9).
- Creator 2026-07-12: the 5 BTC "was never the actual prize, only a tiny fraction"; he "held quite a secret" to share. 2024-04-19: prizes are "a private key, some 'obscure' intel". 2023-08-06: salvation part passed "Partly".
- Already negative (do not repeat): all 218,812 substrings of dbbi/faed/residual as AES passwords; prefixes/suffixes as brainwallets; row/column sum lists at every width mapped to letters; the Phase 3.2 checkerboard applied to dbbi/faed; Neo's passport dates; the GSMG slogan.
