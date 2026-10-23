#!/usr/bin/env python3
"""Comprehensive, high-precision sweep of concrete cryptographic and contextual leads.
Evaluates SMALL_B64, INNER_B64, and COSMIC_B64 strictly offline against infallible oracle.
"""
import sys, os, hashlib, re, json, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')

from systematic_solver import run_sweep, forms_of, check_password

# ==============================================================================
# LEAD 1: South Park / Cartman Chatroulette Quote & Friends Context
# Jrk (#60306): "Maybe, Cartman's quote about chatroulette fits too."
# D1rty Byrd (#60311): "if you wanna find new friends you gotta weave through all the dicks first "
# Jrk (#60312): "Bingo"
# Jrk (2026-07-12): "My close friends have the best chance of solving it... NOTE: that is a hint."
# ==============================================================================
cartman_cands = [
    # Canonical South Park S14E04 quote
    "That's the way the world works! If you wanna find some quality friends, you gotta wade through all the dicks first!",
    "That's the way the world works. If you wanna find some quality friends, you gotta wade through all the dicks first.",
    "that's the way the world works! if you wanna find some quality friends, you gotta wade through all the dicks first!",
    "that's the way the world works. if you wanna find some quality friends, you gotta wade through all the dicks first.",
    "thats the way the world works if you wanna find some quality friends you gotta wade through all the dicks first",
    "If you wanna find some quality friends, you gotta wade through all the dicks first!",
    "If you wanna find some quality friends, you gotta wade through all the dicks first.",
    "If you wanna find some quality friends, you gotta wade through all the dicks first",
    "if you wanna find some quality friends, you gotta wade through all the dicks first!",
    "if you wanna find some quality friends, you gotta wade through all the dicks first",
    "if you wanna find some quality friends you gotta wade through all the dicks first",
    "ifyouwannafindsomequalityfriendsyougottawadethroughallthedicksfirst",
    
    # Variations with "want to", "have to", etc.
    "If you want to find some quality friends, you have to wade through all the dicks first.",
    "If you want to find some quality friends, you have to wade through all the dicks first",
    "if you want to find some quality friends, you have to wade through all the dicks first",
    "if you want to find some quality friends you have to wade through all the dicks first",
    "If you want to find quality friends, you have to wade through all the dicks first.",
    "If you want to find quality friends, you have to wade through all the dicks first",
    "if you want to find quality friends, you have to wade through all the dicks first",
    "if you want to find quality friends you have to wade through all the dicks first",
    "If you wanna find quality friends, you gotta wade through all the dicks first",
    "if you wanna find quality friends you gotta wade through all the dicks first",
    
    # D1rty Byrd verbatim wording ("weave" instead of "wade", "new" instead of "quality")
    "if you wanna find new friends you gotta weave through all the dicks first",
    "if you wanna find new friends you gotta weave through all the dicks first ",
    "If you wanna find new friends you gotta weave through all the dicks first",
    "if you want to find new friends you have to weave through all the dicks first",
    "if you wanna find new friends you gotta wade through all the dicks first",
    "if you want to find new friends you have to wade through all the dicks first",
    
    # Key core clauses
    "you gotta wade through all the dicks first",
    "you have to wade through all the dicks first",
    "wade through all the dicks first",
    "wade through all the dicks",
    "wade through the dicks",
    "you gotta weave through all the dicks first",
    "weave through all the dicks first",
    "weave through all the dicks",
    "wadethroughallthedicksfirst",
    "wadethroughallthedicks",
    "weavethroughallthedicksfirst",
    
    # Episode Title & Themes
    "You Have 0 Friends", "You Have 0 Friends.", "You Have 0 Friends!",
    "you have 0 friends", "you have 0 friends.", "you have 0 friends!",
    "youhave0friends", "You have zero friends", "You have zero friends.", "You have zero friends!",
    "you have zero friends", "you have zero friends.", "you have zero friends!",
    "youhavezerofriends",
    "0 friends", "zero friends", "quality friends", "qualityfriends",
    "close friends", "closefriends", "my close friends", "myclosefriends",
    "friends and family", "friendsandfamily",
]

# ==============================================================================
# LEAD 2: Architect Scene Unabridged Dialogue & Nuances
# English canonical, TV Neos dialogue, Dutch subtitle matches
# ==============================================================================
architect_cands = [
    # Right before choice: The two doors and truth
    "Which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning, and end.",
    "Which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning and end.",
    "which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning, and end",
    "which brings us at last to the moment of truth wherein the fundamental flaw is ultimately expressed and the anomaly revealed as both beginning and end",
    "the anomaly revealed as both beginning, and end",
    "the anomaly revealed as both beginning and end",
    "both beginning, and end",
    "both beginning and end",
    "beginning and end",
    
    # The two doors
    "There are two doors. The door to your right leads to the Source, and the salvation of Zion. The door to your left leads back into the Matrix, to her, and to the end of your species.",
    "There are two doors. The door to your right leads to the source, and the salvation of Zion. The door to the left leads back to the matrix, to her, and to the end of your species.",
    "The door to your right leads to the Source, and the salvation of Zion. The door to your left leads back into the Matrix, to her, and to the end of your species.",
    "The door to your right leads to the source, and the salvation of Zion.",
    "The door to your left leads back into the Matrix, to her, and to the end of your species.",
    "The door to the left leads back to the matrix, to her, and to the end of your species.",
    "the door to your right leads to the source, and the salvation of zion",
    "the door to your left leads back to the matrix, to her, and to the end of your species",
    "the door to your right leads to the source and the salvation of zion",
    "the door to your left leads back to the matrix to her and to the end of your species",
    "the salvation of zion", "salvation of zion", "salvation of Zion",
    
    # The choice & dying quote
    "As you adequately put, the problem is choice. But we already know what you're going to do, don't we? Already I can see the chain reaction, the chemical precursors that signal the onset of emotion, designed specifically to overwhelm logic, and reason. An emotion that is already blinding you from the simple, and obvious truth: she is going to die, and there is nothing that you can do to stop it.",
    "As you adequately put, the problem is choice.",
    "As you adequately put, the problem is choice",
    "as you adequately put, the problem is choice",
    "as you adequately put the problem is choice",
    "The problem is choice.", "The problem is choice",
    "the problem is choice.", "the problem is choice", "theproblemischoice",
    "Choice. The problem is choice.", "Choice. The problem is choice",
    "choice. the problem is choice", "choice the problem is choice",
    "she is going to die, and there is nothing that you can do to stop it.",
    "she is going to die, and there is nothing that you can do to stop it",
    "she is going to die and there is nothing that you can do to stop it",
    "she is going to die, and there is nothing you can do to stop it.",
    "she is going to die, and there is nothing you can do to stop it",
    "she is going to die and there is nothing you can do to stop it",
    "she is going to die and that there is nothing you can do to stop it",
    "she is going to die", "sheisgoingtodie",
    "there is nothing that you can do to stop it.",
    "there is nothing that you can do to stop it",
    "there is nothing you can do to stop it.",
    "there is nothing you can do to stop it",
    "nothing that you can do to stop it.",
    "nothing that you can do to stop it",
    "nothing you can do to stop it.",
    "nothing you can do to stop it",
    "you can do to stop it", "can do to stop it", "to stop it", "stop it", "stopit",
    
    # Neo's lines in the scene
    "No!", "No.", "No", "no", "Trinity.", "Trinity", "trinity",
    "If I were you, I would hope that we don't meet again.",
    "If I were you, I would hope that we don't meet again",
    "If I were you, I would hope we don't meet again.",
    "If I were you, I would hope we don't meet again",
    "if i were you, i would hope that we don't meet again",
    "if i were you, i would hope we don't meet again",
    "if i were you i would hope that we dont meet again",
    "if i were you i would hope we dont meet again",
    "i would hope that we don't meet again",
    "i would hope we don't meet again",
    "hope that we don't meet again",
    "hope we don't meet again",
    "we don't meet again", "we dont meet again", "wedontmeetagain",
    "We won't.", "We won't", "We wont.", "We wont",
    "we won't.", "we won't", "we wont.", "we wont", "wewont",
    
    # Hope monologue
    "Humph. Hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness.",
    "Humph. Hope. It is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness.",
    "Humph. Hope, it is the quintessential human delusion, simultaneously the source of your greatest strength and your greatest weakness.",
    "Hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness.",
    "Hope. It is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness.",
    "hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness",
    "hope, it is the quintessential human delusion",
    "hope it is the quintessential human delusion",
    "the quintessential human delusion",
    "the source of your greatest strength, and your greatest weakness",
    "the source of your greatest strength and your greatest weakness",
    "Hope..", "Hope.", "Hope", "hope",
    
    # Dutch Subtitle matches (verbatim from official Dutch srt)
    "Ze gaat dood en je kunt er niets aan doen om dat te stoppen",
    "ze gaat dood en je kunt er niets aan doen om dat te stoppen",
    "zegaatdoodenjekunternietsaandoenomdattestoppen",
    "Ze gaat dood en je kunt er niets aan doen om het te stoppen",
    "ze gaat dood en je kunt er niets aan doen om het te stoppen",
    "Ze zal sterven en je kunt er niets aan doen om dat te stoppen",
    "ze zal sterven en je kunt er niets aan doen om dat te stoppen",
    "Ze zal sterven en je kunt er niets aan doen om het te stoppen",
    "ze zal sterven en je kunt er niets aan doen om het te stoppen",
    "Ze gaat dood en je kunt er niets aan doen",
    "ze gaat dood en je kunt er niets aan doen",
    "Ze zal sterven en je kunt er niets aan doen",
    "ze zal sterven en je kunt er niets aan doen",
    "je kunt er niets aan doen om dat te stoppen",
    "je kunt er niets aan doen om het te stoppen",
    "om dat te stoppen", "om het te stoppen",
    "Dat doen we ook niet.", "Dat doen we ook niet", "dat doen we ook niet",
    "datdoenweookniet",
    "Dat doen we niet.", "Dat doen we niet", "dat doen we niet", "datdoenweniet",
    "Dat zullen we niet.", "Dat zullen we niet", "dat zullen we niet", "datzullenweniet",
    "Als ik jou was, zou ik hopen dat we elkaar niet meer ontmoeten.",
    "Als ik jou was zou ik hopen dat we elkaar niet meer ontmoeten",
    "als ik jou was zou ik hopen dat we elkaar niet meer ontmoeten",
    "alsikjouwaszouikhopendatweelkaarnietmeerontmoeten",
    "Als ik jou was, zou ik hopen dat we elkaar niet meer zien.",
    "Als ik jou was zou ik hopen dat we elkaar niet meer zien",
    "als ik jou was zou ik hopen dat we elkaar niet meer zien",
    "alsikjouwaszouikhopendatweelkaarnietmeerzien",
    "Hoop. Het is de ultieme menselijke illusie, tegelijkertijd de bron van je grootste kracht en je grootste zwakte.",
    "Hoop. Het is de ultieme menselijke illusie",
    "Hoop. Het is de ultieme menselijke waan",
    "het is de ultieme menselijke illusie",
    "het is de ultieme menselijke waan",
    "de ultieme menselijke illusie", "de ultieme menselijke waan",
    "ultieme menselijke illusie", "ultieme menselijke waan",
    "de bron van je grootste kracht en je grootste zwakte",
    "de bron van je grootste kracht, en je grootste zwakte",
    "Zoals je het zelf al zei: het probleem is keuze",
    "zoals je het zelf al zei: het probleem is keuze",
    "zoals je het zelf al zei het probleem is keuze",
    "het probleem is keuze", "het probleem is de keuze",
    "hetprobleemiskeuze", "dekeuze", "keuze",
    "Er zijn twee deuren.", "Er zijn twee deuren", "er zijn twee deuren",
    "De deur rechts van je leidt naar de Bron, en naar de redding van Zion.",
    "De deur links van je leidt terug naar de Matrix, naar haar en naar het einde van jullie soort.",
    "de deur links van je leidt terug naar de matrix, naar haar en naar het einde van jullie soort",
    "de deur rechts van je leidt naar de bron, en naar de redding van zion",
    "redding van zion", "reddingvanzion",
]

# ==============================================================================
# LEAD 3: "Surface" & "In Front of Your Eyes" Page Objects
# Jrk (2023-08-06): "My hat off to you, and you know why 🫡" to "answer lies on the surface?"
# 2023-02-23 roadmap: "we wont give away thepassword its in front of your eyes but yourenotseeingit"
# ==============================================================================
surface_cands = [
    # Surface expressions
    "The answer lies on the surface", "the answer lies on the surface",
    "theanswerliesonthesurface", "answer lies on the surface", "answerliesonthesurface",
    "on the surface", "onthesurface",
    "The flower blossoms through what seems to be a concrete surface",
    "the flower blossoms through what seems to be a concrete surface",
    "a concrete surface", "concrete surface", "concretesurface",
    "In front of your eyes", "in front of your eyes", "infrontofyoureyes",
    "its in front of your eyes but yourenotseeingit",
    "it's in front of your eyes but you're not seeing it",
    "its in front of your eyes but you're not seeing it",
    "it's in front of your eyes but yourenotseeingit",
    "in front of your eyes but yourenotseeingit",
    "in front of your eyes but you're not seeing it",
    "yourenotseeingit", "you're not seeing it", "not seeing it",
    "very last step is a true give away promised",
    "verylaststepisatruegiveawaypromised",
    "a true give away promised", "true give away promised", "truegiveawaypromised",
    
    # Exact salphaseion.html visible text
    "SalPhaseIon", "salphaseion", "Cosmic Duality", "cosmic duality", "cosmicduality",
    "SalPhaseIon Cosmic Duality", "salphaseion cosmic duality",
    "GSMG Puzzle", "gsmg puzzle", "gsmgpuzzle",
    "GSMG MEGANIGMA || 5 BTC", "GSMG MEGANIGMA 5 BTC", "GSMG MEGANIGMA",
    "gsmg meganigma", "gsmgmeganigma",
    "FOLLOW THE WHITE RABBIT", "Follow the white rabbit", "follow the white rabbit",
    "followthewhiterabbit", "whiterabbit", "white rabbit",
    "A CRYPTOGRAPHIC PUZZLE CHALLENGE", "a cryptographic puzzle challenge",
    "acryptographicpuzzlechallenge",
    "Globally supporting my generation", "Globally Supporting My Generation",
    "globally supporting my generation", "globallysupportingmygeneration",
    
    # Addresses and title combinations
    "GSMGIO5BTCPUZZLECHALLENGE",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
    "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "GSMGIO5BTCPUZZLECHALLENGE17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32",
    
    # The two commands in salphaseion.html
    "our first hint is your last command", "ourfirsthintisyourlastcommand",
    "shabef our first hint is your last command", "shabefourfirsthintisyourlastcommand",
    "shabef ans too", "shabefanstoo", "ans too", "anstoo", "ans",
    "matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword",
    "matrixsumlist enter lastwordsbeforearchichoice thispassword",
    "matrixsumlistenterlastwordsbeforearchichoicethispassword",
    "matrixsumlist enter lastwordsbeforearchichoice thispassword enter",
    "matrixsumlistenterlastwordsbeforearchichoicethispasswordenter",
    "lastwordsbeforearchichoice thispassword",
    "lastwordsbeforearchichoicethispassword",
    "lastwordsbeforearchichoice enter",
    "lastwordsbeforearchichoiceenter",
    
    # "our first hint is your last command" pairings
    "follow the white rabbit enter", "followthewhiterabbitenter",
    "follow the white rabbit\n", "follow the white rabbit\r\n",
    "theseedisplanted enter", "theseedisplantedenter",
    "theflowerblossomsthroughwhatseemstobeaconcretesurface enter",
    "theflowerblossomsthroughwhatseemstobeaconcretesurfaceenter",
    "hashthetext enter", "hashthetextenter", "HASHTHETEXT enter", "HASHTHETEXTenter",
    "hashthetext\n", "HASHTHETEXT\n",
    "causality enter", "causalityenter",
]

# ==============================================================================
# LEAD 4: Phase 3.2 Beaufort Modified Monologue Nuances
# The creator's exact modifications to the Architect's speech
# ==============================================================================
phase32_cands = [
    "REINSERTING THE PRIME BASICS AFTER WHICH YOU WILL BE REQUIRED TO SELECT FROM OVER TWENTY THREE CIPHERS SIXTEEN ENCRYPTIONS AND OR SEVEN INTERTWINED PASSWORDS TO FIND THE ACTUAL PRIVATE KEY",
    "reinserting the prime basics after which you will be required to select from over twenty three ciphers sixteen encryptions and or seven intertwined passwords to find the actual private key",
    "reinserting the prime basics after which you will be required to select",
    "reinserting the prime basics", "reinserting the prime basics after which",
    "reinsertingtheprimebasics", "the prime basics", "theprimebasics",
    "prime basics", "primebasics",
    "twenty three ciphers sixteen encryptions and or seven intertwined passwords",
    "twenty three ciphers, sixteen encryptions and or seven intertwined passwords",
    "twenty three ciphers sixteen encryptions and seven intertwined passwords",
    "sixteen encryptions and or seven intertwined passwords",
    "seven intertwined passwords", "seven intertwined",
    "note that also brute forcing might be required",
    "notethatalsobruteforcingmightberequired",
    "brute forcing might be required", "bruteforcingmightberequired",
    "GOOD LUCK NEVERTHELESS I REALLY HOPE YOURE THE ONE CIAO BELLA O",
    "good luck nevertheless i really hope youre the one ciao bella o",
    "good luck nevertheless, i really hope you're the one. ciao bella o",
    "i really hope youre the one ciao bella o",
    "i really hope you're the one ciao bella o",
    "ciao bella o", "ciao bella", "ciaobellao", "ciaobella",
    "i really hope youre the one", "i really hope you're the one",
    "youre the one", "you're the one", "youretheone", "youre the one.",
    "take the private key youve earned it",
    "take the private key you've earned it",
    "worth hundred fourty of the investment",
    "hundred fourty of the investment",
    "hundred fourty", "hundredfourty",
    "worth hundred forty of the investment",
    "hundred forty", "hundredforty",
    
    # Checkerboard decoded message nuances
    "incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive",
    "in case you manage to crack this the private keys belong to half and better half and they also need funds to live",
    "the private keys belong to half and better half and they also need funds to live",
    "the private keys belong to half and better half",
    "theprivatekeysbelongtohalfandbetterhalf",
    "they also need funds to live", "theyalsoneedfundstolive",
    "need funds to live", "needfundstolive", "funds to live", "fundstolive",
    "half and better half", "halfandbetterhalf", "better half", "betterhalf",
    "my better half", "mybetterhalf", "the better half", "thebetterhalf",
    
    # Hint below numbers
    "Raising the stakes without extra chances of winning. A fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as the first one seen.",
    "Raising the stakes without extra chances of winning.",
    "raising the stakes without extra chances of winning",
    "raising the stakes", "raisingthestakes",
    "A fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as the first one seen.",
    "a fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as the first one seen",
    "as wide as the first one seen", "aswideasthefirstoneseen",
    "sad board but as wide as the first one seen",
    "fubcdora/lethingkymvpszjqwx.",
]

def run_all():
    print("=== EXECUTING SYSTEMATIC CRYPTANALYTIC SWEEPS ===")
    h1 = run_sweep(cartman_cands, "LEAD 1: South Park / Cartman & Friends")
    h2 = run_sweep(architect_cands, "LEAD 2: Architect Scene Nuances & Dutch")
    h3 = run_sweep(surface_cands, "LEAD 3: Surface & Page Objects")
    h4 = run_sweep(phase32_cands, "LEAD 4: Phase 3.2 Monologue & Checkerboard")
    
    total_hits = len(h1) + len(h2) + len(h3) + len(h4)
    print(f"\n=== FINISHED ALL SWEEPS. TOTAL HITS: {total_hits} ===")
    return total_hits

if __name__ == '__main__':
    run_all()
