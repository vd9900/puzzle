"""Known-plaintext scan: is any page block (faed, dbbi, residuals, faed tail) the letter-level digital-root encoding
(a1z26 summed to one digit = (index mod 9)+1, so never 0) of a text we have?  Identity mapping (a..i = 1..9) and
isomorph matching (any relabelling of the 9 symbols). Controls: shuffled targets, same corpora."""
import sys, json, re, random, glob, os
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
R56 = ''.join(c for c in DBBI.replace('be', '') if c != 'b')
targets = {'FAED': FAED, 'FAEDrev': FAED[::-1], 'DBBI': DBBI, 'DBBIrev': DBBI[::-1], 'R60': R60, 'R61': R60 + 'e', 'R56': R56}
def enc(t):  # letters -> a..i by digital root of a1z26
    return ''.join(chr(97 + (ord(c) - 97) % 9) for c in t)
def letters(s): return re.sub('[^a-z]', '', s.lower())
corp = {}
B = '/home/vin/bitcoin_puzzle'
for f in glob.glob(B + '/research/artifacts/phase*.txt') + glob.glob(B + '/scratch/corpora/*.txt') + glob.glob(B + '/scratch/c38/fresco/texts/*djvu.txt'):
    corp[os.path.basename(f)] = letters(open(f, errors='replace').read())
corp['cosmic_duality_book'] = letters(open(B + '/data/user_supplied/cosmic_duality/full.txt', errors='replace').read())
msgs = [json.loads(l)['text'] for l in open(B + '/data/user_supplied/telegram/text_export.jsonl')]
corp['telegram_all'] = letters(' '.join(msgs))
print({k: len(v) for k, v in corp.items()})
K = 11
def canon(s):
    m = {}; return tuple(m.setdefault(c, len(m)) for c in s)
def scan(tg, iso):
    idx = {}
    for name, t in tg.items():
        for i in range(len(t) - K + 1):
            key = canon(t[i:i+K]) if iso else t[i:i+K]
            idx.setdefault(key, []).append((name, i))
    best = []
    for cn, ct in corp.items():
        e = enc(ct)
        for j in range(len(e) - K + 1):
            w = e[j:j+K]
            key = canon(w) if iso else w
            if key in idx:
                if sum(c > 'i' for c in ct[j:j+K]) < 4:  # source must be real text, not a pasted a..i puzzle string
                    continue
                for name, i in idx[key]:
                    t = tg[name]; L = K
                    while i + L < len(t) and j + L < len(e) and (
                        (canon(t[i:i+L+1]) == canon(e[j:j+L+1])) if iso else (t[i+L] == e[j+L])): L += 1
                    if len(set(ct[j:j+L])) <= 9:  # relabelled copy of a puzzle string, not real text
                        continue
                    best.append((L, name, i, cn, j, ct[j:j+L]))
    best.sort(reverse=True)
    return best
for iso in (True,):
    real = scan(targets, iso)
    rr = random.Random(3); ctrl_best = []
    for rep in range(2):
        sh = {k: ''.join(rr.sample(v, len(v))) for k, v in targets.items()}
        cb = scan(sh, iso); ctrl_best.append(cb[0][0] if cb else 0)
    print(f'\n=== {"ISOMORPH (any relabelling)" if iso else "IDENTITY (a..i = 1..9)"}  K={K}: real matches={len(real)}  longest={real[0][0] if real else 0}  control longest={ctrl_best}')
    seen = set()
    for L, name, i, cn, j, src in real[:12]:
        if (name, i) in seen: continue
        seen.add((name, i)); print(f'  len {L:2} {name}[{i}] <- {cn}[{j}]: {src}')
