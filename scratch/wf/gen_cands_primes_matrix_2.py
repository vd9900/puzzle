#!/usr/bin/env python3
"""primes_matrix pass 2: a1z26 colour numbers from the poem (R=18,W=23,B=2,Y=25), prime sub-matrix sums, {1},{4},{21} index readings."""
import sys, re, json
sys.path.insert(0,'/home/vin/bitcoin_puzzle'); sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
from tools.gsmg import extract_grid, SOURCES, spiral_coordinates, CURVE_ORDER
g=extract_grid(SOURCES/'gsmg-puzzle.png'); COL=g['colors']; M=MATRIX
PR=primes_upto(5000); PS=set(PR); OUT=[]
def add(tag,s):
    s=str(s)
    if s and len(s)<=6000: OUT.append((tag,s))
def addnum(tag,s):
    add(tag,s)
    if s.isdigit() and 0<int(s)<CURVE_ORDER: add(tag+' hexkey','%064x'%int(s))
def W(k,w,B,Y,N=None): return {'black':k,'white':w,'blue':B,'yellow':Y,'near_white':w if N is None else N}
SCH={}
for k in (18,11,2,0,1): 
    for w in (23,0):
        for B,Y in ((2,25),(40,92),(25,2)):
            SCH[f'k{k}_w{w}_B{B}_Y{Y}']=W(k,w,B,Y)
            SCH[f'k{k}_w{w}_B{B}_Y{Y}_N0']=W(k,w,B,Y,0); SCH[f'k{k}_w{w}_B{B}_Y{Y}_N1']=W(k,w,B,Y,1)
def fmts(L):
    yield 'cat',''.join(map(str,L)); yield 'sp',' '.join(map(str,L)); yield 'cm',','.join(map(str,L))
def filters(L):
    yield 'id',L
    yield 'primes_only',[x for x in L if x in PS]
    yield 'zero_nonprime',[x if x in PS else 0 for x in L]
    yield 'zero_prime',[0 if x in PS else x for x in L]
    yield 'nonprime_only',[x for x in L if x not in PS]
    yield 'at_prime_idx1',[L[p-1] for p in PR if p<=len(L)]
    yield 'at_prime_idx0',[L[p] for p in PR if p<len(L)]
    yield 'zero_at_prime_idx1',[0 if (i+1) in PS else x for i,x in enumerate(L)]
    yield 'zero_at_nonprime_idx1',[x if (i+1) in PS else 0 for i,x in enumerate(L)]
    yield 'del_at_prime_idx1',[x for i,x in enumerate(L) if (i+1) not in PS]
    yield 'prime_positions1',[i+1 for i,x in enumerate(L) if x in PS]
    yield 'mod26',[x%26 for x in L]
    yield 'letters',None
sp=spiral_coordinates(14); ALL=[(r,c) for r in range(14) for c in range(14)]
ORD={'spiral_ccw':sp,'rowmajor':ALL,'colmajor':[(r,c) for c in range(14) for r in range(14)]}
for sname,Wt in SCH.items():
    val=lambda r,c: Wt[COL[r][c]]
    R=[sum(val(r,c) for c in range(14)) for r in range(14)]; Cc=[sum(val(r,c) for r in range(14)) for c in range(14)]
    D1=sum(val(i,i) for i in range(14)); D2=sum(val(i,13-i) for i in range(14))
    LISTS={'rows':R,'cols':Cc,'rows+cols':R+Cc,'cols+rows':Cc+R,'rows+cols+diags':R+Cc+[D1,D2]}
    for base in (0,1):
        pr=[r for r in range(14) if (r+base) in PS]
        LISTS[f'subrows_b{base}']=[sum(val(r,c) for c in pr) for r in range(14)]   # row sums over prime cols
        LISTS[f'subcols_b{base}']=[sum(val(r,c) for r in pr) for c in range(14)]
        LISTS[f'submatrix_rows_b{base}']=[sum(val(r,c) for c in pr) for r in pr]
        LISTS[f'submatrix_cols_b{base}']=[sum(val(r,c) for r in pr) for c in pr]
        LISTS[f'submatrix_rc_b{base}']=LISTS[f'submatrix_rows_b{base}']+LISTS[f'submatrix_cols_b{base}']
    for lname,L in LISTS.items():
        for fname,FL in filters(L):
            if fname=='letters':
                s=''.join(chr(96+x) if 1<=x<=26 else '0' for x in L); add(f'p2 {sname} {lname} letters',s)
                s2=''.join(chr(96+x) if x in PS and x<=26 else '0' for x in L); add(f'p2 {sname} {lname} primeletters',s2)
                continue
            if not FL: continue
            for fm,s in fmts(FL): add(f'p2 {sname} {lname} {fname} {fm}',s)
            addnum(f'p2 {sname} {lname} {fname} total',str(sum(FL)))
    # prime-indexed cell values in traversals under this weighting
    for oname,order in ORD.items():
        vals=[val(r,c) for r,c in order]
        for base in (0,1):
            sel=[vals[p-base] for p in PR if 0<=p-base<196]
            add(f'p2 {sname} {oname} b{base} primesel cat',''.join(map(str,sel))); add(f'p2 {sname} {oname} b{base} primesel sp',' '.join(map(str,sel)))
            addnum(f'p2 {sname} {oname} b{base} primesel total',str(sum(sel)))
            nz=[x for x in sel if x]; add(f'p2 {sname} {oname} b{base} primesel nonzero',' '.join(map(str,nz)))
        addnum(f'p2 {sname} {oname} total',str(sum(vals)))
# {1},{4},{21} index readings
words=open('/home/vin/bitcoin_puzzle/scratch/speech32_words.txt').read().split()
lyr='the flower blossoms through what seems to be a concrete surface'.split()
R=[sum(r) for r in M]; Cc=[sum(M[r][c] for r in range(14)) for c in range(14)]
SRC={'speechwords':words,'rows+cols':R+Cc,'cols+rows':Cc+R,'dbbi':list(DBBI),'faed':list(FAED),'spiralbits':[M[r][c] for r,c in sp],'rowbits':[M[r][c] for r,c in ALL],'lyric':lyr,'road':'yellow blue primes matrix sumlist last words before archichoice yinyang'.split(),'primes':PR,'speechletters':list(open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().strip())}
for sn,S in SRC.items():
    for base in (0,1):
        try: pick=[S[i-base] for i in (1,4,21)]
        except IndexError: continue
        add(f'idx1421 {sn} b{base} cat',''.join(map(str,pick))); add(f'idx1421 {sn} b{base} sp',' '.join(map(str,pick)))
        if all(isinstance(x,int) for x in pick): addnum(f'idx1421 {sn} b{base} sum',str(sum(pick)))
seen=set(); n=0
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_primes_matrix_2.txt','w') as f:
    f.write('# lens primes_matrix pass 2: poem a1z26 colour weights (R18/W23/B2/Y25), prime sub-matrix sums, {1},{4},{21} index readings\n')
    for tag,s in OUT:
        if s in seen or '\n' in s: continue
        seen.add(s); f.write(s+'\n'); n+=1
print('wrote',n,'unique of',len(OUT))
