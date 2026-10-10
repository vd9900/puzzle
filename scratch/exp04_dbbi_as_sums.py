# Is dbbi (91 digits) the concatenated list of weighted row/column sums of the 14x14 image under some color weights?
from common import *
from fractions import Fraction
from itertools import permutations
import json
img = json.load(open('/home/vin/bitcoin_puzzle/research/artifacts/reproduce.json')) if False else None
# colors from gsmg.py extract_grid
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle')
from tools.gsmg import extract_grid, SOURCES
g = extract_grid(SOURCES/'gsmg-puzzle.png')
colors = g['colors']
CN = ['black','white','blue','yellow','near_white']
def count_vec(cells):
    v=[0]*5
    for (r,c) in cells: v[CN.index(colors[r][c])]+=1
    return v
rows=[[(r,c) for c in range(14)] for r in range(14)]
cols=[[(r,c) for r in range(14)] for c in range(14)]
target=letters_to_digits(DBBI)

def solve_consistent(cons):
    """cons: list of (vec5, value). Return (consistent, solution or None if underdetermined)."""
    # Gaussian elimination over Fractions
    m=[[Fraction(x) for x in v]+[Fraction(val)] for v,val in cons]
    n=5; r=0; piv=[]
    for c in range(n):
        p=None
        for i in range(r,len(m)):
            if m[i][c]!=0: p=i;break
        if p is None: continue
        m[r],m[p]=m[p],m[r]
        pv=m[r][c]; m[r]=[x/pv for x in m[r]]
        for i in range(len(m)):
            if i!=r and m[i][c]!=0:
                fac=m[i][c]; m[i]=[a-fac*b for a,b in zip(m[i],m[r])]
        piv.append(c); r+=1
    for i in range(r,len(m)):
        if m[i][n]!=0: return False,None
    if r==n:
        sol=[None]*n
        for i,c in enumerate(piv): sol[c]=m[i][n]
        return True,sol
    return True,None

found=[]
def dfs(lines, idx, pos, cons, path):
    if idx==len(lines):
        if pos==len(target):
            ok,sol=solve_consistent(cons)
            if ok: found.append((list(path),sol)); print('FOUND', path, sol)
        return
    if pos>=len(target): return
    for L in range(1,6):
        if pos+L>len(target): break
        s=target[pos:pos+L]
        if s[0]=='0': break
        v=int(s)
        ok,sol=solve_consistent(cons+[(lines[idx],v)])
        if not ok: continue
        if sol is not None:
            if any(x<0 or x.denominator!=1 for x in sol): continue
            # fully determined: verify rest directly
            rest=''.join(str(sum(int(x)*c for x,c in zip(sol,lines[j]))) for j in range(idx+1,len(lines)))
            if target[pos+L:]==rest:
                found.append((list(path)+[v],sol)); print('FOUND', path+[v], sol)
            continue
        dfs(lines, idx+1, pos+L, cons+[(lines[idx],v)], path+[v])

orders={}
R=[count_vec(x) for x in rows]; C=[count_vec(x) for x in cols]
orders['rows+cols']=R+C; orders['cols+rows']=C+R; orders['rows']=R; orders['cols']=C
orders['rows_rev+cols_rev']=R[::-1]+C[::-1]; orders['cols_rev+rows_rev']=C[::-1]+R[::-1]
orders['interleaved']=[x for p in zip(R,C) for x in p]
orders['rows_rev']=R[::-1]; orders['cols_rev']=C[::-1]
for name,lines in orders.items():
    dfs(lines,0,0,[],[])
    print(name,'done; found so far',len(found))
