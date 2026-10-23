# Grandpre (9x9 letter square -> (row,col) digit pairs 1-9; homophonic). Squares from first 81 letters of puzzle texts.
import sys,re
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED
A='/home/vin/bitcoin_puzzle/research/artifacts/'
sp=open(A+'phase32-beaufort.txt').read().split('\n')[0].strip()
cb=open(A+'phase32-checkerboard.txt').read().strip()
srcs={'speech':sp,'speech_rev':sp[::-1],'checkerboard':cb,'speech_end':sp[-81:]}
E='etaoinshrdlu'
for nm,t in srcs.items():
    t=re.sub('[^a-z]','',t.lower())[:81] if nm!='speech_end' else t
    for ph in (0,1):
        d=['abcdefghi'.index(c) for c in FAED[ph:]]
        out=''.join(t[9*d[i]+d[i+1]] for i in range(0,len(d)-1,2))
        cov=sum(out.count(c) for c in E)/len(out)
        print(nm,ph,'%.2f'%cov,out[:70])
