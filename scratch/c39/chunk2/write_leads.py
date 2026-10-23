import json, base64
L=[]
def add(ids,author,date,claim,kind,checkable,reaction,spot=None):
    d={"id":len(L)+1,"msg_ids":ids,"author":author,"date":date,"claim":claim,"kind":kind,"checkable":checkable,"reaction_rebuttal":reaction}
    if spot: d["our_spotcheck"]=spot
    L.append(d)
add([66538,66722,66745,66746,66747,66748],"Vasilis Dragon","2026-07-12/13",
 "Take A = dbbi minus M91 letter by letter (a=0..z=25, mod 26), where M91 = 'incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive' (sha256 2fbfbef7...). A = VOZIJBDTIQBRGVEOMZNBC|YOUWON|XCPKW... with YOUWON at index 21; he splits 21/49/21 into a 7x7 frame. 'Borrow rail' (1 where dbbi_i<M91_i): its only run of 7+ ones starts at 21. 'VIC rail' (M91 letters not in the top row FUBCDORA): its longest run (9) also starts at 21. faed self-keyed Bifid -> BTCSEED..., rail2 first row 'tsedomk' reversed = KMODEST; K at (2,5) in a dbbi[:13] Bifid square -> 'BE' => 'YOU WON - BE MODEST'. Hashes: sha256(dbbi)=71fe4625..., sha256(A)=f1785730..., sha256(YOUWONBEMODEST)=e8f32510...",
 "decode_result",True,
 "Rafael Gomes (#66749): the reproducible core reaches TSEDOMK; KMODEST->BE is interpretive. The author admits step 4 is 'a reach' read backwards from the expected answer, and that the {1,4,21}/21-row split is not reproducible and came out statistically null in his own tests.",
 "Steps 1-2 reproduce exactly: YOUWON at index 21, sha256(A)=f17857308a886531..., and the only borrow run of 7+ ones is at 21. However, the borrow rail is NOT independent of A. dbbi uses only the letters a-i, so with no borrow A_i is at most 'I'. Any A letter from J to Z therefore forces a borrow, and YOUWONX forces 1111111. The VIC rail also depends only on M91's letters. The only real signal is one 6-letter English word in a single difference string, and many texts and operations have been tried, so this is most likely a coincidence. BTCSEED was already rated a coincidence in cycle 37.")
add([66244,66245,66247,66264],"حسین ▪️ (claim); Sebastian (rebuttal)","2026-07-02",
 "In the Part4 Bifid output (btcseed...), drop the first 6 chars and take every other char (rest[::2]). That channel uses only {b,c,d,e}. Map d=00,c=01,b=10,e=11, then take 132 symbols from offset 27 = 264 bits = a checksum-valid 24-word BIP39 phrase 'dust trophy mule tragic corn ... copy satoshi fee allow' (entropy 445d1e45...ed520).",
 "decode_result",False,
 "Sebastian checked all 24 mappings x 151 offsets (3624 windows). 13 windows give checksum-valid phrases, against about 14 expected by chance. Offset and length are free parameters. Nothing matches under BIP44/49/84 or as a raw key. The prize address is a vanity address and cannot come from BIP39. Sparky: 'LLM crap'. The {b,c,d,e} channel itself is real and is a known structural property (the 2-bit selector stream of the value/selector pairs).")
add([68284],"MrNobody","2026-08-08",
 "Read dbbi as a straddling checkerboard with row prefixes {b,g}. It parses into exactly 64 tokens using exactly 16 distinct symbols, matching a 64-character hex digest. He claims faed has no valid hex reading at any prefix count. He brute-forced all 16! (2.09e13) symbol-to-hex mappings in two passes (41.8T trials, 13 GPU-hours, the second pass with no assumption about the plaintext): zero hits. He did not say which blob/KDF was the test target. He also notes that a random sha256 hex digest pushed through a 9-column checkerboard passes all ten of the usual 'noise' tests, so 'dbbi/faed are noise' only rules out readable language.",
 "method",True,
 "No rebuttal in this chunk.",
 "The parse reproduces: 64 tokens, 16 distinct symbols, ending cleanly. {a,b,g} also gives 64/16, so {b,g} is not strictly unique. In a shuffled-dbbi control (same letter counts, any 1-3 prefix set) only 0.8% of shuffles give 64/16. This is the strongest new structural lead in this chunk. His negative brute force cannot be audited because the target and success test were not stated.")
add([68249,68259,68376,68394,68434,68464,68262],"MrNobody; Naddiseo; sniper; B58","2026-08-08..11",
 "Cosmic Duality: the '7-token' key = XOR of sha256 over [matrixsumlist, enter, lastwordsbeforearchichoice, thispassword, matrixsumlist, yourlastcommand, secondanswer] = a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735 (jackdevs66/GSMG5_CDuality). The widely cited 1327-byte output with sha256 4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081 reproduces only when the 32 raw digest bytes are the password and the MD5 KDF is used. The hex string as password gives noise. Every solved phase uses -md sha256 (the phase 3.2 control fails under md5). Random 32-byte keys give valid PKCS7 on this blob 63/20000 times (about 1/317). The output has entropy 7.87 and printable ratio 0.389.",
 "data_artifact",True,
 "Naddiseo (#68376, maintainer): he already refuted the jackdevs66 path as guesswork (issue #55), but LLMs treat it as gospel. sniper: the Chain4/XOR-triangle stack needs an operand (cd3fea3d...) that cannot be derived from public data, and its 79-byte anchor is a 1/256 padding coincidence (issue #92). B58: 'any proposed cosmic duality AES decrypt is wrong'.",
 "The 7-token XOR reproduces (a795de11...). Treat the whole 1327-byte / 103x103 / XOR-triangle stack as an unproven padding false positive.")
add([67787,66190],"MrNobody (also Sparky #66190)","2026-08-02",
 "Hypothesis: as in the solved phases (Phase 3 = 7 parts concatenated, '1part..7part'; Phase 3.2 = 3 riddle answers concatenated), the SalPhaseIon password is all of the page's riddle answers joined in page order, then sha256: yellowblueprimes | matrixsumlist | lastwordsbeforearchichoice | yinyang. Getting 3 of 4 right would still hash to noise. He tested the rule on the '2b blob' (likely the Phase 3.2 inner blob) using permutations of 3.2 sub-answers {thematrixhasyou, beaufort, 1141, VIC alphabet, VIC plaintext, FEN}, about 240k combinations: nothing. A 2024-10-26 chat suggestion ('concat each answer as you go... key to cosmic?') was never followed up.",
 "hint_interpretation",True,
 "No rebuttal. He asks for the canonical 3.2 sub-answers in other forms. Loupi (#66829) posted the inner blob U2FsdGVkX1+0Wl49gnWT... (salt b45a5e3d827593ca = our phase32-inner.b64) and asked if it is needed; nobody answered.",
 "This fits the cycle-37 'chained answers' model. A decrypt with valid padding and readable output verifies itself, but the candidate component set is open-ended, so it should be tested only with derivation-backed components.")
add([67741,67787,68332,68337],"MrNobody; Jerry","2026-08-01..09",
 "Normalization rules: README '/(...)' markers (lines 158/168/201): '/(aa, connected enf)' = lowercase, joined, whitespace stripped; '/(aBa, connected not enf)' = keep case and whitespace. The Phase 3 password is case- and space-sensitive: 'causalitySafenetLunaHSM11110<hex>B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1' -> sha256 1a57c572.... Phase 3.2 is lowercase and stripped (jacquefresco+giveitjustonesecond+heisenbergsuncertaintyprinciple). Jerry: the SalPhaseIon URL hash drops the '.' from GSMG.IO but the FEN hash keeps its special characters. Why?",
 "method",True,
 "RB (#67742): case/spacing sensitivity is a known fact.",
 "sha256('GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe') = 89727c598b9cd1cf... matches the SalPhaseIon page name.")
add([66587,66588,66589],"Jrk Bgrt (creator)","2026-07-13",
 "Asked 'salphaseion is 100% solvable?', the creator answered 'Yes'. He added that even if somehow wrong, it is 'all still solvable with a few stable qubits'. He 'verified many times back then after some sad rushed mistakes' (the givetit fix).",
 "creator_reaction",False,"The community reads this as a reaffirmation. He did not clarify whether any later bug exists (Denis #67302-67316 petition to re-verify).")
add([66573,66574],"Jrk Bgrt (creator)","2026-07-13",
 "'My close friends have the best chance of solving it (a few tried). But they don't have the skills some of you do.' followed by 'NOTE: that is a hint.'",
 "creator_reaction",False,
 "Readings: d1d (#68313) says skills are not the main factor, knowing his thinking/values is. Varholy Viktor says the second sentence is the hint. Sparky says befriend Jrk. No operational consequence was derived.")
add([66568,66903,66884,66893],"Jrk Bgrt (creator)","2026-07-13/16",
 "'I have a hidden laptop which I haven't touched in years. On that thing... is the actual answer.' Later: 'it's hidden in a room with a hidden door.' Also 'Hmm. Meta hunting. Like it.'",
 "creator_reaction",False,"Community link to the 'another door' hint (Flo Sku #67013). Mostly jokes. No operational content.")
add([66592,66593,66595,66600,66604],"Jrk Bgrt (creator)","2026-07-13",
 "'I held quite a secret in my head which I seriously wanted to share with the planet'. 'The \"5\" btc was never the actual prize. That was only a tiny fraction.' 'the btc is still available'. 'Some already found it. And understood not to risk it... 🤐' 'Iykyk'.",
 "creator_reaction",False,"Prompted speculation (Satoshi coins, someone ahead, Cereal Killer #67384-67388). Martín: sounds like 'kiber' claims from the other side. Nothing testable.")
add([66562,66563,66564],"Jerry; creator reply","2026-07-13",
 "len(dbbi)+len(faed) = 661. Taking the characters at prime positions leaves 121 characters (an 11x11 square). There are 30 primes up to 121, and 121-30 = 91 (= len(dbbi)). Creator reply: 'I don't know right now.'",
 "data_artifact",False,"Creator was non-committal.","661 is prime and pi(661)=121. The arithmetic holds, but it gives no self-verifying outcome.")
add([66961,66962,66913,66931,66898,66584,66586],"Jrk Bgrt (creator)","2026-07-13/16",
 "Short creator remarks: 'Lately, I'm working with many NOTES.' 'ELI4.5 is meta.' 'You have to be in your prime for that.' 'Had my eyes closed, but still saw double.' 'Give yourself yourself and yourself will be given yourself.' 'I feel a bit off knowing the url (and thus the original puzzle) is \"gone\"' (site offline). Denis asked 'Anything listed here?' (re #52505) and got 'Nope.'",
 "creator_reaction",False,"Spike: 'TRY 4.5 ON EVERYTHING'. Loupi tied NOTES to the music-note idea (lead 13). None was confirmed as a hint.")
add([67391,67394,67395,66612,66872],"Loupi; Denis Golovkin; Agent Mike","2026-07-26",
 "SalPhaseIon a-i letter blocks may be music notes (dCode text analysis flags musical notation). IBM EBCDIC 1141 is the German codepage, and German note names are C D E F G A H B (H = B-natural). Denis ties this to his list of Jrk's 'I ...' statements (#66612, 'I-denial'). That fits because 'i' is the only dbbi letter that is not a German note.",
 "hint_interpretation",False,"No test or rebuttal was posted.")
add([66727,66728,67113,67114,67118,67141,67143,67145,67733,68038],"Vasilis Dragon; Deleted Account; Spike; gnomad; Варя Новая; DerST","2026-07-13..08-05",
 "Creator 2021 hint 'another door might be found on {1},{4},{21}'. (a) Vasilis: rows 1/4/21 of a 21-row transcription = dbbi / faed[94:201] / anstoo. (b) DBBI[1],[4],[21] (1-based) = d,i,e = 'DIE'. Zero-based gives 'bbi', and faed gives 'FDA'. (c) 1 Samuel 4:21 (Ichabod).",
 "hint_interpretation",False,
 "The hint was posted on 2021-04-01, so 1.4.21 = April Fools (Spike, gnomad). Vasilis says (a) has no fixed row boundaries and was statistically null. (b) was tested as deletion/zeroing/selection with no result and is called AI slop. DerST asked the creator to clarify; no answer.",
 "DBBI 1-based [1,4,21] = 'die' confirmed.")
add([66338,66345,66347,66366,66360,66362,66365,66369,66381,67085,67087],"Lexane; Sparky; Diego Schmidt","2026-07-03..17",
 "Lexane claims that solving from the start through phase 3.2 gave 'bullshit' after about 2 months. The word itself does not appear; it is 'a different kind of bullshit'. He calls it 'the next step'. Sparky: BULLSHIT a1z26 = 103 = row-major index of the FEFEFE cell; BULL = 47 ~ (4,7); odd positions sum to 42. Diego: 'matrixsumlistlastwordsbeforearchichoiceshabefourfirsthintisyourlastcommandentershabefanstoo' = 103. In the film, the Architect scene has Neo say 'Bullshit' -> 'Denial is the most predictable of all human responses.'",
 "hint_interpretation",False,"Lexane never shows his derivation and also jokes about it. Sparky's posts are partly parody.",
 "BULLSHIT = 103 confirmed. Diego's 103 does not reproduce: the string is 91 letters long (= len(dbbi) = len(M91)) and its a1z26 sum is 1089.")
add([66307,66308,66309,66310,66311,67789,66215],"Flo Sku; Agent Mike","2026-07-02 / 08-02",
 "Candidates for 'lastwordsbeforearchichoice': (a) the Architect's line before 'There are two doors': 'Which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning, and end.' Right door = Source / 'salvation of Zion' ~ SalPhaseIon; left door = matrix/image. (b) 'We won't' -> yin-yang inversion 'we will' -> Queen -> list = rockyou.txt.",
 "hint_interpretation",False,"ΞZ: the phrase is ambiguous. No test was reported. (b) implies a wordlist search, which our rules forbid.")
add([66242,66395,66942],"Diego Schmidt","2026-07-01/03",
 "Yellow/blue primes: 'if blue < yellow then 1 else 0' gives first 8 bits 01111111 = 0x7F (DEL) and last 8 bits 11111110 = 0xFE. The opposite comparison gives 0x80 and 0x01. 'OVER TWENTY-THREE CIPHERS / SIXTEEN ENCRYPTIONS / SEVEN INTERTWINED PASSWORDS' <-> 'gsmg.io/theseedisplanted' = 24 / 'theseedisplanted' = 16 / 'gsmg.io' = 7 chars. He reposts creator quotes from 2024-11-29: 'I think I'll be going for ASCII 127 myself.' and 'we had a few FE guys working on it.' He replied to Jrk's BIP360 post with 'v = c[0] & 0xfe'.",
 "hint_interpretation",False,"No rebuttal. The comparison rule is underspecified (which values are compared?). The links between 0x7F/0xFE, the creator's 'ASCII 127', and the FEFEFE cell are suggestive but not derived.")
add([67289],"👑","2026-07-26",
 "'VIC result = 91 chars = 23 words; take the first 16 + the last 7' (ties to '23 ciphers / 16 encryptions / 7 passwords').",
 "hint_interpretation",False,"Posted as a taunt. No follow-up.",
 "Confirmed: M91 has exactly 23 words. The first 16 end at '...half and better half' (65 letters). The last 7, 'andtheyalsoneedfundstolive', are exactly 26 letters. The fit is neat, but there is no self-verifying test.")
add([67215,67318,68456],"Denis Golovkin","2026-07-25..08-11",
 "Read 'half and better half' as: dbbi's prime-position characters give 23 bits and theseedisplanted's LSBs give 24 bits ('half +/- 3'). He says some bits in dbbi's yellow/blue primes are probably wrong (found by someone else), and calls dbbi 'storage for y/b primes + 60 more filament characters'.",
 "hint_interpretation",False,"sol: 'probably wrong'. The letter-to-bit mapping was not stated.")
add([67697,67714,67720],"gnomad; Cereal Killer","2026-08-01",
 "(Known, phase 0) Yellow/blue squares are the LSBs of each letter of 'gsmg.io/theseedisplanted' (Naddiseo phase0.ipynb). Colours in order: b b b b y b b b y y b b b b y b b y y b y y b y. 'Prime basics': 9 yellow -> sum of primes up to 9 = 17; 15 blue -> sum of primes up to 15 = 41 -> Decentraland (-41,-17).",
 "data_artifact",True,"This is the established phase-0 solution.")
add([67770,67743,67762,67767],"3.1415926535897932384626; RB","2026-08-02",
 "Decentraland history: LAND contract 0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d. Parcel (-41,-17) token ...1680 and (-41,-16) token ...1679 were merged into estate #955 on 2018-11-08. Transfer from the grant to gsmg on 2019-05-28, metadata update on 2019-05-29. RB: the puzzle started 04/2019, the plot was bought end of 05/2019, and Decentraland opened 02/2020. It was the only pointer to 'hash the text' -> SalPhaseIon. 3.1415: the piece was found on Discord 3 days after deployment, about a year before Jrk's hint.",
 "data_artifact",False,"Cereal Killer argued the coordinates were planned before launch. Not puzzle-internal data.")
add([67217,67220,67226,67230,67988],"Andy | DBBI & FAED; Denis Golovkin; 👑; Agent Mike","2026-07-25",
 "3GSMG tx a82052a216cad8f57dee2a039c3b5cef9b5fcb2bc1c3bffa94d713cee0b30e2b has OP_RETURN 'GSMG.io neighbors, half and double'. Its 4 outputs are P-G (1G1kRAFR68y6CUq1SAJMzHmjd6sEEgtVUT), P+G (1PhXF3xVQ8Sg9FomBcmRwRbvvGfm3Y2os1), P/2 (16eEXbSuKN8tvcos1iKjdju6dAaWWRBMEs) and 2P (1KHMK2C8uBptRz67FbrXy43yHzhZG16Hbm), where P = the 1GSMG1 pubkey 04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559. Andy concludes 3GSMG is a creator hint channel.",
 "data_artifact",True,
 "Denis: correct 'up to the conclusion part'. 👑: anyone can compute these from the public pubkey. Agent Mike: the pubkey has been public since the halving spend at block 630,001, and the tx came about 61,562 blocks later. Cycle 37 already established (Naddiseo issue #114) that the 3GSMG trail is not the creator's.")
add([66613,66617,66618,66625,66627,66630,66635,67357],"Варя Новая; John Smith; 3.1415926535897932384626","2026-07-13/26",
 "1GSMG and 3GSMG transactions in the same block with the same timestamp, adjacent in block order (txids a798905f53fdcadcbd2e2a1e61d23ba69a07e26130a78c76da4bf4d7a170f383, 2aa9a4a90be819d5122d70c993280785a0508f163521e7b38cebb4db0b071b13, 9bb23ee4683f87516e9d40d09dcb23b1995a74860cc676f9ed1e035778739206, c073634c862353b7a90303d52806defba55cac63a86762213fcb949b74a5573b), which they say proves a common owner even though the creator denies it.",
 "other",False,"Denis: synchronous is not intentional; halving timing is predictable. 3.1415: order follows fees/CPFP (child after parent); maybe timelocked 2 blocks before the halving. Superseded by the cycle-37 finding.")
add([67106,67292,67432,67450,67889],"Andy | DBBI & FAED • Res","2026-07-19..08-04",
 "He posts 5 sha256 values as 'stages in SalPhaseIon': 8dce5e157c4b14f13b2872328bd3f2b859ad19724d9cd1e0646ed08edac1bbd5, 6444eab38bb74caca27434fa27e615a868d5b7491f47a5d1d5e26b89a7b13bbd, bb1251a2a332eef08791175c9146a62a26618d5440328862dfe0eaa0581872c7, f8723eeeb65cf0846511a7c44637d3786d696b45820021513378d9587a399c25, 7f5fb9052544588f666d4d7b0f12c3e85128686534c0893b3e245b6bb324d22a. He claims a 'successful, reversible manual decoding of dbbi/faed' and is now on the 'last layer'.",
 "data_artifact",False,"Widely called a scam: he reportedly offered the solution for 1 ETH (👑, Spike, n04oh). No preimages or method were shown.",
 "These could be useful as commitments: hash any candidate intermediate strings against them.")
add([68461,68466,68469,68470,68480],"sniper; Denis Golovkin","2026-08-11",
 "faed negatives: all 9! letter->digit permutations in base 9 and in base 10, both directions, then hex->ascii: no text (best printable 0.52). Iterated base b1 -> reverse -> base b2, up to 5 rounds, bases 2-36: best printable 0.77 (Denis: up to base 91, 3 rounds, nothing). Every faed-derived value (triangle outputs, diagonals, the 474/400 blue-yellow prime sums, FEFEFE) tried as a key, md5 and sha256 KDF, against cosmic, the 79-byte SalPhaseIon blob, blob_readme and phase322: zero clean decrypts.",
 "method",True,"B58: IC does not apply here. sniper retracted his IC argument and kept only 'simple positional base-N is ruled out'.",
 "Consistent with cycle 37 (no lowercase text under any digit map).")
add([68452,68465,68472,68474],"К","2026-08-11",
 "Method warning: the dbbi/faed/matrix stage is so ambiguous that any symmetry (XOR triangle, FEFEFE, yellow/blue primes, '-41 -17 primes', 'hide face') can look like the 'yin-yang'. The only valid test is decrypting a blob. A 'ministep' being simple makes the interpretation space larger, not smaller.",
 "other",False,"sniper agreed. This is a good operating rule for us.")
add([68418,68439,67183,67582,67586,67598,67935,67981,68021,68031,67398,67474,67593],"sniper; d1d; Юрій Н.; Lexane; Alex; 👑; Agent Mike; Cereal Killer; Trin","2026-07-24..08-11",
 "Yin-yang claims and readings: sniper's blue/yellow duality from a dbbi/faed decode has two point-symmetric 'eyes' on the first and last slots, which he reads as 'our first hint is your last command'. d1d says he found 4 yin-yang shapes years ago (images, treating blue/yellow as self-chosen superpositions). Юрій Н. found the 'another door' while looking for the yin-yang. Lexane claims he reached it. 👑: the yin-yang is the duplicate method pairs in Salph (matrixsumlist & enter; lastwordsbeforearchichoice & thispassword). Agent Mike: 'balance' -> spend within 12 blocks. Creator quote (older): 'once you hit a yin-yang ... same day / max 2 hours'.",
 "hint_interpretation",False,"Trin is skeptical because Jrk said a solve follows the same day. n04oh: nobody is close until they show the yin-yang. No proof from anyone.")
add([67981,67992,67993],"Alex","2026-08-04",
 "Yin-yang = the diagonals. One diagonal splits the 14x14 matrix into two 91-cell halves (196-14 = 182 = 2x91). 91 is also the length of dbbi and of the 'incaseyoumanage...' (M91) string, which suggests a half / better half triangular layout of dbbi and M91 on the grid.",
 "hint_interpretation",False,"No follow-up (he also said he was drunk).",
 "The arithmetic holds. This is a cheap deterministic layout (fill a triangle row-major) but has no self-verifying outcome.")
add([66705,66708,66710,66711,66712,66733,66736],"Варя Новая","2026-07-13",
 "The 14x14 yellow-blue matrix is four 7x7 matrices ('GS/MG'), and the diagonally opposite corner blocks look alike. Some operation should make the top-left and top-right blocks identical. Then reading the rows as 7-bit bytes gives seven 4-letter words. Two layers: yellow/blue is layer 2, and layer 1 is hidden beneath it.",
 "hint_interpretation",False,"Vasilis: a stretch. The operation was not specified.")
add([66414,66415],"Robby; 3.1415926535897932384626","2026-07-04",
 "dbbi[0:16] = 'dbbibfbhccbegbih', apparently mapped b,e->0 and the other letters ->1, gives 1001010111001011 (0x95CB). Paired with 1001011000110100 = 0x9634 = '阴' (Yin, U+9634). 3.1415: the difference is 2^10-1 (0x03FF).",
 "decode_result",False,"No rebuttal. The mapping is chosen after the fact and only flips the last 10 bits, so there is no evidential value.")
add([66216],"Deleted Account","2026-06-29",
 "'BLUENET' as hex 061119242f3a5863767e81a3aab9c1 is missing only the hex digit d. dbbi has 'd' at 1-based positions 1, 48, 55, 74 (sum 178). Row-major cell 178 of the 14x14 grid (row 13, col 10) is the last yellow. Yellow positions: 14, 66, 77, 81, 96, 111, 133, 148, 178.",
 "hint_interpretation",False,"sol: 'good point'. No test.","The 'd' positions [1,48,55,74] are confirmed. The yellow-position list is a reusable data point.")
add([68265,68267,68270,68272,68280,68278,67749,67752],"MrNobody; Agent Mike; Spike","2026-08-02/08",
 "Rabbit grid facts: 85 white + 1 FEFEFE + 86 black + 15 blue + 9 yellow = 196 cells. Cell 104 is white (75.7% white pixels, README matrix = 0), and scripts that sample cell centres misread it as black. Phase 3 AES text has 86 lines (85 x 64 chars + 1 x 44 chars). Spike: compared with the Terraria bunny sprite, the tail pixels were rotated so the grid cell is mostly black, which makes the phase-0 reading work.",
 "data_artifact",True,"MrNobody confirmed Agent Mike's correction.")
add([67685,67687],"3.1415926535897932384626","2026-08-01",
 "A Tupper-style encoding of the rabbit matrix (x-flipped, plotted on 14x14) = 568167476976871720527873214809752593479433509283049173948702.",
 "data_artifact",False,"No discussion. It re-encodes the grid as a number.")
add([66208,66214,66223,66225,66407,66408,66411,66413,66175,66167,66190],"3.1415926535897932384626; Sparky; Denis Golovkin","2026-06-29..07-04",
 "(Solved stage) Phase 3.2 Beaufort section: the 26 byte values map to a-z in order, so any order-preserving remapping works. '%,/:>?[_`ÀÁÂÃÅÇÈÉÊËÌÍÎÏÑöø' <-> a-z, and 'thematrixhasyou' <-> 'Ì_>Ã%ÌÊ`Ñ_%ËöÇÍ'. Affine view: encryption key (11,14) <-> decryption key (19,20) '#2019'; 312 = 12x26 key pairs. Sparky: several of the 26 values are control characters in IBM 1141 but printable in ASCII codepages, so the 1141 link is doubtful. The Beaufort key comes from 'Wake up... the matrix has you'.",
 "method",True,"Solved stage, no new consequence. Loupi later used the German-1141 link for the music-note idea.")
add([66425,66427],"3.1415926535897932384626","2026-07-05",
 "Dimension coincidences: the VIC '10x10 table, 28 populated positions'. Text length 1539 (+17) vs image height 1556. Straddle shift 10, 40 (1040+8) vs image width 1048. 17+8 = 25.",
 "hint_interpretation",False,"No discussion.")
add([67169],"Denis Golovkin","2026-07-22",
 "Original site archive listing (sizes in bytes): choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself.html 9398; puzzle.png 29931; 89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32.html 4588; theseedisplanted.html 1081; img/: 'black_banking - war.png' 996, blue_dig_i.png 1030, red_open_lock_n_ing.png 963, red_crypto_gic.png 1642, blue_ca.png 627, red_t.png 506, follow_the_white_rabbit.png 1958 (Jan 24 2025), blue_lock_lo.png 783, red_n_you.png 863. Nikita points to gsmg-archive.org (not visited).",
 "data_artifact",True,"None. Useful for checking the integrity of our local copies.")
add([67548,67552,67563,67565,67566],"Cereal Killer; gnomad; 3.1415926535897932384626","2026-07-30",
 "Request for the original pre-'givetit'-fix Phase 3 AES blob. gnomad: Wayback only goes back to Nov 2020, but the error was reported May 2019; the givetit blob is inside the decoded AES output. 3.1415 posted salt e2991cdcd2c957f9 and an EVP_BytesToKey(sha256, key 32 / IV 16) derivation with password b'0c5ebe39fb72e947ea71bc991fb148f6cb14ad8210580a43e757a0cb65d636c8'.",
 "data_artifact",False,"Which blob this salt belongs to was not stated.",
 "The salt e2991cdcd2c957f9 does not match our phase32-inner (b45a5e3d...), salphaseion-small (3ab58534...) or cosmic (2d3f6fe0...) blobs. Phase 3 and phase 3.2 salts were not checked. Worth a single deterministic decrypt if the blob can be identified.")
add([67774,67097,67582,67802,67705,67706,67571,67574,68029,68030,67095],"3.1415926535897932384626; gnomad; Юрій Н.; Cereal Killer; sol; T K","2026-07-18..08-05",
 "'Another door' readings. 3.1415's inventory of exits: Phase 2 AES content (offline), Phase 3.1/3.2 content (offline), QR redirect (out), Decentraland (out). So the door is most likely a remaining offline AES decryption or an unsolved decryption that redirects out. Others: a door is not always a URL (Юрій claims he found it). Only two doors exist, theseedisplanted and hash-the-text -> SalPhaseIon (Cereal Killer). The hint was confused with Salph, or Salph was added later (sol).",
 "hint_interpretation",False,"Several people asked the creator whether the door is still valid; no answer in this chunk. gnomad says Jrk has said several times that it is.")
add([67506,67501,67335,67338,67336],"Loupi; 👑; Whore Amazing; Denis Golovkin","2026-07-26/28",
 "'shabef' = sha256 and 'anstoo' = 'answer too'. So sha256 of the final SalPhaseIon answer decrypts Cosmic Duality, matching the earlier pattern of hashing an answer. Phase 3.2 is self-contained, and Cosmic continues Salph because it is on the same page.",
 "hint_interpretation",False,"Denis: Cosmic could be fully independent. This is the consensus reading, with no new test.")
add([66698,66598,67788,68427,67486,68199,67831,68083],"E; Варя Новая; Cereal Killer; Cryptono; 𝐆𝐱𝟑; Agent Mike","2026-07-13..08-07",
 "Numerology bundle: dbbi as a1z26 digits /5 = 90-digit 8458525666514596250519651551505045517705772425296513268452667452511550650878525335945110 25. Word lengths of gsmg.io/theseedisplanted = 423427 (prime). Digits of the prize address = 11927 (emirp; 72911). 3 Jan 2009 -> 32009 (prime). shabefanstoo: a+n+s = 34 -> C,D = Cosmic Duality. 2:55 -> 175 = 25x7 rabbit blocks. 196-140 = 56 = 7x8. Yellow 9 = 3x3 and blue 15 = 3x5.",
 "hint_interpretation",False,"None produce a test.","Confirmed: dbbi/5 divides exactly, and 423427, 11927, 72911 are prime. None is meaningful.")
add([67524,67525,68162,68176,68437,68457,67292,67864,67919],"Agent Mike; TekniskTrading; B58; Andy; others","2026-07-29..08-11",
 "Unverified progress claims: 'XORed 2 binary strings, result starts with doR ... now it shows gsmg.in'. 'Faed I figured out' (then 'didn't work'). B58 'past public knowledge'. Andy 'manual reversible dbbi/faed decode'.",
 "other",False,"None came with inputs or method. n04oh: prove it.")
add([66651,68014,68016,68018],"Nikita; Denis Golovkin","2026-07-13 / 08-05",
 "Open questions: does the yin-yang step need input that cannot be computed from the published puzzle? Is the yin-yang before, after, or the same as Cosmic Duality?",
 "other",False,"No answer. Denis asked what difference it would make to the work.")
out='/home/vin/bitcoin_puzzle/scratch/c39/chunk2/leads.json'
meta={"source":"data/user_supplied/telegram/new_chunk2.txt","span":"2026-06-29 .. 2026-08-11 (#66153..#68480)","n_leads":len(L),
 "notes":"Personal details about the creator and others (location, events, substances, family) were deliberately left out. Links in the chat were not visited. Spot-checks were done with our own scripts: spotcheck.py and bg_unique.py in this directory.","leads":L}
json.dump(meta,open(out,'w'),ensure_ascii=False,indent=1)
print(len(L),'leads written')
# confirm Loupi blob == phase32-inner salt
b=base64.b64decode('U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46zgKlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4')
inner=base64.b64decode(''.join(open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-inner.b64').read().split()))
print('Loupi blob == phase32-inner:', b==inner, b[8:16].hex(), len(b))
