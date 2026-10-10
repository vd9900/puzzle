#!/usr/bin/env python3
"""primes_matrix pass 3: prime-position zeroing of stage sha256 hexes, BIN1 and VIC digit stream; prime-filtered sum lists of dbbi/faed at factor widths."""
import sys, re, hashlib, json
sys.path.insert(0,'/home/vin/bitcoin_puzzle'); sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
from tools.gsmg import PHASE3_PREIMAGE, decode_checkerboard, CURVE_ORDER
PR=primes_upto(5000); PS=set(PR); OUT=[]; NOTES=[]
def add(tag,s):
    s=str(s)
    if s and len(s)<=6000: OUT.append((tag,s))
def zdk(t,base):
    pos=set(p-base for p in PR if 0<=p-base<len(t))
    return (''.join('0' if i in pos else c for i,c in enumerate(t)), ''.join(c for i,c in enumerate(t) if i not in pos), ''.join(c for i,c in enumerate(t) if i in pos))
LYRIC='theflowerblossomsthroughwhatseemstobeaconcretesurface'; P32='jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple'
SALPRE='GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
ANS=['causality',LYRIC,PHASE3_PREIMAGE,P32,SALPRE,'matrixsumlist','lastwordsbeforearchichoice','thispassword','yinyang','cosmicduality','salphaseion','theseedisplanted','gsmg.io/theseedisplanted','yellowblueprimes','ourfirsthintisyourlastcommand','anstoo','enter','halfandbetterhalf','1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe','17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa','whiterabbit','followthewhiterabbit','thematrixhasyou','THEMATRIXHASYOU','primes','rabbit','hashthetext','HASHTHETEXT','btcseed','theoryofeverything','cosmic duality','Cosmic Duality','yin yang','GSMGIO5BTCPUZZLECHALLENGE','gsmg','GSMG','1812','21','hundredfourty','fourty','matrixsumlistlastwordsbeforearchichoiceyinyang','yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang']
for a in ANS:
    h=sha256hex(a)
    for base in (0,1):
        z,d,k=zdk(h,base)
        add(f'sha256 {a[:20]} b{base} primezero',z); add(f'sha256 {a[:20]} b{base} primedel',d); add(f'sha256 {a[:20]} b{base} primekeep',k)
        # zero prime positions as hex digits -> key (64 hex) handled by bw hex-as-key; also prime-positions of the raw digest bytes
        hb=bytes.fromhex(h); zb=bytes(0 if (i+base) in PS else x for i,x in enumerate(hb)); add(f'sha256 {a[:20]} b{base} bytezero',zb.hex())
        db=bytes(x for i,x in enumerate(hb) if (i+base) not in PS); add(f'sha256 {a[:20]} b{base} bytedel',db.hex())
        # digest with prime-valued bytes zeroed
        pv=bytes(0 if x in PS else x for x in hb); add(f'sha256 {a[:20]} primevalue bytezero',pv.hex())
# BIN1 (matrixsumlist binary) zeroing
bits=BIN1.translate(str.maketrans('ab','01'))
for base in (0,1):
    z,d,k=zdk(bits,base)
    for lab,s in (('zero',z),('del',d),('keep',k)):
        add(f'bin1 b{base} {lab}',s)
        n=len(s)//8
        if n:
            bs=bytes(int(s[i*8:(i+1)*8],2) for i in range(n)); add(f'bin1 b{base} {lab} hex',bs.hex())
            if all(32<=x<127 for x in bs): NOTES.append(f'BIN1 {lab} b{base} printable {bs.decode()}'); add(f'bin1 b{base} {lab} ascii',bs.decode())
        add(f'bin1 b{base} {lab} dec',str(int(s,2)))
# VIC digit stream zeroing
vic='15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
try: NOTES.append('VIC control decode: '+decode_checkerboard(vic)[:40])
except Exception as e: NOTES.append('VIC control err '+str(e))
for base in (0,1):
    z,d,k=zdk(vic,base)
    for lab,s in (('zero',z),('del',d),('keep',k)):
        add(f'vic b{base} {lab}',s)
        try:
            t=decode_checkerboard(s); add(f'vic b{base} {lab} decoded',t); NOTES.append(f'VIC {lab} b{base}: {t[:70]}')
        except Exception as e: NOTES.append(f'VIC {lab} b{base}: decode error {e}')
    # zero prime-valued digits (2,3,5,7)
    s=''.join('0' if c in '2357' else c for c in vic); add('vic primedigits zeroed',s)
    try: t=decode_checkerboard(s); add('vic primedigits zeroed decoded',t); NOTES.append('VIC primedigits zeroed: '+t[:70])
    except Exception as e: NOTES.append('VIC primedigits zeroed err '+str(e))
    s=''.join(c for c in vic if c not in '2357'); add('vic primedigits removed',s)
    try: t=decode_checkerboard(s); add('vic primedigits removed decoded',t); NOTES.append('VIC primedigits removed: '+t[:70])
    except Exception as e: NOTES.append('VIC primedigits removed err '+str(e))
# dbbi/faed digit grids at factor widths -> prime filtered sum lists
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def fmts(L):
    yield 'cat',''.join(map(str,L)); yield 'sp',' '.join(map(str,L)); yield 'cm',','.join(map(str,L))
def filters(L):
    yield 'primes_only',[x for x in L if x in PS]
    yield 'zero_nonprime',[x if x in PS else 0 for x in L]
    yield 'zero_prime',[0 if x in PS else x for x in L]
    yield 'at_prime_idx1',[L[p-1] for p in PR if p<=len(L)]
    yield 'prime_positions1',[i+1 for i,x in enumerate(L) if x in PS]
    yield 'mod10',[x%10 for x in L]
    yield 'mod9',[x%9 for x in L]
for tn,t,zero in (('dbbi',DBBI,'o'),('faed',FAED,'o'),('res60',RES60,'o')):
    for a0 in (0,1):
        D=[ord(c)-97+a0 for c in t]
        n=len(D); widths=[w for w in range(2,n) if n%w==0]
        for w in widths:
            rows=[D[i*w:(i+1)*w] for i in range(n//w)]
            R=[sum(r) for r in rows]; C=[sum(rows[i][j] for i in range(n//w)) for j in range(w)]
            for lname,L in (('rows',R),('cols',C),('rows+cols',R+C)):
                for fm,s in fmts(L): add(f'{tn} a{a0} w{w} {lname} {fm}',s)
                for fname,FL in filters(L):
                    if not FL: continue
                    for fm,s in fmts(FL): add(f'{tn} a{a0} w{w} {lname} {fname} {fm}',s)
                    add(f'{tn} a{a0} w{w} {lname} {fname} total',str(sum(FL)))
            # prime-row / prime-col sub sums
            for base in (0,1):
                pr=[i for i in range(n//w) if (i+base) in PS]; pc=[j for j in range(w) if (j+base) in PS]
                add(f'{tn} a{a0} w{w} b{base} primerows sums',' '.join(str(sum(rows[i])) for i in pr))
                add(f'{tn} a{a0} w{w} b{base} primecols sums',' '.join(str(sum(rows[i][j] for i in range(n//w))) for j in pc))
                add(f'{tn} a{a0} w{w} b{base} primerows letters',''.join(t[i*w:(i+1)*w] for i in pr))
                add(f'{tn} a{a0} w{w} b{base} primecols letters',''.join(t[i*w+j] for i in range(n//w) for j in pc))
                add(f'{tn} a{a0} w{w} b{base} primerowcols letters',''.join(t[i*w+j] for i in pr for j in pc))
seen=set(); n=0
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_primes_matrix_3.txt','w') as f:
    f.write('# lens primes_matrix pass 3: prime-zeroed stage sha256 hexes, BIN1/VIC digit zeroing, prime-filtered dbbi/faed grid sums\n')
    for tag,s in OUT:
        if s in seen or '\n' in s: continue
        seen.add(s); f.write(s+'\n'); n+=1
print('wrote',n,'unique of',len(OUT))
for x in NOTES: print('NOTE',x)
