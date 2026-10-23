#!/usr/bin/env python3
"""Test BIP39 mnemonic derived from 38x15 column sums against target addresses and AES blobs."""
import sys, os, hashlib, hmac
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')

from tools.gsmg import candidate_addresses, TARGET_ADDRESS, SECONDARY_ADDRESS, CURVE_ORDER as N
from systematic_solver import check_password, verify_body, forms_of, run_sweep
import bifid

# Target addresses
TARGETS = {TARGET_ADDRESS, SECONDARY_ADDRESS}

# 1. Reconstruct the 15-word mnemonic
sq = bifid.CANON
pos = bifid.coords(sq)
b = bifid.BIF
matrix = [b[r*15:(r+1)*15] for r in range(38)]

col_sums = []
for c_idx in range(15):
    s = sum(pos[matrix[r_idx][c_idx]][0] + pos[matrix[r_idx][c_idx]][1] for r_idx in range(38))
    col_sums.append(s)

with open('/home/vin/bitcoin_puzzle/puzzles/btc02/sources/english.txt') as f:
    words = [line.strip() for line in f if line.strip()]

mnemonic_words = [words[s] for s in col_sums]
mnemonic_str = ' '.join(mnemonic_words)
print("15-word mnemonic:", mnemonic_str)

# Also column sums excluding row 0 (which is "btcseeddeoemcke")
col_sums_no_header = []
for c_idx in range(15):
    s = sum(pos[matrix[r_idx][c_idx]][0] + pos[matrix[r_idx][c_idx]][1] for r_idx in range(1, 38))
    col_sums_no_header.append(s)

mnemonic_words_no_header = [words[s] for s in col_sums_no_header]
mnemonic_str_no_header = ' '.join(mnemonic_words_no_header)
print("37-row mnemonic:", mnemonic_str_no_header)

# Test 1: Mnemonic variations as AES passwords
print("\n--- Testing mnemonics against AES blobs ---")
cands = [
    mnemonic_str,
    mnemonic_str.replace(' ', ''),
    mnemonic_str.replace(' ', ','),
    mnemonic_str.replace(' ', '-'),
    mnemonic_str.replace(' ', '_'),
    mnemonic_str_no_header,
    mnemonic_str_no_header.replace(' ', ''),
    "btcseed " + mnemonic_str,
    "btcseed" + mnemonic_str.replace(' ', ''),
    mnemonic_str + " deoemcke",
    mnemonic_str.replace(' ', '') + "deoemcke",
]
run_sweep(cands, "BIP39 Mnemonic Passphrases")

# Test 2: BIP32 Derivations
print("\n--- Testing BIP32 Master Key & Derivations ---")

def bip39_to_seed(mnemonic, passphrase=""):
    salt = ("mnemonic" + passphrase).encode("utf-8")
    return hashlib.pbkdf2_hmac("sha512", mnemonic.encode("utf-8"), salt, 2048)

def bip32_master(seed):
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    master_k = I[:32]
    master_c = I[32:]
    return master_k, master_c

# secp256k1 point multiplication for BIP32 child derivation
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def priv_to_pub(priv_bytes):
    priv_int = int.from_bytes(priv_bytes, 'big')
    pk = ec.derive_private_key(priv_int, ec.SECP256K1()).public_key()
    return pk.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.CompressedPoint)

def ckd_priv(k_par, c_par, i):
    # hardened if i >= 0x80000000
    if i >= 0x80000000:
        data = b"\x00" + k_par + i.to_bytes(4, 'big')
    else:
        data = priv_to_pub(k_par) + i.to_bytes(4, 'big')
    I = hmac.new(c_par, data, hashlib.sha512).digest()
    I_L = I[:32]
    I_R = I[32:]
    k_i = (int.from_bytes(I_L, 'big') + int.from_bytes(k_par, 'big')) % N
    if k_i == 0 or int.from_bytes(I_L, 'big') >= N:
        return None, None
    return k_i.to_bytes(32, 'big'), I_R

def derive_path(k_m, c_m, path_str):
    k, c = k_m, c_m
    segments = path_str.lstrip("m/").split("/")
    if not segments or segments == ['']:
        return k, c
    for seg in segments:
        hardened = seg.endswith("'") or seg.endswith("h")
        num = int(seg.rstrip("'h"))
        if hardened:
            num += 0x80000000
        k, c = ckd_priv(k, c, num)
        if k is None: return None, None
    return k, c

passphrases = [
    "", "deoemcke", "enter", "half", "betterhalf", "gsmg",
    "lastwordsbeforearchichoice", "thispassword", "salphaseion",
    "thematrixhasyou", "causality", "giveitjustonesecond"
]

paths = [
    "m",
    "m/0", "m/1", "m/0/0", "m/0/1", "m/1/0", "m/1/1",
    "m/0'", "m/1'", "m/0'/0", "m/0'/1",
    "m/44'/0'/0'/0/0", "m/44'/0'/0'/0/1", "m/44'/0'/0'/0/2",
    "m/44'/0'/0'/1/0", "m/44'/0'/0'/1/1",
    "m/49'/0'/0'/0/0", "m/84'/0'/0'/0/0"
]

for mn in [mnemonic_str, mnemonic_str_no_header]:
    for passph in passphrases:
        seed = bip39_to_seed(mn, passph)
        km, cm = bip32_master(seed)
        
        # Also check seed and master key directly as candidates for AES blobs
        check_password(km)
        check_password(seed[:32])
        check_password(seed[32:])
        
        for p in paths:
            k, c = derive_path(km, cm, p)
            if k:
                # Check against target addresses
                ads = candidate_addresses(k)
                for mode, ad in ads.items():
                    if ad in TARGETS:
                        print(f"!!! HIT FOUND BIP32: {ad} at {p} with passphrase '{passph}'!")
                        with open('/home/vin/bitcoin_puzzle/scratch/wf/HITS.log', 'a') as f:
                            f.write(f"BIP32 HIT: {ad} path={p} passph={passph} k={k.hex()}\n")

print("Finished BIP32 derivations check.")
