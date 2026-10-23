"""Word-search reading of the SalPhaseIon textarea: are there dictionary words (letters a-i only, len>=L) hidden in
dbbi / faed in any of 8 directions for grid widths 1(linear)..60, beyond shuffled controls?  Calibrated, no AES."""
import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
W=set()
for f in ('/usr/share/dict/american-english','/usr/share/dict/british-english'):
    for w in open(f):
        w=w.strip()
        if w.isalpha() and w.islower() and set(w)<=set('abcdefghi'): W.add(w)
def words_in(s, L, widths):
    found=set()
    n=len(s)
    for w in widths:
        for dr,dc in ((0,1),(1,0),(1,1),(1,-1),(0,-1),(-1,0),(-1,-1),(-1,1)):
            if w==0 and (dr,dc) not in ((0,1),(0,-1)): continue
            if w==0:
                lines=[s, s[::-1]] if dc==1 else []
            else:
                rows=[s[i:i+w] for i in range(0,n,w)]
                H=len(rows); lines=[]
                # walk each line in direction
                starts=set()
                for r in range(H):
                    for c in range(w):
                        pr,pc=r-dr,c-dc
                        if not(0<=pr<H and 0<=pc<w and pc<len(rows[pr])): starts.add((r,c))
                for r,c in starts:
                    t=''
                    while 0<=r<H and 0<=c<len(rows[r]):
                        t+=rows[r][c]; r+=dr; c+=dc
                    lines.append(t)
            for t in lines:
                for i in range(len(t)):
                    for j in range(i+L, min(len(t),i+14)+1):
                        if t[i:j] in W: found.add((t[i:j],w))
    return found
L=int(sys.argv[1]) if len(sys.argv)>1 else 6
print('dict a-i words len>=%d:'%L, sum(1 for w in W if len(w)>=L))
widths=[0]+list(range(2,61))
for name,s in (('dbbi',DBBI),('faed',FAED)):
    real=words_in(s,L,widths)
    rw=sorted(set(x[0] for x in real),key=len,reverse=True)
    ctrl=[]
    rng=random.Random(1)
    for k in range(20):
        t=list(s); rng.shuffle(t); t=''.join(t)
        ctrl.append(len(set(x[0] for x in words_in(t,L,widths))))
    print(name,'distinct words',len(rw),'controls mean %.1f max %d'%(sum(ctrl)/len(ctrl),max(ctrl)),'longest',rw[:15])
