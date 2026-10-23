"""Critic quick check: is a g-resolved faed/dbbi/R60 prefix the decimal expansion of n^(1/r) (r=2,3,4,5) for ANY integer n?
x = first m letters (a..i=1..9, g in {0,7}) with integer-part length L. n = round(x^r); verify n^(1/r) against ALL letters.
Plant control: digits of sqrt(1234567) and cbrt(98765432109) g-encoded (0,7 -> g)."""
import sys, itertools
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
from math import isqrt
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def iroot(N,r):
    if N<2: return N
    x=1<<((N.bit_length()+r-1)//r)
    while True:
        y=((r-1)*x+N//x**(r-1))//r
        if y>=x: return x
        x=y
def enc(digs): return ''.join('g' if d in '07' else chr(96+int(d)) for d in digs)
def matches(s, digs): return all((c=='g' and d in '07') or (c!='g' and d==str(ord(c)-96)) for c,d in zip(s,digs))
def check(s, m=40, rs=(2,3,4,5), Ls=range(0,16)):
    gi=[i for i,c in enumerate(s[:m]) if c=='g']
    hits=[]
    for bits in itertools.product('07', repeat=len(gi)):
        d=[str(ord(c)-96) if c!='g' else None for c in s[:m]]
        for i,b in zip(gi,bits): d[i]=b
        D=int(''.join(d))
        for L in Ls:
            fr=m-L
            if fr<10: continue
            for r in rs:
                # x = D/10^fr ; n = round(x^r)
                num=D**r; den=10**(fr*r)
                n=(num+den//2)//den
                if n<2: continue
                # full verification: digits of n^(1/r) to len(s) digits total
                tot=len(s)
                root=iroot(n*10**((tot-L)*r), r)
                rd=str(root)
                if len(rd)!=tot: continue
                if matches(s, rd):
                    hits.append((r,L,n))
    return hits
# plant controls
p1=str(isqrt(1234567*10**(2*95)))      # sqrt(1234567) to ~99 digits, L=4
p2=str(iroot(98765432109*10**(3*96),3)) # cbrt, L=4
for nm,p in (('sqrt1234567',p1),('cbrt98765432109',p2)):
    s=enc(p[:100]); h=check(s,m=40)
    print('control',nm,'hits',h[:3]); assert h, 'control failed'
for nm,s in (('faed',FAED),('faed_rev',FAED[::-1]),('dbbi',DBBI),('dbbi_rev',DBBI[::-1]),('R60',R60),('R60rev',R60[::-1])):
    print(nm, 'g in first 40:', s[:40].count('g'), 'hits', check(s,m=40), flush=True)
