from common import *
from serial import hcond_z
import re, pathlib
f=letters_to_digits(FAED); d=letters_to_digits(DBBI)
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
speech=open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().strip()
cb='15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
keys={
 'dbbi':[int(x) for x in d], 'res60':[int(x) for x in letters_to_digits(RES60)], 'res61':[int(x) for x in letters_to_digits(RES60+'e')],
 'speech_a1z26':[ord(c)-96 for c in speech], 'speech_a0z25':[ord(c)-97 for c in speech],
 'cb_digits':[int(x) for x in cb],
 'matrix_bits':[b for row in MATRIX for b in row],
 'faed_rev':[int(x) for x in f[::-1]],
 'url_a1z26':[ord(c)-96 for c in 'gsmgiotheseedisplanted'],
}
def add_mod(s, key, sign, mod, offset):
    out=[]
    L=len(key)
    for i,ch in enumerate(s):
        k=key[(i+offset)%L]; v=int(ch)
        out.append(str(((v-1+sign*k)%9)+1) if mod==9 else str((v+sign*k)%10))
    return ''.join(out)
def beaufort(s,key,offset):
    # key - text
    out=[]; L=len(key)
    for i,ch in enumerate(s):
        k=key[(i+offset)%L]; v=int(ch); out.append(str(((k-v)%9)+1))
    return ''.join(out)
results=[]
for kn,k in keys.items():
    L=len(k)
    offs=range(L) if L<=600 else range(0,L,1)
    for off in offs:
        for sign in (1,-1):
            for mod in (9,10):
                results.append((hcond_z(add_mod(f,k,sign,mod,off),trials=30),f'{kn} off{off} s{sign} m{mod}'))
        results.append((hcond_z(beaufort(f,k,off),trials=30),f'{kn} off{off} beaufort'))
    print(kn,'done',len(results),flush=True)
results.sort()
print('N',len(results)); 
for z,t in results[:15]: print(round(z,2),t)
print('worst',results[-3:])
