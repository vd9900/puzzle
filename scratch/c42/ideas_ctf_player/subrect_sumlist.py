# Hypothesis: a "matrix sum list" = the list of sums over ALL sub-rectangles (or sub-squares) of a small matrix.
# Length fingerprints: 91 = T(1)T(13) (all contiguous sublists of a 13-list; 13 = len('matrixsumlist'))
#                      91 = 1^2+..+6^2 (all sub-squares of 6x6); 60 = T(3)T(4) (R60 = sub-rectangles of 3x4)
#                      570 = T(2)T(19) (sub-rectangles of 2x19); 285 = 1^2+..+9^2 (each faed half = sub-squares of 9x9)
# Self-verifying: 1x1 entries fix the base matrix (mod 9 / mod 10); all other entries must then match (chance 1/9 each).
import sys, itertools, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
D=lambda s:[ord(c)-96 for c in s]
def rects(m,n,squares=False):
    out=[]
    for r0 in range(m):
        for c0 in range(n):
            for h in range(1,m-r0+1):
                for w in range(1,n-c0+1):
                    if squares and h!=w: continue
                    out.append((r0,c0,h,w))
    return out
def orderings(R):
    keys=['r0','c0','h','w']
    idx={'r0':0,'c0':1,'h':2,'w':3}
    seen=set()
    for perm in itertools.permutations(keys):
        for signs in itertools.product((1,-1),repeat=4):
            k=lambda t:tuple(s*t[idx[p]] for p,s in zip(perm,signs))
            o=tuple(sorted(R,key=k))
            if o in seen: continue
            seen.add(o); yield (perm,signs),o
def score(seq,order,mod):
    pos={t:i for i,t in enumerate(order)}
    base={}
    for t,i in pos.items():
        if t[2]==1 and t[3]==1: base[(t[0],t[1])]=seq[i]%mod
    ok=0
    for t,i in pos.items():
        s=sum(base[(r,c)] for r in range(t[0],t[0]+t[2]) for c in range(t[1],t[1]+t[3]))%mod
        ok+= (s==seq[i]%mod)
    return ok/len(order)
def run(name,seq,shape,squares,ctrl=20):
    m,n=shape; R=rects(m,n,squares)
    assert len(R)==len(seq),(len(R),len(seq))
    best=(0,None)
    ords=list(orderings(R))
    for lab,o in ords:
        for mod in (9,10):
            sc=score(seq,o,mod)
            if sc>best[0]: best=(sc,(lab,mod))
    # control: shuffled sequences
    cb=[]
    rnd=random.Random(1)
    for _ in range(ctrl):
        sh=seq[:]; rnd.shuffle(sh)
        cb.append(max(score(sh,o,mod) for lab,o in ords for mod in (9,10)))
    print(f'{name:10s} shape={shape} squares={squares} orderings={len(ords)} best={best[0]:.3f} {best[1]}  ctrl max={max(cb):.3f} mean={sum(cb)/len(cb):.3f}')
# planted self-test
rnd=random.Random(7); M=[[rnd.randint(1,9) for _ in range(13)]]
o=sorted(rects(1,13),key=lambda t:(t[3],t[1]))
pl=[ (sum(M[0][t[1]:t[1]+t[3]])-1)%9+1 for t in o]
run('PLANT',pl,(1,13),False,ctrl=3)
run('dbbi',D(DBBI),(1,13),False)
run('dbbi',D(DBBI),(6,6),True)
run('R60',D(R60),(3,4),False)
run('R60',D(R60),(4,3),False)
run('faedA',D(FAED[:285]),(9,9),True,ctrl=5)
run('faedB',D(FAED[285:]),(9,9),True,ctrl=5)
# direct: label 'matrixsumlist' as base
lab='matrixsumlist'
for vname,vals in [('a1z26',[ord(c)-96 for c in lab]),('ascii',[ord(c) for c in lab])]:
    for oname,key in [('len,start',lambda t:(t[3],t[1])),('start,len',lambda t:(t[1],t[3])),('end,len',lambda t:(t[1]+t[3],t[3])),('lenDesc,start',lambda t:(-t[3],t[1]))]:
        o=sorted(rects(1,13),key=key)
        s=''.join('abcdefghi'[(sum(vals[t[1]:t[1]+t[3]])-1)%9] for t in o)
        m=sum(a==b for a,b in zip(s,DBBI))
        print('label-base',vname,oname,s[:30],'matches with dbbi',m,'/91')
