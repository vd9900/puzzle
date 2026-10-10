#!/usr/bin/env python3
"""Round 2 for lens creator_context: double-sha256 ('ans too'), reversal habit, page-text-as-password, short strings, 20 more doors."""
import hashlib, re, itertools, string, sys, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from tools.gsmg import PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE, TARGET_ADDRESS, SECONDARY_ADDRESS
from common import DBBI, FAED, SMALL_B64, INNER_B64, COSMIC_B64, BIN1, BIN2
H = lambda s: hashlib.sha256(s.encode('utf-8', 'surrogatepass')).hexdigest()
W = '/home/vin/bitcoin_puzzle/scratch/wf/'
def lines(fn):
    return [l.rstrip('\n') for l in open(W + fn, encoding='utf-8', errors='replace') if l.strip() and not l.startswith('#')]
LYRIC = "theflowerblossomsthroughwhatseemstobeaconcretesurface"
SALPH_HASH = "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32"
STAGES = ["theseedisplanted", LYRIC, "causality", "SafenetLunaHSM11110", PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE,
          "GSMGIO5BTCPUZZLECHALLENGE", TARGET_ADDRESS, SECONDARY_ADDRESS, "HASHTHETEXT", "lastwordsbeforearchichoice", "thispassword",
          "matrixsumlist", "enter", "anstoo", "ourfirsthintisyourlastcommand", "yinyang", "cosmicduality", "salphaseion", SALPH_HASH, DBBI, FAED]
mine = lines('cands_lens_creator_context.txt') + json.load(open(W + 'cands_lens_creator_context_multiline.json'))
arch = lines('cands_lens_architect_choice.txt') + lines('cands_lens_architect_choice_1141.txt') + lines('cands_lens_architect_choice_2.txt')
def norm_forms(c):
    return {x for x in {c, c.lower(), re.sub(r'\s+', '', c.lower()), re.sub(r'[^a-z0-9]', '', c.lower()), c.upper(), c.strip()} if x}

# ---- A: double / triple sha256 ("shabef ans too" = hash the answer too) ----
A = []
for c in STAGES + mine + arch:
    for f in norm_forms(c):
        h1 = H(f); A.append(h1); A.append(H(h1))          # fastcheck --no-normalize tries raw + sha256 -> covers sha256^2 and sha256^3
A = list(dict.fromkeys(A))
open(W + 'cands_lens_creator_context_double.txt', 'w').write("# lens creator_context r2: sha256hex / sha256hex^2 of every normalized form of stage strings, creator-context cands and the Architect battery (run with fastcheck --no-normalize => tests sha256^2 and sha256^3)\n" + "\n".join(A) + "\n")

# ---- B: reversal habit (Phase-2 hex was reversed, 2023 binary was reversed) ----
B = []
def revs(s):
    out = [s[::-1]]
    h = H(s); out += [h[::-1], "".join(h[i:i+2] for i in range(62, -1, -2))]   # reversed hex string, byte-reversed hash
    return out
for c in STAGES + mine + arch:
    for f in norm_forms(c):
        B += revs(f)
for s in STAGES:  # reversed binary / bit-level
    bits = "".join(format(b, '08b') for b in s.encode()); B.append(bits[::-1]); B.append("".join(chr(int(bits[::-1][i:i+8], 2)) for i in range(0, len(bits), 8)))
B = [x for x in dict.fromkeys(B) if x and '\n' not in x and '\r' not in x]
open(W + 'cands_lens_creator_context_rev.txt', 'w').write("# lens creator_context r2: reversed strings, reversed sha256 hex, byte-reversed hashes, bit-reversed bytes\n" + "\n".join(B) + "\n")

# ---- D: page text / blobs as their own password ("it's in front of your eyes") ----
D = []
toks = ["matrixsumlist", "lastwordsbeforearchichoice", "thispassword", "ourfirsthintisyourlastcommand", "enter", "anstoo"]
for i in range(len(toks)):
    for j in range(i+1, len(toks)+1):
        for sep in ("", " "): D.append(sep.join(toks[i:j]))
        D.append("".join(H(t) for t in toks[i:j]))
D += ["shabef" + t for t in toks] + ["shabef" + H(t) for t in toks]
D += [DBBI, FAED, DBBI + FAED, BIN1, BIN2, DBBI + BIN1 + FAED, SMALL_B64, INNER_B64, COSMIC_B64,
      SMALL_B64.replace("\n", ""), INNER_B64.replace("\n", ""), COSMIC_B64.replace("\n", ""), "U2FsdGVkX1", "Salted__", "SalPhaseIon Cosmic Duality",
      "salphaseioncosmicduality", "GSMG Puzzle SalPhaseIon Cosmic Duality", "gsmgpuzzlesalphaseioncosmicduality", "Cosmic Duality", "cosmicduality",
      "SalPhaseIon", "salphaseion", "GSMG Puzzle", DBBI[:len(DBBI)//2], DBBI[len(DBBI)//2:], FAED[:285], FAED[285:], "-41,-17", "41,17", "-41-17",
      "parcel-41,-17", "estate955", "955", "gsmg.io magic puzzle piece", "White Rabbits everywhere", "whiterabbitseverywhere", "magicpuzzlepiece"]
# "half and better half": halves of the small blob b64 / salph hash
for s in (SALPH_HASH, SMALL_B64.replace("\n", ""), TARGET_ADDRESS):
    D += [s[:len(s)//2], s[len(s)//2:], s[len(s)//2:] + s[:len(s)//2]]
D = [x for x in dict.fromkeys(D) if x and '\n' not in x]
open(W + 'cands_lens_creator_context_pagetext.txt', 'w').write("# lens creator_context r2: SalPhaseIon page tokens/windows, page text, blobs and halves as passwords\n" + "\n".join(D) + "\n")

# ---- C: short strings ('tiny hint' <3) ----
P = [c for c in string.printable if c not in '\t\n\r\x0b\x0c']
AL = string.ascii_lowercase + string.digits
with open(W + 'cands_lens_creator_context_short.txt', 'w') as f:
    f.write("# lens creator_context r2: 'tiny hint' sweep: printable len1-2, alnum len3, lowercase len4, digits len4-5 (fastcheck --no-normalize)\n")
    for n in (1, 2):
        for t in itertools.product(P, repeat=n): f.write("".join(t) + "\n")
    for t in itertools.product(AL, repeat=3): f.write("".join(t) + "\n")
    for t in itertools.product(string.ascii_lowercase, repeat=4): f.write("".join(t) + "\n")
    for n in (4, 5):
        for t in itertools.product(string.digits, repeat=n): f.write("".join(t) + "\n")

# ---- E: doors round 2 (20 probes; mixed-case lines cost 2 probes each) ----
E = ["COSMICDUALITY" + TARGET_ADDRESS, "YINYANG" + TARGET_ADDRESS, "SALPHASEION" + TARGET_ADDRESS, "HASHTHETEXT" + TARGET_ADDRESS,
     "THESEEDISPLANTED" + TARGET_ADDRESS, "WHITERABBITSEVERYWHERE" + TARGET_ADDRESS,
     "detnalpsideeseht", "ootsna", "friends", "yinyangphase", "lasthint", "tinyfraction", "thehardestpartisdone", "youhavealltheinfo"]
open(W + 'cands_lens_creator_context_doors2.txt', 'w').write("# lens creator_context r2 doors: TEXT+address (creator's SalPhaseIon door recipe) and reversed/leftover tokens; 6 mixed-case lines = 2 probes each + 8 lowercase = 20 probes\n" + "\n".join(E) + "\n")
print("double:", len(A), "rev:", len(B), "pagetext:", len(D), "doors2:", len(E))
