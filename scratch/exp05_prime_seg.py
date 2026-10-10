from common import *
import random
P=set(primes_upto(200))
def segmentations(s, marker='b', suffix='e', base=1):
    """logical positions base..; prime logical pos must consume marker or marker+suffix; others 1 symbol."""
    out=[]
    def rec(i, lp, toks):
        if i==len(s):
            out.append(list(toks)); return
        if (lp) in P:
            if s[i]==marker:
                rec(i+1, lp+1, toks+[marker])
                if i+1<len(s) and s[i+1]==suffix:
                    rec(i+2, lp+1, toks+[marker+suffix])
        else:
            rec(i+1, lp+1, toks+[s[i]])
    rec(0, base, [])
    return out
segs=segmentations(DBBI)
print('segmentations found:',len(segs), [len(t) for t in segs])
colors='BBBBYBBBYYBBBBYBBYYBWYYBY'  # spiral order incl near-white W at index 20
for t in segs:
    markers=[(i+1,tok) for i,tok in enumerate(t) if (i+1) in P]
    bits=''.join('0' if tok=='b' else '1' for _,tok in markers)
    resid=''.join(tok for i,tok in enumerate(t) if (i+1) not in P)
    print(f'L{len(t)}: {len(markers)} markers b={bits.count("0")} be={bits.count("1")} bits={bits}')
    print('   residual',len(resid),resid)
print('colors as bits (B=0,Y=1,W=?):', colors)
# null: how often does a random shuffle of dbbi admit any segmentation?
r=random.Random(0); l=list(DBBI); hits=0; N=5000
for _ in range(N):
    r.shuffle(l)
    if segmentations(''.join(l)): hits+=1
print('shuffle null: segmentable fraction', hits/N)
# alternative: random strings with same letter counts but require only 'b' (no 'be') at primes?
