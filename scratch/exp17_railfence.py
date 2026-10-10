from common import *
from serial import hcond_z
f=letters_to_digits(FAED)
def rail_pattern(n,k,offset=0):
    # zigzag rail index for each position
    if k==1: return [0]*n
    period=2*(k-1); out=[]
    for i in range(n):
        p=(i+offset)%period
        out.append(p if p<k else period-p)
    return out
def rail_encrypt(s,k,off=0):
    pat=rail_pattern(len(s),k,off)
    return ''.join(s[i] for r in range(k) for i in range(len(s)) if pat[i]==r)
def rail_decrypt(s,k,off=0):
    pat=rail_pattern(len(s),k,off); n=len(s)
    order=[i for r in range(k) for i in range(n) if pat[i]==r]
    out=[None]*n
    for ch,i in zip(s,order): out[i]=ch
    return ''.join(out)
res=[]
for k in range(2,61):
    for off in range(0,2*(k-1)):
        for lab,fn in (('dec',rail_decrypt),('enc',rail_encrypt)):
            s=fn(f,k,off); res.append((hcond_z(s,trials=40),f'rail k={k} off={off} {lab}'))
res.sort(); print('N',len(res))
for z,t in res[:10]: print(round(z,2),t)
print('tail',[(round(z,2),t) for z,t in res[-3:]])
