#!/usr/bin/env python3
"""Sweep candidate phrases from the Phase 3.2 Architect speech around
'reinserting the prime basics', 'return to the source codes',
and the selection of 'twenty three ciphers sixteen encryptions and or seven intertwined passwords'.
Tests all 3 blobs (small, inner, cosmic) under sha256 and md5 EVP KDFs,
checking printable text and target secp256k1 addresses.
"""
import sys, os, time, re, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from systematic_solver import run_sweep

# Sentences and subphrases from the Phase 3.2 speech
PHRASES = [
    # Around the choice / selection
    "reinserting the prime basics",
    "reinserting the prime basics.",
    "reinserting the prime basic",
    "reinserting prime basics",
    "reinserting prime basic",
    "reinsertingtheprimebasics",
    "reinserting the prime basics after which you will be required to select",
    "after which you will be required to select",
    "you will be required to select",
    "required to select",
    "select from over twenty three ciphers sixteen encryptions and or seven intertwined passwords",
    "select from over twenty three ciphers sixteen encryptions and or seven intertwined passwords to find the actual private key",
    "over twenty three ciphers sixteen encryptions and or seven intertwined passwords",
    "twenty three ciphers sixteen encryptions and or seven intertwined passwords",
    "twenty three ciphers",
    "sixteen encryptions",
    "seven intertwined passwords",
    "twentythreecipherssixteenencryptionsandorsevenintertwinedpasswords",
    "twentythreeciphers",
    "sixteenencryptions",
    "sevenintertwinedpasswords",
    
    # Return to source codes
    "the function of the you is now to return to the source codes",
    "the function of the one is now to return to the source codes",
    "the function of the you is now to return to the source code",
    "the function of the you is now to return to the source",
    "function of the you is now to return to the source codes",
    "to return to the source codes",
    "return to the source codes",
    "return to the source code",
    "return to the source",
    "the source codes",
    "the source code",
    "source codes",
    "source code",
    "thefunctionoftheyouisnowtoreturntothesourcecodes",
    "returntothesourcecodes",
    "returntothesource",
    
    # Temporary dissemination
    "allowing a temporary dissemination of the code you hopefully carry",
    "temporary dissemination of the code you hopefully carry",
    "allowing a temporary dissemination of the code you hopefully carry reinserting the prime basics",
    "temporary dissemination",
    "the code you hopefully carry",
    "code you hopefully carry",
    "thecodeyouhopefullycarry",
    "temporarydissemination",
    
    # Beginning of the speech
    "your life is the sum of a remainder of an unbalanced equation inherent to the programming of this puzzle",
    "your life is the sum of a remainder of an unbalanced equation",
    "the sum of a remainder of an unbalanced equation",
    "a remainder of an unbalanced equation",
    "unbalanced equation",
    "yourlifeisthesumofaremainderofanunbalancedequationinherenttotheprogrammingofthispuzzle",
    "yourlifeisthesumofaremainderofanunbalancedequation",
    "thesumofaremainderofanunbalancedequation",
    "unbalancedequation",
    
    # Anomaly
    "you are the eventuality of an anomaly which despite my sincerest efforts i have been unable to eliminate",
    "you are the eventuality of an anomaly",
    "the eventuality of an anomaly",
    "eventuality of an anomaly",
    "youaretheeventualityofananomaly",
    "harmony of mathematical precision",
    "a harmony of mathematical precision",
    "harmonyofmathematicalprecision",
    
    # Questions & Wise man
    "you havent answered my question",
    "you haven't answered my question",
    "you: you havent answered my question",
    "me: quite right",
    "quite right. interesting. that was quicker than the others",
    "that was quicker than the others",
    "what a wise man above hinted at is worth hundred fourty of the investment",
    "what a wise man above hinted at is worth hundred forty of the investment",
    "worth hundred fourty of the investment",
    "worth hundred forty of the investment",
    "hundred fourty of the investment",
    "hundred forty of the investment",
    "worth hundred fourty",
    "worth hundred forty",
    "hundred fourty",
    "hundred fourty%",
    "hundred forty%",
    "hundredfourty",
    "hundredfourtyoftheinvestment",
    "what us guys at gsmg are trying to accomplish in the end",
    "what us guys at gsmg are trying to accomplish",
    "that's what us guys at gsmg are trying to accomplish",
    "gsmg are trying to accomplish",
    
    # End of the speech
    "note that also bruteforcing might be required",
    "bruteforcing might be required",
    "notethatalsobruteforcingmightberequired",
    "failure to comply with this process will result in a cataclysmic system crash",
    "cataclysmic system crash",
    "cataclysmicsystemcrash",
    "killing your willpower",
    "killing your will power",
    "extermination of your will to live",
    "extinction of the entireness of yourself self",
    "extinction of the entireness of yourself",
    "the extinction of the entireness of yourself self",
    "the entireness of yourself self",
    "entireness of yourself self",
    "entireness of yourself",
    "yourself self",
    "yourselfself",
    "good luck nevertheless",
    "good luck nevertheless. i really hope youre the one",
    "good luck nevertheless. i really hope you're the one",
    "i really hope youre the one",
    "i really hope you're the one",
    "i really hope youre the one. ciao bella o",
    "i really hope you're the one. ciao bella o",
    "hope youre the one",
    "hope you're the one",
    "youre the one",
    "you're the one",
    "ciao bella o",
    "ciao bella o.",
    "ciaobellao",
    "ciao bella",
    "ciaobella",
    "bella ciao",
    "bellaciao",
]

all_cands = set(PHRASES)
print(f"Total speech candidates to sweep: {len(all_cands)}")

out_hits = run_sweep(list(all_cands), label="speech_phrases_sweep")
print(f"Sweep completed. Structured hits: {len(out_hits)}")
if out_hits:
    for h in out_hits:
        print(f"HIT: {h}")
