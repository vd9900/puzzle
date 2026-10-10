from common import *
from serial import hcond_z
import itertools, sys
f=letters_to_digits(FAED)
def rank_key(key):
    idx=sorted(range(len(key)), key=lambda i:(key[i],i)); order=[0]*len(key)
    for r,i in enumerate(idx): order[i]=r
    return order
def irregular_coldec(ct, order):
    n=len(order); L=len(ct); rows=L//n; extra=L%n
    lens=[rows+(1 if c<extra else 0) for c in range(n)]
    cols=[None]*n; pos=0
    for r in range(n):
        c=order.index(r); cols[c]=ct[pos:pos+lens[c]]; pos+=lens[c]
    return ''.join(cols[c][r] for r in range(rows+1) for c in range(n) if r<lens[c])
def irregular_colenc(pt, order):
    n=len(order); cols=[[] for _ in range(n)]
    for i,ch in enumerate(pt): cols[i%n].append(ch)
    return ''.join(''.join(cols[order.index(r)]) for r in range(n))
def myszkowski_dec(ct,key):
    # equal letters read row-wise together
    n=len(key); L=len(ct); rows=L//n; extra=L%n
    lens=[rows+(1 if c<extra else 0) for c in range(n)]
    cols=[None]*n; pos=0
    for letter in sorted(set(key)):
        cs=[i for i,k in enumerate(key) if k==letter]
        if len(cs)==1:
            c=cs[0]; cols[c]=list(ct[pos:pos+lens[c]]); pos+=lens[c]
        else:
            tot=sum(lens[c] for c in cs); seg=ct[pos:pos+tot]; pos+=tot
            for c in cs: cols[c]=[]
            i=0
            for r in range(rows+1):
                for c in cs:
                    if r<lens[c]: cols[c].append(seg[i]); i+=1
    return ''.join(cols[c][r] for r in range(rows+1) for c in range(n) if r<lens[c])
keywords=['matrixsumlist','lastwordsbeforearchichoice','thispassword','lastwordsbeforearchichoicethispassword','yinyang','yingyang','cosmicduality','salphaseion','gsmgpuzzle','theseedisplanted','followthewhiterabbit','thematrixhasyou','causality','jacquefresco','heisenberg','architect','thearchitect','neo','trinity','morpheus','zion','salvation','enter','shabef','sha256','ourfirsthintisyourlastcommand','anstoo','answer','halfandbetterhalf','betterhalf','primes','prime','yellowblueprimes','yellow','blue','matrix','sumlist','sum','list','gsmg','bitcoin','btcseed','whiterabbit','rabbit','hushhush','infrared','purplepill','theory','everything','theoryofeverything','warning','thewarning','logic','redrose','blackrose','dbbi','faed','abba','key','privatekey','password','choice','door','source','oracle','keymaker','merovingian','smith','agentsmith','wewont','hope','cheshirecat','alice','wonderland','venusproject','lookingforward']
res=[]
def ev(t,s): res.append((hcond_z(s,trials=40),t))
for kw in keywords:
    order=rank_key(kw)
    for lab,fn in (('idec',irregular_coldec),('ienc',irregular_colenc)):
        s=fn(f,order); ev(f'{kw} {lab}',s); ev(f'{kw} {lab} rev',s[::-1])
    ev(f'{kw} mysz',myszkowski_dec(f,kw))
    # short additive key (a1z26 values) at all offsets, mod 9 and 10
    k=[ord(c)-96 for c in kw]
    for off in range(len(k)):
        for sign in (1,-1):
            for mod in (9,10):
                s=''.join(str(((int(ch)-1+sign*k[(i+off)%len(k)])%9)+1) if mod==9 else str((int(ch)+sign*k[(i+off)%len(k)])%10) for i,ch in enumerate(f))
                ev(f'{kw} add off{off} s{sign} m{mod}',s)
print('single pass done',len(res),file=sys.stderr)
# double columnar with the main keywords
main=['matrixsumlist','lastwordsbeforearchichoice','thispassword','yinyang','cosmicduality','salphaseion','lastwordsbeforearchichoicethispassword']
for a,b in itertools.product(main,main):
    s=irregular_coldec(irregular_coldec(f,rank_key(a)),rank_key(b)); ev(f'double dec {a}>{b}',s)
    s=irregular_colenc(irregular_colenc(f,rank_key(a)),rank_key(b)); ev(f'double enc {a}>{b}',s)
res.sort(); print('N',len(res))
for z,t in res[:15]: print(round(z,2),t)
print('tail',[(round(z,2),t) for z,t in res[-3:]])
