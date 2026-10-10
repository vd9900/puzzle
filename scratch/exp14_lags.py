from common import *
from serial import hcond_z
import math, random
from collections import Counter
def mi_lag(s,k):
    pairs=Counter(zip(s,s[k:])); n=len(s)-k
    a=Counter(s[:-k]); b=Counter(s[k:])
    return sum(c/n*math.log2(c*n/(a[x]*b[y])) for (x,y),c in pairs.items())
def mi_z(s,k,trials=300,seed=0):
    r=random.Random(seed); l=list(s); vals=[]
    for _ in range(trials):
        r.shuffle(l); vals.append(mi_lag(''.join(l),k))
    m=sum(vals)/trials; sd=(sum((v-m)**2 for v in vals)/trials)**.5
    return (mi_lag(s,k)-m)/sd
f=letters_to_digits(FAED); d=letters_to_digits(DBBI)
r60=letters_to_digits('difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea')
vic='15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
for name,s in (('faed',f),('dbbi',d),('res60',r60),('vic322',vic)):
    zs=[(k,round(mi_z(s,k),2)) for k in range(1,31)]
    print(name, zs)
# de-interleave faed
print()
for k in range(2,7):
    for j in range(k):
        s=f[j::k]
        print(f'faed stream {j}/{k} len={len(s)} hcond_z={hcond_z(s,trials=100):.2f}  mi1={mi_z(s,1,200):.2f}')
