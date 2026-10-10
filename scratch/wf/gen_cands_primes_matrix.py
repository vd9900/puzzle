#!/usr/bin/env python3
"""Lens primes_matrix: numeric-hint derivations (primes x 14x14 grid, sum lists, a1z26-minus-primes,
21/1812-bit framings, prime-position zeroing of texts/hashes). Writes cands + doors files."""
import sys, re, hashlib, json, itertools
sys.path.insert(0,'/home/vin/bitcoin_puzzle'); sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
from tools.gsmg import extract_grid, SOURCES, spiral_coordinates, PHASE3_PREIMAGE, CURVE_ORDER
g=extract_grid(SOURCES/'gsmg-puzzle.png'); COL=g['colors']; M=MATRIX
PR=primes_upto(5000); PS=set(PR)
OUT=[]; DOORS=[]; NOTES=[]
def add(tag,s):
    s=str(s)
    if s and len(s)<=6000: OUT.append((tag,s))
def door(s): DOORS.append(s)
def addnum(tag,s):
    add(tag,s)
    if s.isdigit() and 0<int(s)<CURVE_ORDER: add(tag+' hexkey','%064x'%int(s))
def addbits(tag,b,keys=True):
    add(tag+' bits',b); v=int(b,2); add(tag+' dec',str(v)); add(tag+' hex',hex(v)[2:])
    if keys and len(b)<=256:
        add(tag+' key_rpad','%064x'%(v<<(256-len(b)))); add(tag+' key_lpad','%064x'%v)
    for w in (7,8):
        n=len(b)//w
        if n:
            bs=bytes(int(b[i*w:(i+1)*w],2) for i in range(n))
            if all(32<=x<127 for x in bs):
                add(tag+f' ascii{w}',bs.decode()); NOTES.append(f'PRINTABLE {tag} w{w}: {bs.decode()}')
CI={'black':'k','white':'w','blue':'B','yellow':'Y','near_white':'N'}
# ---------- 1. traversals x prime-indexed cells ----------
sp=spiral_coordinates(14)
ALL=[(r,c) for r in range(14) for c in range(14)]
ORD={'spiral_ccw':sp,'spiral_cw':[(c,r) for r,c in sp],
 'rowmajor':ALL,'colmajor':[(r,c) for c in range(14) for r in range(14)],
 'snake_row':[(r,c if r%2==0 else 13-c) for r in range(14) for c in range(14)],
 'snake_col':[(r if c%2==0 else 13-r,c) for c in range(14) for r in range(14)],
 'antidiag':sorted(ALL,key=lambda rc:(rc[0]+rc[1],rc[0])),'maindiag':sorted(ALL,key=lambda rc:(rc[1]-rc[0],rc[0]))}
for k in list(ORD): ORD[k+'_rev']=ORD[k][::-1]
for oname,order in ORD.items():
    bits=''.join(str(M[r][c]) for r,c in order); cols=''.join(CI[COL[r][c]] for r,c in order)
    addbits(f'{oname} all196',bits)
    cbits=''.join('1' if COL[r][c]=='blue' else '0' for r,c in order if COL[r][c] in ('blue','yellow'))
    add(f'{oname} colourbits24',cbits); add(f'{oname} colourbits24 dec',str(int(cbits,2)))
    add(f'{oname} colourbits24 primesel',''.join(cbits[p-1] for p in PR if p<=24))
    for base in (0,1):
        pidx=[p-base for p in PR if 0<=p-base<196]; pset=set(pidx)
        sel=''.join(bits[i] for i in pidx); addbits(f'{oname} b{base} primesel',sel)
        add(f'{oname} b{base} primesel colours',''.join(cols[i] for i in pidx))
        add(f'{oname} b{base} primesel popcount',str(sel.count('1')))
        zer=''.join('0' if i in pset else bits[i] for i in range(196)); addbits(f'{oname} b{base} primezero',zer)
        one=''.join('1' if i in pset else bits[i] for i in range(196)); addbits(f'{oname} b{base} primeone',one,keys=False)
        dele=''.join(bits[i] for i in range(196) if i not in pset); addbits(f'{oname} b{base} primedel',dele)
        # prime positions among the coloured cells (spiral indices 7,15,..) : indices that are prime
        cp=[i for i,(r,c) in enumerate(order) if COL[r][c] in ('blue','yellow') and (i+base) in PS]
        add(f'{oname} b{base} colouredprimeidx',' '.join(str(i+base) for i in cp))
        add(f'{oname} b{base} colouredprime colours',''.join(cols[i] for i in cp))
    # 21-bit framing
    w21=[int(bits[i:i+21],2) for i in range(0,196-20,21)]
    add(f'{oname} 21bit words',' '.join(map(str,w21))); add(f'{oname} 21bit concat',''.join(map(str,w21)))
    add(f'{oname} 21bit sum',str(sum(w21)))
    w21p=[x for x in w21 if x in PS]
    if w21p: add(f'{oname} 21bit primes',' '.join(map(str,w21p)))
# yellow/blue spiral-index primes (0-based spiral; coloured cells at 7,15,...,191)
ybits='111101110011110110010010'
yidx=[7+8*k for k in range(24)]
bluep=[i for i,b in zip(yidx,ybits) if b=='1' and i in PS]; yelp=[i for i,b in zip(yidx,ybits) if b=='0' and i in PS]
NOTES.append(f'spiral0 blue primes {bluep} sum {sum(bluep)}; yellow primes {yelp} sum {sum(yelp)}')
for lab,L in (('blue',bluep),('yellow',yelp),('yb',yelp+bluep),('by',bluep+yelp)):
    addnum(f'ybprimes {lab} concat',''.join(map(str,L))); add(f'ybprimes {lab} space',' '.join(map(str,L))); add(f'ybprimes {lab} comma',','.join(map(str,L)))
sy,sb=sum(yelp),sum(bluep)
for s in (f'{sy}{sb}',f'{sb}{sy}',f'{sy} {sb}',f'yellow{sy}blue{sb}',f'blue{sb}yellow{sy}',str(sy),str(sb),str(sy+sb),str(sy*sb),f'{sy},{sb}'): addnum('ybprimes sums',s)
# yellow/blue cell coordinates
yc=[(r,c) for r,c in ALL if COL[r][c]=='yellow']; bc=[(r,c) for r,c in ALL if COL[r][c]=='blue']
for base in (0,1):
    for lab,L in (('yellow',yc),('blue',bc)):
        add(f'{lab} coords b{base}',' '.join(f'{r+base},{c+base}' for r,c in L)); add(f'{lab} coords b{base} concat',''.join(f'{r+base}{c+base}' for r,c in L))
        add(f'{lab} rowsum b{base}',str(sum(r+base for r,c in L))); add(f'{lab} colsum b{base}',str(sum(c+base for r,c in L)))
        add(f'{lab} rc sum b{base}',str(sum(r+c+2*base for r,c in L)))
        add(f'{lab} rc prod sum b{base}',str(sum((r+base)*(c+base) for r,c in L)))
# ---------- 2. sum lists with prime filters ----------
def sums(W):
    val=lambda r,c: W[COL[r][c]]
    R=[sum(val(r,c) for c in range(14)) for r in range(14)]; Cc=[sum(val(r,c) for r in range(14)) for c in range(14)]
    D1=[val(i,i) for i in range(14)]; D2=[val(i,13-i) for i in range(14)]
    return R,Cc,D1,D2
def W(k,w,B,Y,N=None): return {'black':k,'white':w,'blue':B,'yellow':Y,'near_white':w if N is None else N}
SCHEMES={'bits':W(1,0,1,0),'inv':W(0,1,0,1),'bits_N1':W(1,0,1,0,1),'BY_a1z26':W(1,0,2,25),'BY_a1z26_only':W(0,0,2,25),'counts':W(1,0,15,9),'counts_only':W(0,0,15,9),'counts_N1':W(0,0,15,9,1),
 'blue1':W(0,0,1,0),'yellow1':W(0,0,0,1),'BY11':W(0,0,1,1),'BY12':W(0,0,1,2),'BY21':W(0,0,2,1),'BY_bits_Y2':W(1,0,1,2),'white1_colours':W(0,1,1,1)}
for B,Y in ((2,3),(3,2),(5,7),(7,5),(2,5),(5,2),(3,5),(5,3),(11,13),(13,11),(2,7),(7,2),(3,7),(7,3),(9,15),(15,9)):
    SCHEMES[f'k1_B{B}_Y{Y}']=W(1,0,B,Y); SCHEMES[f'k0_B{B}_Y{Y}']=W(0,0,B,Y)
def fmts(L):
    yield 'cat',''.join(map(str,L)); yield 'sp',' '.join(map(str,L)); yield 'cm',','.join(map(str,L)); yield 'z2',''.join(f'{x:02d}' for x in L)
def filters(L):
    yield 'id',L
    yield 'primes_only',[x for x in L if x in PS]
    yield 'zero_nonprime',[x if x in PS else 0 for x in L]
    yield 'zero_prime',[0 if x in PS else x for x in L]
    yield 'nonprime_only',[x for x in L if x not in PS]
    yield 'at_prime_idx1',[L[p-1] for p in PR if p<=len(L)]
    yield 'at_prime_idx0',[L[p] for p in PR if p<len(L)]
    yield 'at_prime_idx1_zero_nonprime',[L[p-1] if L[p-1] in PS else 0 for p in PR if p<=len(L)]
    yield 'zero_at_prime_idx1',[0 if (i+1) in PS else x for i,x in enumerate(L)]
    yield 'zero_at_nonprime_idx1',[x if (i+1) in PS else 0 for i,x in enumerate(L)]
    yield 'del_at_prime_idx1',[x for i,x in enumerate(L) if (i+1) not in PS]
    yield 'prime_positions1',[i+1 for i,x in enumerate(L) if x in PS]
    yield 'prime_positions0',[i for i,x in enumerate(L) if x in PS]
for sname,Wt in SCHEMES.items():
    R,Cc,D1,D2=sums(Wt)
    LISTS={'rows':R,'cols':Cc,'rows+cols':R+Cc,'cols+rows':Cc+R,'rows+cols+diags':R+Cc+[sum(D1),sum(D2)],'diag':[sum(D1),sum(D2)]}
    for lname,L in LISTS.items():
        for fname,FL in filters(L):
            if not FL: continue
            for fm,s in fmts(FL): add(f'sum {sname} {lname} {fname} {fm}',s)
            addnum(f'sum {sname} {lname} {fname} total',str(sum(FL)))
            add(f'sum {sname} {lname} {fname} count',str(len(FL)))
# ---------- 3. a1z26 of hint words with primes removed ----------
cb='incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive'
ROAD='yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang'
SALPRE='GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
ADDR='1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'; ADDR2='17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
H='89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32'
LYRIC='theflowerblossomsthroughwhatseemstobeaconcretesurface'
P32='jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple'
WORDS=['matrixsumlist','yellowblueprimes','lastwordsbeforearchichoice','thispassword','yinyang','cosmicduality','salphaseion','theseedisplanted','gsmg','followthewhiterabbit','whiterabbit','rabbit','causality',LYRIC,P32,'ourfirsthintisyourlastcommand','anstoo','halfandbetterhalf','whiterabbitseverywhere',ROAD,'thematrixhasyou','enter','shabef','gsmgiotheseedisplanted','archichoice','lastwords','primes','prime','matrix','sumlist','yellow','blue','theoryofeverything','cosmic','duality','btcseed',cb,'gsmgiobtcpuzzlechallenge','theseedisplantedwhenoppositesattract','yellowblue','blueyellow','matrixsumlistlastwordsbeforearchichoice','lastwordsbeforearchichoiceyinyang','wewontgiveawaythepassword','itsinfrontofyoureyes','verylaststepisatruegiveawaypromised','hundredfourty','fourty','rab','rabbit','bit','rabbits','neo','trinity','morpheus','architect','oracle','merovingian','keymaker','zion','source','salvation','halfanddouble','neighbors']
def a1z26(w,base=1): return [ord(c)-97+base for c in w if c.isalpha()]
for w in WORDS:
    wl=w.lower()
    for base in (1,0):
        V=a1z26(wl,base); letters=[c for c in wl if c.isalpha()]
        tag=f'a1z26 b{base} {wl[:20]}'
        for fm,s in fmts(V): add(f'{tag} plain {fm}',s)
        np_=[v for v in V if v not in PS]; pp=[v for v in V if v in PS]
        for fm,s in fmts(np_): add(f'{tag} primes_removed {fm}',s)
        for fm,s in fmts(pp): add(f'{tag} primes_only {fm}',s)
        for fm,s in fmts([0 if v in PS else v for v in V]): add(f'{tag} primes_zeroed {fm}',s)
        for fm,s in fmts([v if v in PS else 0 for v in V]): add(f'{tag} nonprimes_zeroed {fm}',s)
        add(f'{tag} letters_nonprime',''.join(c for c,v in zip(letters,V) if v not in PS))
        add(f'{tag} letters_prime',''.join(c for c,v in zip(letters,V) if v in PS))
        add(f'{tag} letters_prime_zeroed',''.join('0' if v in PS else c for c,v in zip(letters,V)))
        add(f'{tag} letters_nonprime_zeroed',''.join(c if v in PS else '0' for c,v in zip(letters,V)))
        addnum(f'{tag} sum',str(sum(V))); addnum(f'{tag} sum_primes',str(sum(pp))); addnum(f'{tag} sum_nonprimes',str(sum(np_))); add(f'{tag} count_primes',str(len(pp)))
        # prime letter positions (1-based)
        add(f'{tag} pos_prime_letters',''.join(c for i,c in enumerate(letters) if (i+1) in PS))
        add(f'{tag} pos_nonprime_letters',''.join(c for i,c in enumerate(letters) if (i+1) not in PS))
        add(f'{tag} pos_prime_zeroed',''.join('0' if (i+1) in PS else c for i,c in enumerate(letters)))
        for fm,s in fmts([v for i,v in enumerate(V) if (i+1) in PS]): add(f'{tag} pos_prime_nums {fm}',s)
# ---------- 4. prime-position zeroing of long texts / hashes ----------
spch=open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().strip()
p32full=re.sub(r'[^a-z0-9]','',open('/home/vin/bitcoin_puzzle/research/artifacts/phase32.txt',errors='ignore').read().lower())
words=open('/home/vin/bitcoin_puzzle/scratch/speech32_words.txt').read().split()
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
TEXTS={'speech':spch,'vic':cb,'roadmap':ROAD,'phase3pre':PHASE3_PREIMAGE,'phase32pre':P32,'lyric':LYRIC,'urlhash':H,'salpre':SALPRE,'addr':ADDR,'addr2':ADDR2,'dbbi':DBBI,'faed':FAED,'res60':RES60,'p32full':p32full,'z1':Z1,'z2':Z2,'z3':Z3,'bin1':BIN1,'matrixsumlist':'matrixsumlist','lastwords':'lastwordsbeforearchichoice','titleaddr':SALPRE.lower(),'smallb64':SMALL_B64,'innerb64':INNER_B64}
for tn,t in TEXTS.items():
    for base in (0,1):
        pos=set(p-base for p in PR if 0<=p-base<len(t))
        z=''.join('0' if i in pos else c for i,c in enumerate(t)); d=''.join(c for i,c in enumerate(t) if i not in pos); k=''.join(c for i,c in enumerate(t) if i in pos)
        add(f'{tn} b{base} primezero',z); add(f'{tn} b{base} primedel',d); add(f'{tn} b{base} primekeep',k)
        if tn in ('dbbi','faed','res60'):
            zo=''.join('o' if i in pos else c for i,c in enumerate(t)); add(f'{tn} b{base} prime_o',zo)
            for lab,s in (('zero',z),('o',zo),('del',d),('keep',k)):
                dg=letters_to_digits(s)
                if dg.isdigit():
                    try:
                        bs=zmethod_digits(dg); pr=printable_ratio(bs)
                        if pr>0.7: NOTES.append(f'ZMETHOD {tn} b{base} {lab} printable {pr:.2f} {bs[:60]}')
                        add(f'{tn} b{base} {lab} zmethod hex',bs.hex())
                    except Exception: pass
        if tn in ('urlhash','salpre','addr','titleaddr','matrixsumlist','lastwords','roadmap'):
            door(z); door(d)
        if tn in ('speech','p32full','vic','phase3pre'):
            # a1z26 digit stream with prime-valued letters zeroed
            V=a1z26(t); add(f'{tn} b{base} a1z26 primes_zeroed',''.join('0' if v in PS else str(v) for v in V)); add(f'{tn} b{base} a1z26 primes_removed',''.join(str(v) for v in V if v not in PS))
# speech words at prime indices
for base in (0,1):
    pw=[words[p-base] for p in PR if 0<=p-base<len(words)]; npw=[w for i,w in enumerate(words) if (i+base) not in PS]
    add(f'speechwords b{base} prime joined',''.join(pw).lower()); add(f'speechwords b{base} prime spaced',' '.join(pw).lower())
    add(f'speechwords b{base} nonprime joined',''.join(npw).lower())
    add(f'speechwords b{base} prime initials',''.join(w[0] for w in pw).lower())
    add(f'speechwords b{base} prime zeroed',' '.join('0' if (i+base) in PS else w for i,w in enumerate(words)).lower())
# word lengths at prime positions etc
WL=[len(w) for w in words]
for fname,FL in filters(WL):
    for fm,s in fmts(FL):
        if fm in ('cat','sp'): add(f'speech wordlens {fname} {fm}',s)
# ---------- 5. faed prime positions (104 = len BIN1) ----------
fp1=[FAED[p-1] for p in PR if p<=570]; fp0=[FAED[p] for p in PR if p<570]
add('faed primekeep1',''.join(fp1)); add('faed primekeep0',''.join(fp0))
NOTES.append(f'faed prime-position symbols (1-based) n={len(fp1)}: {"".join(fp1)}')
mask=BIN1.translate(str.maketrans('ab','01'))
for base,fp in ((1,fp1),(0,fp0)):
    pidx=[p-base for p in PR if 0<=p-base<570]
    for mb in ('1','0'):
        zpos=set(i for i,b in zip(pidx,mask) if b==mb)
        for lab,rep in (('zero','0'),('o','o'),('del',None)):
            s=''.join((rep if rep is not None else '') if i in zpos else c for i,c in enumerate(FAED))
            add(f'faed b{base} bin1mask{mb} {lab}',s)
            dg=letters_to_digits(s)
            if dg.isdigit():
                bs=zmethod_digits(dg); pr=printable_ratio(bs)
                if pr>0.6: NOTES.append(f'ZMETHOD faed bin1mask b{base} m{mb} {lab} printable {pr:.2f} {bs[:60]}')
        # the kept symbols only where mask==mb
        kept=''.join(FAED[i] for i,b in zip(pidx,mask) if b==mb); add(f'faed b{base} bin1mask{mb} primekeep',kept)
    # 512 binary maps of the 104 prime-position symbols -> 13 bytes
    found=0
    for m in range(512):
        bits=''.join(str((m>>(ord(c)-97))&1) for c in fp)
        bs=bytes(int(bits[i:i+8],2) for i in range(0,104,8))
        if all(32<=x<127 for x in bs):
            found+=1; NOTES.append(f'FAED104 b{base} map{m:09b} printable: {bs.decode()}'); add(f'faed104 b{base} map{m}',bs.decode())
        # also reversed bit order
        bs2=bytes(int(bits[::-1][i:i+8],2) for i in range(0,104,8))
        if all(32<=x<127 for x in bs2):
            found+=1; NOTES.append(f'FAED104rev b{base} map{m:09b} printable: {bs2.decode()}'); add(f'faed104rev b{base} map{m}',bs2.decode())
    NOTES.append(f'faed104 b{base}: {found} printable maps of 1024')
# dbbi prime positions (24): map test too (b/be tokens known) - digits of dbbi at prime idx
dp1=''.join(DBBI[p-1] for p in PR if p<=91); add('dbbi primekeep1 physical',dp1)
# ---------- 6. rabbit / 21 / 1812 / {1},{4},{21} ----------
for s in ['21bit','1812bit','bit21','bit1812','21bits','1812bits','rabbit21','rabbit1812','21rabbit','1812rabbit','18 1 2','18,1,2','18-1-2','1812','21','r18a1b2','R18A1B2','R=18A=1B=2','rab','RAB','rabbit','RABBIT','RABbit','whiterabbit21','whiterabbit1812','18112','181221','211812','1812 21','21 1812','2118','1821','rabbit bit','rab bit','21 bit','1812 bit','1421','1 4 21','1,4,21','{1},{4},{21}','{1 },{4} ,{21}','1-4-21','14 21','14,21','1 4 21 bit','142','1 4 2 1','124','2 7 73','2773','7 23 31 47 103 127','71 79 151 191','101','43','44','4344','43 44','1012','2 3 5 7 11 13','23571113','0b10101','10101','11100010100','1812bitrabbit','21bitrabbit','rabbit21bit','rabbit1812bit','twentyone','eighteentwelve','eighteenonetwo','eighteen one two','onefourtwentyone','whiterabbits','whiterabbitseverywhere','followthewhiterabbit21','followthewhiterabbit1812','theseedisplanted21','theseedisplanted1812','matrixsumlist21','matrixsumlist1812','primes21','primes1812','1812primes','21primes','hundredfourty','hundredfourtyoftheinvestment','worthhundredfourty','fourty','140','hundred fourty','onehundredfourty','onehundredforty','fefefe','FEFEFE','104','hundredfour','hundred four','fefefe104','0xfefefe','16711422','101010','fefe','fe']:
    addnum('rabbit/numeric',s)
for s in ['1421','1 4 21','1,4,21','{1},{4},{21}','{1 },{4} ,{21}','21bit','1812bit','rabbit21','rabbit1812','21 1812','1812 21','r18a1b2','hundredfourty','fefefe','104','101','75777375','7 5 7 7 7 3 7 5','4 7 11 13 6 7 9 10','47111367910','7577','7375','7577 7375','75777375 47111367910','43 44','4344','338493','493338','7 23 31 47 103 127 71 79 151 191','72331471031277179151191','yellow493blue338','yellowblueprimes21','yellowblueprimes1812']:
    door(s)
# ---------- 7. matrix bits with coloured cells zeroed / coloured-only ----------
for oname in ('spiral_ccw','rowmajor','colmajor','spiral_cw'):
    order=ORD[oname]
    bits=''.join(str(M[r][c]) for r,c in order)
    zc=''.join('0' if COL[r][c] in ('blue','yellow','near_white') else str(M[r][c]) for r,c in order); addbits(f'{oname} colouredzero',zc)
    zk=''.join('0' if COL[r][c]=='black' else str(M[r][c]) for r,c in order); addbits(f'{oname} blackzero',zk,keys=True)
    # prime rows / prime cols only (1-based)
    for base in (0,1):
        pr_=''.join(str(M[r][c]) for r,c in order if (r+base) in PS); pc_=''.join(str(M[r][c]) for r,c in order if (c+base) in PS); prc=''.join(str(M[r][c]) for r,c in order if (r+base) in PS and (c+base) in PS)
        addbits(f'{oname} b{base} primerows',pr_); addbits(f'{oname} b{base} primecols',pc_); addbits(f'{oname} b{base} primerowscols',prc)
        npr=''.join(str(M[r][c]) for r,c in order if (r+base) not in PS and (c+base) not in PS); addbits(f'{oname} b{base} nonprimerowscols',npr)
        zrc=''.join('0' if ((r+base) in PS or (c+base) in PS) else str(M[r][c]) for r,c in order); addbits(f'{oname} b{base} primerowscols_zeroed',zrc)
        zn=''.join(str(M[r][c]) if ((r+base) in PS and (c+base) in PS) else '0' for r,c in order); addbits(f'{oname} b{base} nonprimerowscols_zeroed',zn)
# ---------- 8. raw zero-padded ASCII keys ("Good job Neo" grammar) ----------
for s in ['matrixsumlist','lastwordsbeforearchichoice','thispassword','yellowblueprimes','theseedisplanted','gsmg.io/theseedisplanted','yinyang','cosmicduality','salphaseion','halfandbetterhalf','betterhalf','whiterabbit','followthewhiterabbit','primes','matrixsumlist21','rabbit','enter','anstoo','shabef','btcseed','gsmg.io/salphaseion','gsmg.io/cosmicduality','archichoice','lastwords','causality','thematrixhasyou','THEMATRIXHASYOU','whiterabbitseverywhere','yellowblueprimesmatrix','theproblemischoice','hundredfourty','1812','21','GSMGIO5BTCPUZZLECHALLENGE','gsmgio5btcpuzzlechallenge','cosmic duality','Cosmic Duality','yin yang','half and better half','White Rabbits everywhere','theseedisplanted21','theseedisplanted1812','gsmg.io/theseedisplanted21','gsmg.io/theseedisplanted1812']:
    b=s.encode()
    if len(b)<=32:
        add(f'rawascii lpad {s}',(b'\0'*(32-len(b))+b).hex()); add(f'rawascii rpad {s}',(b+b'\0'*(32-len(b))).hex())
        # prime-position bytes zeroed (1-based)
        zb=bytes(0 if (i+1) in PS else x for i,x in enumerate(b)); add(f'rawascii lpad primezero {s}',(b'\0'*(32-len(b))+zb).hex())
# write
seen=set(); n=0
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_primes_matrix.txt','w') as f:
    f.write('# lens primes_matrix: numeric hints x 14x14 grid / sum lists / a1z26-primes / 21,1812 bits / prime-position zeroing\n')
    for tag,s in OUT:
        if s in seen or '\n' in s: continue
        seen.add(s); f.write(s+'\n'); n+=1
dseen=set(l.strip() for l in open('/home/vin/bitcoin_puzzle/scratch/wf/_doors_seen.txt'))
ds=set(); nd=0
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_primes_matrix_doors.txt','w') as f:
    f.write('# lens primes_matrix door preimages (gsmg.io/<sha256hex(line)>)\n')
    for s in DOORS:
        if s in ds or s in dseen or '\n' in s: continue
        ds.add(s); f.write(s+'\n'); nd+=1
json.dump([(t,s[:100]) for t,s in OUT],open('/home/vin/bitcoin_puzzle/scratch/wf/primes_matrix_tags.json','w'))
print(f'wrote {n} unique candidates ({len(OUT)} tagged), {nd} door preimages')
for x in NOTES: print('NOTE',x)
