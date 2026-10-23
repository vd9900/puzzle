import sys
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
D=lambda s:[ord(c)-96 for c in s]
for name,s in [('faed',FAED),('dbbi',DBBI),('R60',R60)]:
    d=D(s); best=0
    for x0 in range(10):
        x=[x0]; ok=0
        for f in d:
            nx=f-x[-1]
            if not 0<=nx<=9: break
            x.append(nx); ok+=1
        best=max(best,ok)
    print(name,'longest exact (no-mod) pair-sum inversion run',best,'of',len(d))
