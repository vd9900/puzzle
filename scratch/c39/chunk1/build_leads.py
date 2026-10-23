import json
L = []
def add(msg_ids, author, date, claim, kind, checkable, reaction, local_check=None):
    d = {"id": f"C1-{len(L)+1:02d}", "msg_ids": msg_ids, "author": author, "date": date,
         "claim": claim, "kind": kind, "checkable": checkable, "reaction": reaction}
    if local_check: d["local_check_c39"] = local_check
    L.append(d)

add([65298], "Diego Schmidt", "2026-06-11",
    "SalPhaseIon instruction string 'matrixsumlistlastwordsbeforearchichoicethispasswordshabefourfirsthintisyourlastcommandentershabefanstoo' is exactly 103 chars; written row-by-row into the 14x14 grid its last char lands exactly on the FEFEFE (near-white) cell. Truncating the btcseed Bifid output at the first 'del' ('last command' = DEL) leaves 93 chars; 103+93 = 196 = 14x14.",
    "data_artifact", True, "No direct rebuttal; author says it may be coincidence. Token selection (which SalPhaseIon pieces are concatenated, 'del' cut) is post-hoc; btcseed itself judged coincidence in cycle 37.",
    "VERIFIED: FEFEFE at (row 7, col 4) 0-based = row-major index 102 (103rd cell); spiral index 163. 'del' first at index 93 of btcseed string. Lengths 103 and 93 confirmed.")
add([65299, 65305], "Diego Schmidt", "2026-06-11",
    "Delete the row and column containing FEFEFE -> 13x13 binary matrix; total = 89 (24th prime; 9 yellow + 15 blue = 24 colored cells). Row sums [6,10,7,6,6,5,4,8,8,7,8,6,8], column sums [7,9,7,10,7,3,6,7,5,8,6,6,8]; 26 sums = len('lastwordsbeforearchichoice').",
    "data_artifact", True, "Denis Golovkin asked 'why?'; author calls it probably coincidence. Pure numerology, no decode.",
    "VERIFIED: sub-matrix sum 89, row and column sum lists match exactly.")
add([65938, 65939], "Denis Golovkin", "2026-06-25",
    "Cut out the colored (yellow+blue) cells of the 14x14 grid -> a valid turning-grille (Cardan) mask: the 24 cells never overlap under the four 90-degree rotations.",
    "data_artifact", True, "No rebuttal in chat.",
    "VERIFIED true (also with FEFEFE added). Random 24-cell sets pass only 0.49% of the time, BUT the property is automatic here: all colored cells sit at spiral index = 7 mod 8 and every spiral ring has odd quarter-length (13,11,9,7,5,3), so rotations can never hit another colored cell. Not independent evidence of a grille.")
add([64497, 64503], "Whore Amazing", "2026-06-03",
    "Yellow/blue cells are just byte boundaries of the phase-1 bit string (the colors carry no separate cipher).",
    "data_artifact", True, "Sparky 64506: matrix could still be an XOR key; Denis argues multi-message encoding.",
    "VERIFIED: colored cells are exactly the 24 cells at spiral indices 7,15,...,191 (last bit of each ASCII byte of 'gsmg.io/theseedisplanted'); yellow = bit 0 (9 cells), blue = bit 1 (15 cells), i.e. they mark each character's LSB.")
add([64374, 64502, 64509, 64515, 64516, 64530, 65309, 65492], "Denis Golovkin / Sparky", "2026-05-30",
    "dbbi tokenizes into 'b' and 'be' markers on prime indices (count each 'be' as one index); the b/be sequence reproduces the rabbit grid's yellow/blue order for the first ~20 (Denis) to 23 (Sparky) bits; the off-white (FEFEFE) cell signals use as blue. Sparky: 0 of 300,000,000 shuffles of dbbi admit a valid prime-marker parse plus color match. Denis also claims the same 24-bit sequence appears in a JFK executive order (5 bits) and elsewhere.",
    "data_artifact", True, "Whore Amazing 64504/64517: coincidence/pareidolia; Sparky and Denis argue design (p ~2^-20 per Denis, smaller per Sparky). Denis 64375: 'solid as rock, yet useless' (no next step known).")
add([65336, 65363, 65364], "Diego Schmidt (+gnosis, Denis)", "2026-06-11",
    "Chars of the decoded URL at yellow positions = '.thdplntd' (ords 46,116,104,100,112,108,110,116,100); chars of the URL whose ASCII code is prime = 'gmg/eeeae'. Pairwise rule 'blue<yellow -> 1' gives 011111110 -> 0x7F (DEL) / 0xFE. gnosis: 'eeeae' = 'the seed is planted' minus all other letters; Denis: also the ending of dbbi once 'be'->'e'.",
    "data_artifact", True, "No rebuttal; the comparison rule is ad hoc (labelled 'blue primes' but it is prime-ASCII chars, not blue cells).",
    "VERIFIED both strings: '.thdplntd' = URL chars at the 9 yellow bytes; 'gmg/eeeae' = URL chars with prime ASCII code.")
add([65082, 65083, 65214], "Artem", "2026-06-09",
    "Flip the FEFEFE cell 0->1: over GF(2) the 14x14 matrix then has rank 12 (row13 = R2^R6^R8^R10^R11^R12, row14 = R1^R4^R5^R6^R8^R11^R12, 1-based; similar column dependencies). Removing independent rows 3,7,9 and columns 1,3,13 leaves 11x11; rows as 11-bit BIP39 indices give 'famous soldier peace method ginger parrot vessel screen skirt vintage repair', columns give 'jelly slight comic liquid expire expect skin carry tortoise radar help'; suggests brute-forcing a 12th word.",
    "method", True, "Denis 65214: 'true once we flip FE block'. gnosis/X 65084-65093: creator says prize is a raw private key; vanity generators do not produce mnemonics. Row/column removal choice is arbitrary.",
    "VERIFIED rank: 13 for the original matrix, 12 with FE flipped. Baseline: a random 14x14 GF(2) matrix has rank <=12 about 13% of the time, so not significant. Mnemonic test would be a last-word guessing loop; not run.")
add([63701], "Artem", "2026-05-24",
    "The grid contains exactly 101 ones; 101b = 5, shifting the binary point gives 10.1b = 2.5 and 1.01b = 1.25 (the halving prize amounts).",
    "data_artifact", True, "No rebuttal; numerology.", "VERIFIED: 101 ones (black+blue).")
add([63504, 63505, 63515, 63520, 63521, 63522, 63528, 63540, 63541, 65724, 65735], "X", "2026-05-22",
    "Produces 'JLIQFOPGVBLSENDTHECZAGJJYDSWCGUDJNFTWB' from dbbi+faed: dbbi row sums (7x13 layout) form a repeating key; faed (570 = 38x15) split into 38 rows of 15 letters, each row summed; XOR the row sums with the key; zero-masks from the yellow/blue positions of the 14x14 matrix reveal 'SENDTHE', 'BLUE', 'TOSETHEX' (read as 'SEND THE BLUE(NET) TO SET HEX'). Script posted on ideone (not visited).",
    "decode_result", False, "Sparky 63521: 7x13 vs 38x15 size mismatch unexplained; Denis 63522/63528: repetitive output follows from sums of 13 digits clustering in a narrow range, 'another heavy coincidence'; Vasilis 65629 later calls the 'set hex' readings curve-fit/dead.")
add([63653, 63664, 63674], "Sparky", "2026-05-24",
    "'From 14x14 grid + yinyang + yellowblueprimes + matrixsumlist' obtains 'IARLCOWMUGXRIA' (reversed 'AIRXGUMWOCLRAI').",
    "decode_result", False, "Author: 'might be nothing'; method never specified.")
add([64669, 64701, 64678, 64704, 64709, 64712, 64713, 64717, 65492, 65515, 65517, 65672], "Flo Sku / gnosis (orig. X)", "2026-06-07",
    "btcseed: CyberChef Bifid_Cipher_Decode('dbifhceg') on faed (key = dbbi letters de-duplicated in order; CyberChef ignores period, i.e. period 570) gives 'btcseeddeoemckeadhbschdkbdcsdkdvbxcpcochcrdicibqeebddbcndsbdcpdgcpdncncsescgddclenbmcuducqcacdeldzel...' (full string in #64669).",
    "decode_result", True, "Sparky: keys 'dbjfhcek', 'dbifhcegapqm', 8th letter 'p' also give btcseed; ignores 82/91 dbbi chars; faed fails Bifid/Trifid IoC. Denis 65492/65515: Bifid properties restrict output letters, coincidence. Denis 64712 posted a CyberChef 'a-i ciphertext duplicator' (base9->base3->aei->Bifid encode key 'akblcmnopqdresftuvwxgyhzi') as a control. Already closed in cycle 37.")
add([65456, 65459, 65460, 65461, 65462, 65468, 65469, 65470], "Denis Golovkin / Sparky", "2026-06-16",
    "'Password golf': random short passwords pass the OpenSSL PKCS#7 padding check about 1/256 of the time. Examples that 'decrypt' with valid padding: Phase 3.2 '4LR*c', Cosmic Duality '}<b}=', SalPhaseIon 'mrJ|3'; 'THE FLOWER' is also 'correct'. Any blob 'decryption' claim judged only by padding is a false positive.",
    "data_artifact", True, "Used to rebut Pro Tlo 65456 ('7 passwords decrypted, 64-digit outcome'). Denis also points to a HF space 'openssl-for-restless-souls' (not visited).")
add([64723, 64725, 64727, 64733, 64736], "Denis Golovkin / Robby / Sigma", "2026-06-08",
    "Reported .bin outputs of Cosmic Duality (e.g. 1,327 bytes) are false positives: produced with 7 passwords incl. duplicate 'matrixsumlist' plus a guessed different openssl flag; output is garbage. Several GitHub issues pushing 'files' are reportedly the same person.",
    "other", True, "Community consensus: scam or LLM output; AES-CBC has no integrity check beyond padding.")
add([65496, 65497], "Hossein (+Denis)", "2026-06-17",
    "Compiled SalPhaseIon decode: (a) A1Z26 triple sums on dbbi remainder 'bihabebeihbe...eeeabe' (e.g. 'bei'=16=P, 'hbe'=15=O) -> 'POSNITOVERMMJIOLSJPJSRO' read as 'position it over mmjiolsjpjsro'; (b) openssl enc -aes-256-cbc -d -a -md md5 on the small blob with pass 'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist' -> hex 9fa9db91a9dee0e3...0ed1c5, split as K_C1/K_C2/E_C; (c) anstoo = ans2000 (cipher book) or OEIS A141920 (primes = 16 mod 23) linked to the 'Your life is the sum...' text.",
    "decode_result", True, "No direct rebuttal (Sanad: 'could be a good lead'). (b) is almost certainly a padding false positive (see password-golf lead); (a) triple grouping is not fully specified and the output is not English.")
add([64387, 64388, 64389], "Hossein", "2026-05-31",
    "Take the Phase 3 dialogue strings ('Right, this is causality', 'do you beleive me you need it?', 'part of the cipher', 'are you sure?', 'phase3.2 pass OK', 'You are here because 227 chars were correct', 'Good job, Neo!'), SHA256 each password and use it as a private key (WIF), compare with the prize address.",
    "method", True, "No reaction. Finite and self-verifying (address match), very low prior; likely already tried by others.")
add([63229, 63233, 63295, 63298, 63305, 63308], "Artem", "2026-05-17",
    "Hex->decimal of the SalPhaseIon URL hash 89727c59...6a32 = 62169139051977406799456590670741406588888301705500207831609968087667150121522 ('88888' in the middle); prize HASH160 a9553269572a317e39f0f518cb87c1a0ee1dbae4 in decimal = 966719395070911013213399990876229779543419632356 ('9999' in the middle).",
    "data_artifact", True, "Sparky: digit runs are expected in random numbers and could not have been engineered into a vanity H160 plus page hash.",
    "VERIFIED that both runs are present. No operational consequence.")
add([63463, 63472, 63473, 63474, 63476, 63477, 63358, 63359], "Artem (rebutted by Sparky)", "2026-05-21",
    "Prize pubkey 04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559 (Y; -Y = 638c2da0...0cc6d6). Hypothesis: yin/yang = +/-Y, 17ucy key reachable from 1GSMG point via curve traversal/negation.",
    "data_artifact", True, "Sparky: negated-point address and bit-inverted key (~k = 2^256-1-k) do not match 17ucy; pubkey only became known after the 2020 halving spend, so it cannot be puzzle mechanics. Denis/Sparky: 3GSMG addresses are fan-made halvings/doublings of the 1GSMG point.")
add([63957, 63966, 63942, 65804], "Jrk Bgrt (creator); Zil", "2026-05-28",
    "Creator, asked whether gsmg.io going offline affects solving SalPhaseIon/Cosmic Duality: 'Ah, ofcourse. The puzzle is still valid!' (#63957), and an emoji to 'No hint Thursday, every Friday!' (#63966). Zil (#65804) recalls the creator earlier said 'internet is no longer required' after seeing in nginx logs that people reached SalPhaseIon. Consequence: everything needed from SalPhaseIon on is offline and already public; no hidden server endpoint is needed.",
    "creator_reaction", False, "Cebotari 64114 complains there is no hint. alpha.gsmg.io went down 2026-05-22 (Sparky 63529); gsmg-archive.org (Flo Sku) mirrors the pages.")
add([63428, 63430, 63605, 64108, 65670], "Y (relaying creator); Sparky; X", "2026-05-21",
    "Relayed creator quotes: Jan 2023 'might appear unsolvable but it is not'; Aug 2023 may give an extra hint if not solved in a few years; 'It should take just a few hours to crack the private key when the final phase is reached'. Sparky's paraphrase: 'Just hit yin-yang then 2h max same day'. Consequence: the last step likely includes a bounded brute force (hours of compute), e.g. a partial key or reduced range, after the yin-yang output.",
    "hint_interpretation", False, "X 65670: 'we will need brute force but not yet according to phase 3.2 text'.")
add([63482, 63484, 63485, 63497, 64655, 64656, 64897, 65854, 65857, 65850, 65533, 65534], "X / Denis / Sigma / Zil / sol (relaying)", "2026-05-21",
    "Halving and two keys: creator (11 May 2020): 'If you find the answer now, the remaining 2.5 btc is well deserved... Or 5, who knows'; 'who knows what you'll find after opening the 2nd door. The price is in half'; 'We have our reasons halving the price money at every bitcoin halving event'. Better half = 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa (2.5 BTC moved 2020-05-11). Phase 3.3: 'the privatekeys belong to half and better half and they also need funds to live'. Readings: Phase 3.2 inner blob -> one key and SalPhaseIon -> the other; or the 3.2 blob plaintext is the SalPhaseIon password. sol relays (Dutch) creator lines: 'there really is a private key to find' and the welcome puzzle was solved in 2 hours vs an estimated week.",
    "hint_interpretation", False, "X 63488: 2nd door = SalPhaseIon + Cosmic Duality. Sparky 63483: 17ucy was empty when the puzzle launched, no proven key relation.")
add([64555, 64630, 64914, 65084, 65091, 65093], "gnomad / Whore Amazing / gnosis / X", "2026-06-03",
    "Creator has stated the prize is a (raw) private key; with the vanity prefix 1GSMG1 this means a vanity-generator key, not a BIP39-derived one. Consequence: BIP39 mnemonic readings (T K 63411, Artem 63398/65083) are unlikely.",
    "creator_reaction", False, "Relayed, not quoted with message link in this chunk.")
add([63913, 65878, 65863, 65921, 65922], "Mr Crazy / X / Sigma", "2026-05-26",
    "Creator hint chain (quoted): 'yellow blue primes matrix sumlist last words before archichoice yinyang we wont give away thepassword its in front of your eyes but youre not seeing it very last step is a true give away promised'. X's layout of SalPhaseIon: 'lastwordsbeforearchichoice z thispassword z sha256ourfirsthintisyourlastcommand U2FsdGVkX186tYU0...rdd9 z enter QvX0t8v3...GuN/jJ sha256anstoo'; 'archichoice' = the Architect's left/right door choice ('the door to your right leads to the Source and the salvation of Zion'), so 'last words before archichoice' = Neo's last words before choosing.",
    "hint_interpretation", False, "Sigma 65863: the only reliable SalPhaseIon hint is 'the password is right in front of your eyes'. Flo Sku 65873 suggests the FEFEFE square.")
add([63460, 63726, 65090, 63734, 63737], "Artem / X / pi-user", "2026-05-21",
    "Creator quotes 'Could also be 21 or 1812 bit' and 'Only -41,-17 matters' read as BIP39 indices (21 action, 1812 tiny, 41 acoustic, 17 agree); X: 'tiny hint -> TINY INT'; '3.1415...' user: 'logo 117,141'.",
    "hint_interpretation", False, "No operational consequence derived; conflicts with prize = raw private key.")
add([63676, 63677, 65924, 65927, 65929], "Artem / X / Agent Mike", "2026-05-24",
    "Creator New Year 2026 hint '. .. ... .... .....' ('Changed'). X: dots = 1..5, primes 2,3,5; 'sum each row, keep only prime sums, zero the rest' -> 107 101 89 109 103 109 97 = 'keYmgma' -> 'mgma' Caesar -8 = 'eyes' ('key eyes', matching 'in front of your eyes'); zero-stripped '17118919131997' is prime. Agent Mike: the dots were posted 1 minute apart, 5th at 4:20.",
    "hint_interpretation", False, "RB 65928 mocks it. Which rows are summed is unspecified (14x14 row sums are <=14). Cycle 37 found no hidden channel in the new-year hint.",
    "17118919131997 is prime (verified); derivation not reproducible.")
add([63681, 63684, 63685, 63687, 63688], "Artem / pi-user", "2026-05-24",
    "Creator message 'I'm going to rewatch episode 3.5 with  the better half.' contains a double space before 'the better half' (0x20 0x20 -> '2020' halving).",
    "hint_interpretation", False, "None; could be a typing artifact.")
add([63418, 63420, 63424, 63425, 65578], "Sparky / Y / gnomad", "2026-05-21",
    "Typo precedent: the 'givetit' Phase 3 typo survived the creator solving it 3 times. gnomad: the author said the remaining typos do not affect the puzzle logic. Consequence: do not assume a fatal typo in SalPhaseIon.",
    "creator_reaction", False, "pi-user 63426: the typo may have been intentional.")
add([64194, 64206, 64218, 64222, 64230], "Hii / Robby", "2026-05-29",
    "Creator once said someone mentioning yin and yang was 'scarily close' to the solution (old msgs #10082/#8315).",
    "creator_reaction", False, "Robby 64222: that remark was about the Cosmic Duality book, not a yin-yang solution.")
add([65105, 65106, 65108], "X (relaying creator)", "2026-06-09",
    "Creator, Aug 2023: 'Something was solved rather... remarkable.' X: a real piece of progress was posted Jan-Aug 2023 and went unnoticed; re-read that period.",
    "creator_reaction", False, "None.")
add([65882, 65886, 63360, 65990, 65994, 63707, 65531, 65544], "various", "2026-06-23",
    "On-chain/vanity artifacts: 1GSMG9VDLTU6jyuG7bkNMdmnHBLtbbM51M (pubkey 04d3b822...) inscribed 'leavethematrix -> hereismysecret -> yourlastcommand -> isolveditwithanabacus -> secondanswer'; 3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK (multisig) and 1GSMG1ABC95GES4k9UZCLtz6CYCUL8LUV2; sol posted 183hmJGRuTEi2YDCWy5iozY8rZtFwVgahM; Denis tx 21809edab11fe9c934a78f663d570f133339990b096c625171f1db3f099b8e25 ('March 2019: People! Help!').",
    "data_artifact", False, "Creator said on-chain messages are not his (Sparky 63360, 65990); ns 65886: a 1GSMG vanity takes 0.5 s; X 65994: not ruled out as from another builder. Treat as fan-made.")
add([63368, 63370, 63371, 63382, 63383], "Artem", "2026-05-19",
    "Parent address sent 0.01337 BTC (leet) to a look-alike address months before funding the prize; 1GSMG1CLxGXuFtnKbwh1QWfp4xA6reAet3 was the 'marker' address.",
    "data_artifact", False, "pi-user 63383: it is the GSMG donation address. No consequence.")
add([65629, 65714], "Vasilis Dragon", "2026-06-21",
    "'Canonical chain': cosmic decrypt sha256 4f7a1e4e; chain4 post-AES (PKCS7 stripped) 1151 bytes sha256 e4269ed5; its 35 ciphertext blocks (1120 B) sha256 43d3fe43; a chain4 of a80a399a means the broken GitHub #68 derivation. Claims one AES key decrypts those 35 blocks to the prize key; tested all held values, Cosmic Duality book data, on-chain messages and a 2700-term passphrase brute force with an EC oracle (prize/C32/17ucy, +/-1, x2, /2): nothing. Asks for the full rendered SalPhaseIon/Cosmic page text and the exact 2019 first hint.",
    "other", False, "No response. A 'cosmic decrypt' contradicts the consensus that the Cosmic blob is unsolved; probably the GitHub .bin false-positive family. Hashes are truncated and passwords not given.")
add([65123, 65141, 65206, 64920, 64921, 64922, 65183, 65234, 65241], "gnosis", "2026-06-09",
    "'Verifiable yin-yang program': REINS '4AA2A3A956A7A83', compose = 34414132603341393536413741383300 ('4AA2`3A956A7A83'), unified = 3924283367293f3224242521363a0000, sha256(compose hex)+'yourlastcommand' -> sha -> 9cd4d721fa64e56560af855b387d9442, glue6 = 0d0a00111310; also 'vig_dec(VIC|head80) = INCASEYOUMANAGETOCRACKTHISTH', 'vig_dec(post_win15, reins6|hex_az) = BLOCK'. Admits no blob decrypts.",
    "method", False, "Flo Sku 65183: none of these terms exist; Sparky 65234/65241: Texas-sharpshooter, steps not invertible so not a design; Nietzsch: LLM output. Inputs (S, s15, cadena3) undefined.")
add([65684, 65693, 65697, 65452, 65453, 65454, 65654], "pi-user / X / T K / Denis / E", "2026-06-21",
    "SalPhaseIon textarea is 2149 chars: 1074 whitespace + 1075 non-whitespace (X: 'yin-yang', maybe drop one char). Spaces: X says token separators; T K says z's are separators; Denis says spaces make the faed length 1141 with both outer spaces; E: 'anstoo' a(1) n(14) s(19) -> 1141.",
    "data_artifact", True, "No resolution; counts depend on the exact page source (archived HTML).")
add([65523, 63520], "RB", "2026-06-18",
    "570 = 2*3*5*19 = 15*38, and 38 = len('lastwordsbeforearchichoicethispassword') (X's method uses 38 rows x 15).",
    "data_artifact", True, "None.", "VERIFIED: 26+12 = 38.")
add([64897], "Agent Mike", "2026-06-08",
    "Phase 3.3 checkerboard digits for 'privatekeys' = 42 8 15 41 9 13 12 18 12 19 43; regrouped as hex bytes 42 81 54 19 13 12 18 12 19 43 only 0x42 'B', 0x54 'T', 0x43 'C' are printable -> 'the BTC belong to half and better half'. Notes B and C share the checkerboard's top row but T does not.",
    "data_artifact", True, "Self-described as probably coincidence.")
add([63628, 63629, 63630, 65585], "Y / Sparky / RB", "2026-05-23",
    "The Architect passage in the puzzle is an altered version of the film transcript (Sparky: the GSMG insertion after 'that was quicker' is not in the movie); RB: the Alice-in-Wonderland quotes used in Phase 3 and hints are fabricated internet quotes, not Carroll. Consequence: quoted clues ('last words before archichoice') should be matched against web transcripts/quote sites, and the diff against the canonical transcript is a concrete artifact.",
    "hint_interpretation", True, "gnomad 65593: illusion vs reality is the theme.")
add([65647, 65648, 63530, 63542, 63529], "Denis Golovkin / Flo Sku / Sparky", "2026-06-21",
    "Site archive listing: choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself.html (9398 B), puzzle.png (29931 B), 89727c...6a32.html (4588 B), theseedisplanted.html (1081 B), img/: 'black_banking - war.png', 'blue_dig_i.png', 'red_open_lock_n_ing.png', 'red_crypto_gic.png', 'blue_ca.png', 'red_t.png', 'follow_the_white_rabbit.png', 'blue_lock_lo.png', 'red_n_you.png'. The phase1verification endpoint 302-redirects based on the POSTed password. alpha.gsmg.io down since 2026-05-22; gsmg-archive.org mirrors the phases.",
    "data_artifact", False, "None; useful for checking page-text completeness (Vasilis 65629 says the full live SalPhaseIon page text is missing).")
add([66003, 66005, 66008, 66017, 66035, 66036, 66037], "sol / Denis / Alex", "2026-06-28",
    "QR code is standard and reproducible: encode 'https://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe' as Byte, UTF-8, ECC L (7%) with the optional ECI header present. FEFEFE is spiral index 163 (0-based) / 164 (1-based); 33/32 from the end.",
    "data_artifact", True, "sol 66037 saw extra undecodable hex in raw QR bytes (padding/ECC per Denis). Cycle 37 already closed the QR.",
    "FEFEFE spiral index 163 VERIFIED.")
add([66069, 66086, 66088, 66094, 66111, 66114, 66121, 66123, 66142, 66151], "Sparky vs Denis Golovkin", "2026-06-28",
    "Phase 3.2 decode pipeline (Denis): POST 'theflowerblossomsthroughwhatseemstobeaconcretesurface'; openssl pass = sha256('causalitySafenetLunaHSM111100x736B...b - - 0 1'); then pass = sha256('jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple'); tail -c+448 | head -c 1539 | iconv ISO-8859-1->CP1141 | beaufort --decrypt key 'thematrixhasyou'. Dispute: Sparky says the CP1141 step is irrelevant (26 byte values, hill-climbing recovers the mapping); Denis says Beaufort's modulo makes the byte->letter order matter.",
    "method", True, "Unresolved; concerns an already-solved phase (tooling detail only).")
add([65762, 65764, 65765, 64580, 63570], "pi-user / Sparky", "2026-06-21",
    "Blob KDF: key = sha256(sha256hex(pw) || salt) (EVP_BytesToKey, md sha256, 1 round); IV = first half of the next digest. Candidates can be rejected by decrypting only the last 2 blocks and checking padding; Sparky runs an AES-NI/SIMD scanner at ~100M keys/s over all 3 unsolved blobs.",
    "method", True, "Y 63574 notes AES itself cannot be broken; Sparky clarifies it is a password-candidate scanner.")
add([63411], "T K", "2026-05-21",
    "6 checksum-valid BIP39 mnemonics from 'bcde-pair decoding' (b90+t472 offsets), e.g. 'uphold shed scissors tonight oxygen like net festival invest frame unaware candy', 'now harvest install engine little hire again such edit bulk huge ball', 18-word 'bus hobby project ... call gallery'.",
    "decode_result", True, "Mr Crazy: 'nonsense'. A valid checksum happens by chance (1/16 for 12 words, 1/64 for 18 words); conflicts with prize = raw key.")
add([64643, 64644], "Robby / Denis", "2026-06-06",
    "Digit->letter on prize amounts: 5 = 'e', 2.5 = 'be', 1.25 = 'abe', 0.625 = '`fbe' (ties halving to dbbi's b/be tokens).",
    "hint_interpretation", False, "None; numerology.")
add([64473, 64474, 64477, 64480, 64481, 65335], "E", "2026-06-03",
    "Relayed creator line: 'all he had to do was look at the address and he will know how it was solved'. 1GSMG1 / 17ucy1 -> '7ucy' = '7 you see why'; mark every 7th spiral square (28 strings of 7 fill 196 exactly, dropping the 0000 pad), starting positions vary.",
    "hint_interpretation", False, "Denis 64476: visual art. No result.")
add([65799, 65800, 65801, 65860, 65861, 65862], "Zil / Sigma", "2026-06-22",
    "Order of stages: solvers were meant to reach SalPhaseIon first, before Phase 3.2.2; a group reached SalPhaseIon before the 'hush hush' hint, so it is not a later add-on.",
    "hint_interpretation", False, "Martin 65810 asks for basis; Zil later doubts it (65804).")
add([63169, 64392, 63417, 65836, 65842, 64373, 63243, 65456], "Andy / Lexane / Nietzsch / Artem / Pro Tlo", "2026-05-15",
    "Unverified progress claims: Andy says SalPhaseIon has a solution that yields concept-related clues and dbbi is not the main problem; Lexane claims to be at 'phase 3.2.2.10/11' (cipher 'is there', no new blob); Nietzsch claims a consistency check that kills popular dbbi readings (never explained); Artem promised releases every 3 days (did not follow through, per Alex 64641); Pro Tlo claims 7 passwords and a 64-digit blob output.",
    "other", False, "None substantiated; Pro Tlo rebutted by the padding false-positive argument.")

json.dump({"source": "data/user_supplied/telegram/new_chunk1.txt", "range": "#63169 (2026-05-15) .. #66152 (2026-06-29)",
           "n_leads": len(L), "leads": L}, open("/home/vin/bitcoin_puzzle/scratch/c39/chunk1/leads.json", "w"), indent=1, ensure_ascii=False)
print(len(L), sum(l["checkable"] for l in L))
