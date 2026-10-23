# Quick feasibility checks (mathematician lens, cycle 42).
# (1) dbbi (91=T(13)) as a Pascal "sum pyramid": entry = neighbour sum/diff mod 9|10 of the row below. 78 constraints, chance ~1/9-1/10 each.
# (2) R60 (60 = Pisano period pi(10)) +/- Fibonacci mod 10 -> 60 digits -> z-method bytes; printable oracle.
import sys, random; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, zmethod_digits
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def vals(s,base): return [ord(c)-97+base for c in s]
def pyramid_score(v,mod,op,inc):
    rows=[];i=0
    lens=list(range(1,14)) if inc else list(range(13,0,-1))
    for L in lens: rows.append(v[i:i+L]); i+=L
    if inc: rows=rows[::-1]           # make rows[0] the 13-long base
    ok=tot=0
    for r in range(1,13):
        for j in range(len(rows[r])):
            a,b=rows[r-1][j],rows[r-1][j+1]
            pred=(a+b)%mod if op=='+' else (a-b)%mod if op=='-' else (b-a)%mod
            ok+= (rows[r][j]%mod)==pred; tot+=1
    return ok/tot
best=[]
for s,name in ((DBBI,'dbbi'),(DBBI[::-1],'dbbi_rev')):
    for base in (0,1):
        for mod in (9,10):
            for op in '+-~':
                for inc in (0,1):
                    best.append((pyramid_score(vals(s,base),mod,op,inc),name,base,mod,op,inc))
best.sort(reverse=True); print('pyramid best',best[:3])
random.seed(1); ctrl=[]
for _ in range(200):
    t=list(DBBI); random.shuffle(t); t=''.join(t)
    ctrl.append(max(pyramid_score(vals(t,b),m,o,i) for b in (0,1) for m in (9,10) for o in '+-~' for i in (0,1)))
print('pyramid control max-of-48 p50/p99', sorted(ctrl)[100], sorted(ctrl)[198])
# (2) Fibonacci keystream
def fib(n,mod,a=0,b=1):
    out=[]
    for _ in range(n): out.append(a%mod); a,b=b,a+b
    return out
res=[]
for start in ((0,1),(1,1),(1,2)):
    for base in (0,1):
        for op in '+-~':
            for mod in (10,9):
                F=fib(60,mod,*start); v=vals(R60,base)
                d=[(x+f)%mod if op=='+' else (x-f)%mod if op=='-' else (f-x)%mod for x,f in zip(v,F)]
                ds=''.join(map(str,d)).lstrip('0') or '0'
                b=zmethod_digits(ds)
                pr=sum(32<=c<127 for c in b)/len(b)
                res.append((pr,start,base,op,mod,b))
res.sort(key=lambda t:-t[0]); print('fib best', res[:3])
