from common import *
from serial import hcond_z, hcond
from textmodel import score as qscore
import exp02_transposition as T
import itertools, sys

f = letters_to_digits(FAED)          # '1'..'9'
d = letters_to_digits(DBBI)
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
RES61=RES60+'e'
r60=letters_to_digits(RES60); r61=letters_to_digits(RES61)
MARK84='00001000110000100110010'; MARK83='00001000110000100110011'
img_rows=[6,10,8,7,6,6,5,4,9,9,7,8,7,9]; img_cols=[8,10,8,10,8,7,3,6,7,5,9,6,6,8]
def colsums(digs,ncol): 
    rows=[digs[i:i+ncol] for i in range(0,len(digs),ncol)]
    return [sum(int(r[c]) for r in rows if c<len(r)) for c in range(ncol)]
def rowsums(digs,ncol):
    return [sum(int(x) for x in digs[i:i+ncol]) for i in range(0,len(digs),ncol)]

keys = {
 'dbbi':[int(x) for x in d], 'res60':[int(x) for x in r60], 'res61':[int(x) for x in r61],
 'mark84':[int(x) for x in MARK84], 'mark83':[int(x) for x in MARK83],
 'img_rows':img_rows,'img_cols':img_cols,'img_rows+cols':img_rows+img_cols,
 'res60_c15':colsums(r60,15),'res60_r15':rowsums(r60,15),'res60_c12':colsums(r60,12),'res60_c10':colsums(r60,10),'res60_c6':colsums(r60,6),'res60_c5':colsums(r60,5),'res60_c4':colsums(r60,4),'res60_c3':colsums(r60,3),'res60_c2':colsums(r60,2),
 'res60_c20':colsums(r60,20),'res60_c30':colsums(r60,30),
 'dbbi_c13':colsums(d,13),'dbbi_c7':colsums(d,7),'dbbi_r13':rowsums(d,13),'dbbi_r7':rowsums(d,7),
 'imgbits':[int(b) for b in ''.join(str(x) for row in MATRIX for x in row)],
 'msl_a1z26':[ord(c)-96 for c in 'matrixsumlist'], 'lw_a1z26':[ord(c)-96 for c in 'lastwordsbeforearchichoice'], 'tp_a1z26':[ord(c)-96 for c in 'thispassword'],
 'lwtp_a1z26':[ord(c)-96 for c in 'lastwordsbeforearchichoicethispassword'],
}
results=[]
def ev(tag, s):
    z=hcond_z(s,trials=60)
    results.append((z,tag,s))
    return z

# 0. baselines
ev('faed',f); ev('faed rev',f[::-1])
# 1. additive keys, periodic, mod 9 (1..9 cyclic) and mod 10, +/- , key over positions
def add_mod(s, key, sign, mod, offset=0):
    out=[]
    for i,ch in enumerate(s):
        k=key[(i+offset)%len(key)]
        v=int(ch)
        if mod==9:
            v=((v-1 + sign*k) % 9)+1
        else:
            v=(v + sign*k) % 10
        out.append(str(v))
    return ''.join(out)
for kn,k in keys.items():
    for sign in (1,-1):
        for mod in (9,10):
            ev(f'add {kn} s{sign} m{mod}', add_mod(f,k,sign,mod))
            ev(f'add {kn} s{sign} m{mod} rev', add_mod(f[::-1],k,sign,mod))
# 2. per-column keys on 38x15 and 15x38 layouts
def col_key(s, ncol, key, sign, mod):
    out=list(s)
    for i in range(len(s)):
        c=i%ncol; k=key[c%len(key)]; v=int(s[i])
        out[i]=str(((v-1+sign*k)%9)+1) if mod==9 else str((v+sign*k)%10)
    return ''.join(out)
for kn in ('res60_c15','res60_r15','img_rows','img_cols','dbbi_c13','dbbi_c7','res60_c4','dbbi_r7','dbbi_r13'):
    k=keys[kn]
    for ncol in (15,38,14,13,7,4,19,30):
        for sign in (1,-1):
            for mod in (9,10):
                ev(f'colkey {kn} ncol{ncol} s{sign} m{mod}', col_key(f,ncol,k,sign,mod))
# 3. transpositions keyed by numeric lists (rank order) and phrases, regular & irregular
def rank_key(nums):
    idx=sorted(range(len(nums)), key=lambda i:(nums[i],i)); order=[0]*len(nums)
    for r,i in enumerate(idx): order[i]=r
    return order
def irregular_coldec(ct, order):
    n=len(order); L=len(ct); rows=L//n; extra=L%n
    lens=[rows+(1 if c<extra else 0) for c in range(n)]
    cols=[None]*n; pos=0
    for r in range(n):
        c=order.index(r); cols[c]=ct[pos:pos+lens[c]]; pos+=lens[c]
    out=[]
    for r in range(rows+1):
        for c in range(n):
            if r<lens[c]: out.append(cols[c][r])
    return ''.join(out)
def irregular_colenc(pt, order):
    n=len(order); L=len(pt); rows=L//n; extra=L%n
    lens=[rows+(1 if c<extra else 0) for c in range(n)]
    cols=[[] for _ in range(n)]
    for i,ch in enumerate(pt): cols[i%n].append(ch)
    out=''
    for r in range(n):
        c=order.index(r); out+=''.join(cols[c])
    return out
phrase_keys={'lw+tp':'lastwordsbeforearchichoicethispassword','tp+lw':'thispasswordlastwordsbeforearchichoice','msl':'matrixsumlist','lw':'lastwordsbeforearchichoice','tp':'thispassword','ybp':'yellowblueprimes','yinyang':'yinyang','enter':'enter','ofh':'ourfirsthintisyourlastcommand','sha256':'shabef'}
orders={}
for kn,ph in phrase_keys.items(): orders['ph:'+kn]=rank_key([ord(c) for c in ph])
for kn in ('res60_c15','res60_r15','img_rows','img_cols','img_rows+cols','dbbi_c13','dbbi_c7','dbbi_r7','dbbi_r13','res60_c4','res60_c12','res60_c10','res60_c6','res60_c5','res60_c20','res60_c30'):
    orders['num:'+kn]=rank_key(keys[kn])
for on,order in orders.items():
    for fn,fun in (('dec',irregular_coldec),('enc',irregular_colenc)):
        ev(f'transp {on} {fn}', fun(f,order)); ev(f'transp {on} {fn} rev', fun(f[::-1],order))
# 4. half/half combos
h1,h2=f[:285],f[285:]
for mod in (9,10):
    for sign in (1,-1):
        ev(f'halves add s{sign} m{mod}', add_mod(h1,[int(x) for x in h2],sign,mod))
ev('interleave halves', ''.join(a+b for a,b in zip(h1,h2)))
ev('h2+h1', h2+h1)
# 5. bifid output as letters
import bifid
ev('BIF letters', bifid.BIF); ev('BIF odd', bifid.BIF[1::2]); ev('BIF even', bifid.BIF[0::2])

results.sort()
print('N candidates', len(results))
for z,tag,s in results[:25]:
    pr=printable_ratio(zmethod_digits(s.lstrip('0') or '0')) if s.isdigit() else -1
    print(f'{z:7.2f}  {tag:50s} zmpr={pr:.2f}  {s[:40]}')
print('...')
for z,tag,s in results[-5:]:
    print(f'{z:7.2f}  {tag}')
