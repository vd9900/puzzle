#!/usr/bin/env python3
"""Sweep compound hash chains and combinations of 'our first hint' and 'your last command',
including embedded binary command 'enter', audio clue 'HASHTHETEXT', 'follow the white rabbit',
and SalPhaseIon delimiters.
Tests all 3 AES blobs and target secp256k1 addresses.
Completely offline, deterministic, and self-auditing.
"""
import sys, os, hashlib, json, time, itertools, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import BLOBS, evp, sha256hex, DBBI, FAED, BIN1, Z1, Z2, Z3
from tools.gsmg import candidate_addresses, TARGET_ADDRESS, CURVE_ORDER as N
from systematic_solver import check_password, verify_body, forms_of, run_sweep

ADDR_HALF = TARGET_ADDRESS # 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe
ADDR_BETTER = '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
TARGETS = {ADDR_HALF, ADDR_BETTER}

first_hints = [
    "followthewhiterabbit",
    "follow the white rabbit",
    "Follow the white rabbit",
    "thewhiterabbit",
    "whiterabbit",
    "white rabbit",
    "hashthetext",
    "hash the text",
    "HASHTHETEXT",
    "theseedisplanted",
    "the seed is planted",
    "The seed is planted",
    "salphaseion",
    "SalPhaseIon",
    "yellowblueprimes",
    "yellow blue primes",
    "matrixsumlist",
    "choiceisanillusion",
    "choice is an illusion",
    "choiceisanillusioncreatedbetweenthosewithpowerandthosewithout",
    "averyspecialdessertiwroteitmyself",
    "purplepill",
    "infrared",
    "bingo",
    "causality",
    "wake up, you",
    "wakeupyou",
    "thematrixhasyou",
    "ourfirsthint",
    "our first hint"
]

last_commands = [
    "enter",
    "ENTER",
    "\n",
    "\r\n",
    "lastwordsbeforearchichoice",
    "last words before archi choice",
    "thispassword",
    "this password",
    "shabef",
    "sha256",
    "hashthetext",
    "HASHTHETEXT",
    "wewont",
    "we won't",
    "ciaobellao",
    "yourlastcommand",
    "your last command"
]

phrases = [
    "our first hint is your last command",
    "ourfirsthintisyourlastcommand",
    "OUR FIRST HINT IS YOUR LAST COMMAND",
    "our first hint might be your last command",
    "ourfirsthintmightbeyourlastcommand",
    "my first hint might be your last command",
    "myfirsthintmightbeyourlastcommand",
    "first hint is your last command",
    "firsthintisyourlastcommand",
    "first hint your last command",
    "firsthintlastcommand",
    "shabef our first hint is your last command",
    "shabefourfirsthintisyourlastcommand",
    "shabef anstoo",
    "shabef anstoo",
    "shabefanstoo",
    "shabef ans too",
    "ans too",
    "anstoo",
    "secondanswer",
    "second answer"
]

candidates = set(phrases)

# Pair combinations: first_hint + last_command
for fh in first_hints:
    candidates.add(fh)
    for lc in last_commands:
        candidates.add(f"{fh}{lc}")
        candidates.add(f"{fh} {lc}")
        candidates.add(f"{fh}_{lc}")
        candidates.add(f"{fh}:{lc}")
        candidates.add(f"{fh};{lc}")
        
        # Hash chains
        h_fh = sha256hex(fh)
        h_lc = sha256hex(lc)
        candidates.add(f"{h_fh}{lc}")
        candidates.add(f"{fh}{h_lc}")
        candidates.add(f"{h_fh}{h_lc}")
        candidates.add(f"{h_fh} {lc}")
        candidates.add(f"{fh} {h_lc}")
        
        # Double hashes
        candidates.add(sha256hex(f"{fh}{lc}"))
        candidates.add(sha256hex(f"{fh} {lc}"))

# Z-tokens + delimiters combinations
# Z1 = "lastwordsbeforearchichoice", Z2 = "thispassword", BIN1 = "matrixsumlist", BIN2 = "enter"
z_tokens = ["matrixsumlist", "enter", "lastwordsbeforearchichoice", "thispassword"]
for r in range(1, len(z_tokens) + 1):
    for p in itertools.permutations(z_tokens, r):
        candidates.add("".join(p))
        candidates.add(" ".join(p))
        candidates.add("_".join(p))
        # concatenated hashes
        candidates.add("".join(sha256hex(t) for t in p))
        # XOR of hashes
        xor_hash = bytes(32)
        for t in p:
            xor_hash = bytes(a ^ b for a, b in zip(xor_hash, hashlib.sha256(t.encode()).digest()))
        candidates.add(xor_hash.hex())

cands_list = sorted(list(candidates))
print(f"Generated {len(cands_list)} candidate strings for Hint & Command chains.")

hits = run_sweep(cands_list, label="Hint_Command_Chains")

print(f"\nFinal Summary: {len(cands_list)} candidates tested.")
print(f"Structured AES Hits: {len(hits)}")
