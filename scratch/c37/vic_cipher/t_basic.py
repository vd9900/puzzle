import sys, re, random, time
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch/c37/vic_cipher')
import vic, vicfast as V
import numpy as np
# 1. untranspose_index consistency with vic.py decoders
rnd=random.Random(1)
for _ in range(50):
    n=565; Q=[rnd.randrange(10) for _ in range(rnd.randint(8,29))]; R=[rnd.randrange(10) for _ in range(rnd.randint(8,29))]
    s=''.join(rnd.choice('0123456789') for _ in range(n))
    ct=vic.disrupted_enc(vic.columnar_enc(s,Q),R)
    idx=V.untranspose_index(n,Q,R)
    assert ''.join(ct[i] for i in idx)==s
    ct2=vic.columnar_enc(vic.columnar_enc(s,Q),R)
    assert ''.join(ct2[i] for i in V.untranspose_index(n,Q,R,'plain'))==s
print('untranspose_index consistent with vic.py enc/dec')
# 2. planted English
txt=re.sub('[^A-Z]','',open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt').read().upper())
pl,st,k=V.plant(txt[5000:],'FOLLOWTHEWHITERABBIT','1192001',7,'38215')
print(len(pl), pl[:60])
from collections import Counter
print(sorted(Counter(pl).items(),key=lambda x:-x[1]))
body=pl[:113*5-0]  # keygroup at last group (d6=0 -> end0)
kgl=pl[565:570]
print('kg letters',kgl)
a=V.to_idx(pl[:565])
mu,sd=V.null_stats(a,9)
idx=V.untranspose_index(565,k['Q'],k['R'])
print('planted right key z=',(V.hcond_arr(a[idx],9)-mu)/sd, ' transposed z=',(V.hcond_arr(a,9)-mu)/sd)
k2=vic.derive('FOLLOWTHEWHITERABBIT','1192001',8,'38215')
idx2=V.untranspose_index(565,k2['Q'],k2['R'])
print('wrong pnum z=',(V.hcond_arr(a[idx2],9)-mu)/sd)
# faed itself
from common import FAED
fa=V.to_idx(FAED[:565]); m2,s2=V.null_stats(fa,9)
print('faed raw z', (V.hcond_arr(fa,9)-m2)/s2)
t=time.time()
for i in range(2000):
    idx=V.untranspose_index(565,tuple(rnd.randrange(10) for _ in range(rnd.randint(8,29))),tuple(rnd.randrange(10) for _ in range(rnd.randint(8,29))))
    V.hcond_arr(a[idx],9)
print('per derivation ms', (time.time()-t)/2000*1000)
