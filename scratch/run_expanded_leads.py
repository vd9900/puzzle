#!/usr/bin/env python3
"""Expanded sweep of concrete leads: Mr. Robot endgame, Architect nuances,
Keymaker final words, surface text, and binary hash forms.
"""
import sys, os, hashlib, re, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from systematic_solver import check_password, run_sweep, forms_of

# ==============================================================================
# LEAD A: Mr. Robot Endgame & Inside References
# Creator: "I hope to witness the day that the last scene of mr. Robot becomes a reality"
# Creator: "rewatching mr robot episode 3.5"
# ==============================================================================
mr_robot_cands = [
    # The last scene of Mr. Robot
    "Hello, Elliot.", "Hello Elliot.", "Hello, Elliot", "Hello Elliot", "hello elliot",
    "Hello, friend.", "Hello Friend.", "Hello, friend", "Hello Friend", "hello friend",
    "This only works if you let go too.", "This only works if you let go too",
    "this only works if you let go too", "let go", "let go too",
    "Welcome back, Elliot.", "Welcome back, Elliot", "Welcome back Elliot", "welcome back elliot",
    "The Mastermind", "the mastermind", "mastermind",
    "Redistribution of wealth", "redistribution of wealth", "redistributionofwealth",
    "The greatest redistribution of wealth in human history",
    "the greatest redistribution of wealth in human history",
    "greatest redistribution of wealth in human history",
    "greatest redistribution of wealth",
    "Heroes", "heroes", "David Bowie Heroes",
    "M83 Outro", "M83 - Outro", "Outro", "outro",
    
    # Episode 3.5 & technical strings
    "eps3.5_kill-process.inc", "kill-process", "killprocess", "kill process",
    "eps3.4_runtime-error.r00", "runtime-error", "runtime error",
    "z1on0101", "022350", "e-corp", "ecorp", "evil corp", "evilcorp",
    "fsociety", "f society", "fsociety00.dat",
    "leave me here", "dont delete me", "don't delete me",
    "4161", "11110", "111101110011110110010010"
]

# ==============================================================================
# LEAD B: Keymaker Final Lines & Door Choice
# "It was meant to be. That door will take you home. You'll know which door. Hurry, Neo."
# ==============================================================================
keymaker_cands = [
    "It was meant to be. That door will take you home. You'll know which door. Hurry, Neo.",
    "It was meant to be. That door will take you home. You'll know which door. Hurry, Neo",
    "it was meant to be. that door will take you home. you'll know which door. hurry, neo.",
    "it was meant to be that door will take you home youll know which door hurry neo",
    "It was meant to be. That door will take you home.",
    "it was meant to be. that door will take you home",
    "it was meant to be that door will take you home",
    "That door will take you home. You'll know which door. Hurry, Neo.",
    "That door will take you home. You'll know which door. Hurry, Neo",
    "that door will take you home. you'll know which door. hurry, neo",
    "that door will take you home youll know which door hurry neo",
    "That door will take you home.", "That door will take you home",
    "that door will take you home", "thatdoorwilltakeyouhome",
    "You'll know which door. Hurry, Neo.", "You'll know which door. Hurry, Neo",
    "you'll know which door. hurry, neo", "youll know which door hurry neo",
    "You'll know which door.", "You'll know which door", "you'll know which door", "youll know which door",
    "Hurry, Neo.", "Hurry, Neo", "Hurry Neo", "hurry neo", "hurry, neo", "hurryneo",
    "It was meant to be.", "It was meant to be", "it was meant to be", "itwasmeanttobe"
]

# ==============================================================================
# LEAD C: Architect Speech Precise Fragments & Deviations
# Both movie canonical and Phase 3.2 Beaufort modified variants
# ==============================================================================
architect_nuances = [
    # Right before Neo chooses (door on left):
    "she is going to die, and there is nothing that you can do to stop it.",
    "she is going to die, and there is nothing that you can do to stop it",
    "she is going to die and there is nothing that you can do to stop it",
    "she is going to die and there is nothing you can do to stop it",
    "there is nothing that you can do to stop it.",
    "there is nothing that you can do to stop it",
    "there is nothing you can do to stop it.",
    "there is nothing you can do to stop it",
    "nothing that you can do to stop it.",
    "nothing that you can do to stop it",
    "nothing you can do to stop it.",
    "nothing you can do to stop it",
    "you can do to stop it",
    "can do to stop it",
    "to stop it",
    "stop it",
    "stopit",
    
    # The moment of truth & anomaly
    "Which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning, and end.",
    "which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning, and end",
    "which brings us at last to the moment of truth wherein the fundamental flaw is ultimately expressed and the anomaly revealed as both beginning and end",
    "the anomaly revealed as both beginning, and end",
    "the anomaly revealed as both beginning and end",
    "both beginning, and end",
    "both beginning and end",
    "beginning and end",
    "beginning, and end",
    
    # The two doors
    "There are two doors. The door to your right leads to the source, and the salvation of Zion. The door to the left leads back to the matrix, to her, and to the end of your species.",
    "there are two doors. the door to your right leads to the source, and the salvation of zion. the door to the left leads back to the matrix, to her, and to the end of your species",
    "the door to your right leads to the source, and the salvation of zion",
    "the door to your right leads to the source and the salvation of zion",
    "the door to the left leads back to the matrix, to her, and to the end of your species",
    "the door to the left leads back to the matrix to her and to the end of your species",
    "the door to your left leads back to the matrix, to her, and to the end of your species",
    "the door to your left leads back to the matrix to her and to the end of your species",
    "the door to your right",
    "the door to the left",
    "the door to your left",
    "the source, and the salvation of zion",
    "the source and the salvation of zion",
    "the salvation of zion",
    "salvation of zion",
    "salvation of Zion",
    "salvation",
    
    # Choice quotes
    "As you adequately put, the problem is choice.",
    "as you adequately put, the problem is choice",
    "as you adequately put the problem is choice",
    "Choice. The problem is choice.",
    "Choice. The problem is choice",
    "choice. the problem is choice",
    "choice the problem is choice",
    "The problem is choice.",
    "The problem is choice",
    "the problem is choice",
    "theproblemischoice",
    "the problem is",
    "theproblemis",
    "choice",
    
    # After choice & We won't
    "Humph. Hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness.",
    "humph. hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness",
    "humph hope it is the quintessential human delusion simultaneously the source of your greatest strength and your greatest weakness",
    "Hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness.",
    "hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness",
    "hope it is the quintessential human delusion simultaneously the source of your greatest strength and your greatest weakness",
    "hope, it is the quintessential human delusion",
    "hope it is the quintessential human delusion",
    "the quintessential human delusion",
    "the source of your greatest strength, and your greatest weakness",
    "the source of your greatest strength and your greatest weakness",
    "If I were you, I would hope that we don't meet again.",
    "If I were you, I would hope that we don't meet again",
    "if i were you, i would hope that we don't meet again",
    "if i were you i would hope that we dont meet again",
    "if i were you, i would hope that we dont meet again",
    "i would hope that we don't meet again",
    "i would hope that we dont meet again",
    "hope that we don't meet again",
    "hope that we dont meet again",
    "we don't meet again",
    "we dont meet again",
    "We won't.",
    "We won't",
    "we won't",
    "we won't.",
    "We wont.",
    "We wont",
    "we wont",
    "wewont",
    
    # Phase 3.2 Beaufort unique modifications:
    "reinserting the prime basics after which you will be required to select from over twenty three ciphers sixteen encryptions and or seven intertwined passwords to find the actual private key",
    "reinserting the prime basics after which",
    "reinserting the prime basics",
    "prime basics",
    "primebasics",
    "twenty three ciphers, sixteen encryptions and or seven intertwined passwords",
    "twenty three ciphers sixteen encryptions and or seven intertwined passwords",
    "sixteen encryptions and or seven intertwined passwords",
    "sixteen encryptions and seven intertwined passwords",
    "seven intertwined passwords",
    "seven intertwined",
    "note that also brute forcing might be required",
    "notethatalsobruteforcingmightberequired",
    "brute forcing might be required",
    "bruteforcingmightberequired",
    "good luck nevertheless, i really hope you're the one. ciao bella o",
    "good luck nevertheless i really hope youre the one ciao bella o",
    "ciao bella o", "ciao bella", "ciaobellao", "ciaobella",
    "i really hope you're the one", "i really hope youre the one",
    "you're the one", "youre the one",
    "hundred fourty of the investment", "hundred fourty", "hundredforty"
]

# ==============================================================================
# LEAD D: Surface of the Puzzle & Exact Page Objects
# "the answer lies on the surface", "its in front of your eyes"
# ==============================================================================
surface_cands = [
    "GSMG MEGANIGMA || 5 BTC",
    "GSMG MEGANIGMA",
    "gsmg meganigma",
    "gsmgmeganigma",
    "FOLLOW THE WHITE RABBIT",
    "Follow the white rabbit",
    "follow the white rabbit",
    "followthewhiterabbit",
    "A CRYPTOGRAPHIC PUZZLE CHALLENGE",
    "a cryptographic puzzle challenge",
    "SalPhaseIon", "salphaseion", "SalPhaseIon Cosmic Duality",
    "Cosmic Duality", "cosmic duality", "cosmicduality",
    "GSMG Puzzle", "gsmg puzzle", "gsmgpuzzle",
    "matrixsumlist", "lastwordsbeforearchichoice", "thispassword",
    "our first hint is your last command", "ourfirsthintisyourlastcommand",
    "shabef our first hint is your last command", "shabefourfirsthintisyourlastcommand",
    "shabef ans too", "shabefanstoo", "ans too", "anstoo", "ans",
    "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32",
    "GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "GSMGIO5BTCPUZZLECHALLENGE",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "half and better half", "halfandbetterhalf", "better half", "betterhalf",
    "the private keys belong to half and better half and they also need funds to live",
    "theprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive",
    "fundstolive", "needfundstolive"
]

def run_all():
    print("=== EXECUTING EXPANDED SYSTEMATIC SWEEPS ===")
    run_sweep(mr_robot_cands, "LEAD A: Mr. Robot Clues & End Scene")
    run_sweep(keymaker_cands, "LEAD B: Keymaker Final Words")
    run_sweep(architect_nuances, "LEAD C: Architect Monologue Nuances")
    run_sweep(surface_cands, "LEAD D: Surface Page Objects")
    print("=== FINISHED ALL SWEEPS ===")

if __name__ == '__main__':
    run_all()
