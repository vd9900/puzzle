# Test 0: is faed's letter-frequency profile consistent with a VIC (AT ONE SIR board) English stream mapped a1 with 0 merged?
# Since transposition preserves the multiset, compare sorted profiles. Also the Phase 3.2 board and other plaintext types.
import sys, re, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch/c37/vic_cipher'); sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
import vic, numpy as np
from collections import Counter
from common import FAED
txt=re.sub('[^A-Z]','',open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt').read().upper())
obs=sorted(Counter(FAED).values(),reverse=True)
print('faed sorted', obs)
rnd=random.Random(3)
def board_p32():
    esc=('1','4'); singles=[d for d in '0123456789' if d not in esc]
    b={}
    for d,l in zip(singles,'FUBCDORA'): b[l]=d
    for j,l in enumerate('/LETHINGKY'): b[l]='1'+str(j)
    for j,l in enumerate('MVPSZJQWX.'): b[l]='4'+str(j)
    return b
def stream(enc, n=565):
    st=''; i=rnd.randrange(len(txt)-2000)
    while len(st)<n:
        c=enc.get(txt[i]); i+=1
        if c: st+=c
    return st[:n]
def profile(st, merge_into):  # a1 mapping; digit 0 merged into letter of digit merge_into
    c=Counter(st)
    v={d:c.get(d,0) for d in '123456789'}
    v[merge_into]+=c.get('0',0)
    return sorted(v.values(),reverse=True)
def dist(p,q): return sum(abs(a-b) for a,b in zip(p,q))
res={}
for name in ['ATONESIR','P32']:
    maxs=[]; ds=[]; best=None
    for t in range(3000):
        if name=='ATONESIR':
            S=list(range(10)); rnd.shuffle(S)
            enc,dec,esc=vic.vic_board(S)
        else:
            enc=board_p32()
        st=stream(enc)
        m=rnd.choice('123456789')
        p=profile(st,m)
        maxs.append(p[0]); ds.append(dist(p,obs))
    maxs=np.array(maxs); ds=np.array(ds)
    print(name, 'max-letter count: mean %.1f sd %.1f, frac<=107: %.4f ; L1 dist to faed profile: median %.0f min %.0f'%(maxs.mean(),maxs.std(),(maxs<=107).mean(),np.median(ds),ds.min()))
# Best case: merge chosen to minimise distance (optimistic for the hypothesis)
best=[]
for t in range(2000):
    S=list(range(10)); rnd.shuffle(S); enc,dec,esc=vic.vic_board(S); st=stream(enc)
    best.append(min(dist(profile(st,m),obs) for m in '123456789'))
print('ATONESIR optimistic-merge L1: median', np.median(best), 'min', min(best))
# control: profile distance of i.i.d. samples drawn from faed's own unigram (what L1 a perfect model gives)
c=Counter(FAED); p=np.array([c[x] for x in 'abcdefghi'])/570
ctrl=[dist(sorted(Counter(np.random.default_rng(t).choice(9,570,p=p)).values(),reverse=True),obs) for t in range(2000)]
print('self-model L1: median', np.median(ctrl), '95%', np.percentile(ctrl,95))
