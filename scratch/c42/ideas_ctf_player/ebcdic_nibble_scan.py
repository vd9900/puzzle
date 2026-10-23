"""Creator demonstrably used IBM EBCDIC 1141 in Phase 3.2. In EBCDIC, letters are zone+digit nibbles:
a-i=81-89, j-r=91-99, s-z=A2-A9 (upper C/D/E same low nibbles), space=40 (low nibble 0 -> 'o'/zero), digits F0-F9.
Hypothesis: page a..i strings are the EBCDIC LOW NIBBLES (1..9) of a connected text (no spaces -> no zeros).
This map differs from the cycle-41 digital-root map for s..z (s->2 not 1, ..., z->9 not 8; r->9 same).
Known-plaintext scan (identity + isomorph), shuffled-target controls. No telegram/chat corpora used."""
import sys, re, random, glob, os
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
R56 = ''.join(c for c in DBBI.replace('be', '') if c != 'b')
targets = {'FAED': FAED, 'FAEDrev': FAED[::-1], 'DBBI': DBBI, 'DBBIrev': DBBI[::-1], 'R60': R60, 'R61': R60+'e', 'R56': R56}
def nib(c):
    i=ord(c)-97
    if i<9: return i+1
    if i<18: return i-8
    return i-16   # s(18)->2 ... z(25)->9
assert [nib(c) for c in 'airjsz']==[1,9,9,1,2,9]
def enc(t): return ''.join(chr(96+nib(c)) for c in t)
def letters(s): return re.sub('[^a-z]', '', s.lower())
B='/home/vin/bitcoin_puzzle'
corp={}
files=glob.glob(B+'/research/artifacts/phase*.txt')+glob.glob(B+'/scratch/c38/fresco/texts/*djvu.txt')+[B+'/scratch/corpora/puzzle_texts.txt',B+'/data/user_supplied/cosmic_duality/full.txt']
for f in files:
    if os.path.exists(f): corp[os.path.basename(f)]=letters(open(f,errors='replace').read())
print({k:len(v) for k,v in corp.items()})
K=10
def canon(s):
    m={}; return tuple(m.setdefault(c,len(m)) for c in s)
def scan(tg, iso):
    idx={}
    for name,t in tg.items():
        for i in range(len(t)-K+1):
            idx.setdefault(canon(t[i:i+K]) if iso else t[i:i+K],[]).append((name,i))
    best=[]
    for cn,ct in corp.items():
        e=enc(ct)
        for j in range(len(e)-K+1):
            w=e[j:j+K]; key=canon(w) if iso else w
            if key in idx:
                if sum(c>'i' for c in ct[j:j+K])<4: continue
                for name,i in idx[key]:
                    t=tg[name]; L=K
                    while i+L<len(t) and j+L<len(e) and ((canon(t[i:i+L+1])==canon(e[j:j+L+1])) if iso else t[i+L]==e[j+L]): L+=1
                    best.append((L,name,i,cn,j,ct[j:j+L]))
    best.sort(reverse=True); return best
for iso in (False,True):
    real=scan(targets,iso); rr=random.Random(3); cb=[]
    for _ in range(3):
        sh={k:''.join(rr.sample(v,len(v))) for k,v in targets.items()}
        c=scan(sh,iso); cb.append(c[0][0] if c else 0)
    print(f'{"ISO" if iso else "IDENTITY"} K={K}: matches={len(real)} longest={real[0][0] if real else 0} control longest={cb}')
    for r in real[:5]: print('  ',r)
