# Chain: known-board decode -> letters -> Beaufort / Vigenere / reverse-Vigenere with puzzle keys; score vs random keys.
import json, random
from cb3lib import *
KEYS = ['THEMATRIXHASYOU', 'LASTWORDSBEFOREARCHICHOICE', 'THISPASSWORD', 'MATRIXSUMLIST', 'CAUSALITY', 'COSMICDUALITY', 'WHITERABBIT', 'WHITERABBITSEVERYWHERE',
        'HALFANDBETTERHALF', 'GSMG', 'SALPHASEION', 'JACQUEFRESCO', 'HEISENBERG', 'ARCHITECT', 'MEROVINGIAN', 'THESEEDISPLANTED', 'FOLLOWTHEWHITERABBIT', 'ONEFORONEFOURFORONE',
        'PRIME', 'PRIMES', 'NEO', 'TRINITY', 'MORPHEUS', 'ORACLE', 'KEYMAKER', 'SOURCE', 'ZION', 'ENTER', 'ANSTOO', 'SHABEF', 'MEGANIGMA', 'GIVEIT', 'BTCSEED', 'DBIFHCEGA', 'FAEDGCBHI']
def beaufort(c, k): return ''.join(chr(97 + (ord(k[i % len(k)]) - 65 - (ord(ch) - 97)) % 26) for i, ch in enumerate(c))
def vig_dec(c, k): return ''.join(chr(97 + (ord(ch) - 97 - (ord(k[i % len(k)]) - 65)) % 26) for i, ch in enumerate(c))
def vig_enc(c, k): return ''.join(chr(97 + (ord(ch) - 97 + (ord(k[i % len(k)]) - 65)) % 26) for i, ch in enumerate(c))
rng = random.Random(3)
def randkey(L): return ''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(L))
rows = []; cands = set()
board = make_board(); esc = ('1', '4')
srcs = {}
for sn, s in (('faed', FAED), ('dbbi', DBBI), ('res61', RES61)):
    for mn, tr in (('a0', A0), ('a1', A1)):
        for pm in ('none', 'drop'):
            for rd in (0, 1):
                d = prime_mode(s, pm).translate(tr); d = d[::-1] if rd else d
                srcs[f'{sn}|{mn}|{pm}|revdig={rd}'] = letters(decode(d, board, esc))
for sname, c in srcs.items():
    if len(c) < 20: continue
    for K in KEYS:
        for fn_name, fn in (('beaufort', beaufort), ('vigdec', vig_dec), ('vigenc', vig_enc)):
            t = fn(c, K); q = qscore(t)
            ctrl = [qscore(fn(c, randkey(len(K)))) for _ in range(20)]
            m = sum(ctrl) / 20; sd = (sum((v - m) ** 2 for v in ctrl) / 20) ** .5 or 1e-9
            rows.append({'tag': f'{sname}|{fn_name}|{K}', 'q': round(q, 3), 'z': round((q - m) / sd, 2), 'frags': frags(t), 'text': t})
            cands.add(t)
rows.sort(key=lambda r: -r['z'])
json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/wf/lens_cb3_chain_rows.json', 'w'), indent=0)
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto_chain.txt', 'w') as f:
    for c in sorted(cands): f.write(c + '\n')
print('rows', len(rows), 'cands', len(cands))
for r in rows[:12]: print(r['z'], r['q'], r['tag'], r['frags'], r['text'][:60])
print('frags>=6:', [(r['tag'], r['frags']) for r in rows if any(len(w) >= 6 for w in r['frags'])][:10])
