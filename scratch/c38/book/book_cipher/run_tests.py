"""Book-cipher tests on Cosmic Duality (printed page = PDF-4, verified on 72 pages).
Each reading maps a digit stream to book tokens; scored by (a) validity rate (fraction of index tuples in range: a true
book cipher gives ~100%) and (b) readability: mean log10 quadgram (clean Carroll model quad_indep) of output letters.
Controls: 200 shuffles of the same stream (same length, same digit multiset). Report empirical p (>= observed)."""
import sys, json, re, random, itertools, math
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics'); import quad_indep as Q
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch'); from common import DBBI, FAED, Z1, Z2, MATRIX
M=json.load(open('model.json')); IDX=json.load(open('index_entries.json'))
def clean(w): return re.sub('[^a-z]','',w.lower())
PAGES={}   # printed page -> list of lines -> list of clean words (drop empty)
for m in M:
    p=m['pdf']-4
    if p<1: continue
    PAGES[p]=[[c for c in (clean(w) for w in l) if c] for l in m['lines']]
    PAGES[p]=[l for l in PAGES[p] if l]
PW={p:[w for l in L for w in l] for p,L in PAGES.items()}
PL={p:''.join(PW[p]) for p in PAGES}
BOOKW=[w for p in sorted(PW) if p<=137 for w in PW[p]]       # body (pre-credits) words
BOOKL=''.join(BOOKW)
IDXH=[clean(e['head']) for e in IDX[1:]]; IDXH=[h for h in IDXH if h]
IDXW=[c for e in IDX[1:] for c in (clean(w) for w in e['text'].split()) if c]
def qscore(s):
    if len(s)<4: return -9.9
    return sum(Q.LOGP.get(s[i:i+4],Q.FLOOR) for i in range(len(s)-3))/(len(s)-3)
def chunks(d, sizes):
    T=sum(sizes); out=[]
    for i in range(0,len(d)-T+1,T):
        t=[];j=i
        for s in sizes: t.append(int(d[j:j+s])); j+=s
        out.append(t)
    return out
def look(kind, t):
    try:
        if kind=='pw': p,w=t; return PW[p][w-1] if w>=1 else None
        if kind=='plw': p,l,w=t; return PAGES[p][l-1][w-1] if l>=1 and w>=1 else None
        if kind=='pl': p,c=t; return PL[p][c-1] if c>=1 else None
        if kind=='bw': (n,)=t; return BOOKW[n-1] if n>=1 else None
        if kind=='bl': (n,)=t; return BOOKL[n-1] if n>=1 else None
        if kind=='ih': (n,)=t; return IDXH[n-1] if n>=1 else None
        if kind=='iw': (n,)=t; return IDXW[n-1] if n>=1 else None
    except (KeyError,IndexError): return None
def decode(d, kind, sizes, mode):
    toks=[look(kind,t) for t in chunks(d,sizes)]
    n=len(toks); good=[x for x in toks if x]
    if mode=='first': s=''.join(x[0] for x in good)
    elif mode=='word': s=''.join(good)
    else: s=''.join(good)   # letters
    return (len(good)/n if n else 0.0), s, n
READ=[]
for a,b in itertools.product([1,2,3],repeat=2):
    READ+= [('pw',(a,b),'first'),('pw',(a,b),'word'),('pl',(a,b),'letter')]
for a,b,c in itertools.product([1,2,3],repeat=3):
    READ+= [('plw',(a,b,c),'first'),('plw',(a,b,c),'word')]
for k in [1,2,3,4,5]:
    READ+= [('bw',(k,),'first'),('bw',(k,),'word'),('bl',(k,),'letter')]
for k in [1,2,3]:
    READ+= [('ih',(k,),'first'),('ih',(k,),'word'),('iw',(k,),'first'),('iw',(k,),'word')]
def L2D(s): return ''.join('0' if c=='o' else str(ord(c)-96) for c in s)
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
FAEDS='faed'  # placeholder name
P32='15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
rs=[sum(r) for r in MATRIX]; cs=[sum(c) for c in zip(*MATRIX)]
SRC={'dbbi':L2D(DBBI),'res60':L2D(RES60),'faed':L2D(FAED),'Z1':L2D(Z1),'Z2':L2D(Z2),'p32':P32,
     'msum_rc':''.join(map(str,rs+cs)),'msum_cr':''.join(map(str,cs+rs))}
for k,v in SRC.items(): print(k,len(v),v[:40])
assert len(SRC['dbbi'])==91 and len(SRC['res60'])==60 and len(SRC['faed'])==570 and len(P32)==149
NC=200; rng=random.Random(38); rows=[]
for name,d in SRC.items():
    ctrl=[]
    for _ in range(NC):
        x=list(d); rng.shuffle(x); ctrl.append(''.join(x))
    for kind,sizes,mode in READ:
        v,s,n=decode(d,kind,sizes,mode)
        if n<3: continue
        q=qscore(s); cv=[];cq=[]
        for c in ctrl:
            vv,ss,_=decode(c,kind,sizes,mode); cv.append(vv); cq.append(qscore(ss))
        pv=(1+sum(x>=v for x in cv))/(NC+1); pq=(1+sum(x>=q for x in cq))/(NC+1)
        mq=sum(cq)/NC; sd=(sum((x-mq)**2 for x in cq)/NC)**.5 or 1e-9
        rows.append(dict(src=name,kind=kind,sizes=sizes,mode=mode,ntup=n,valid=round(v,3),cvalid=round(sum(cv)/NC,3),p_valid=round(pv,4),
                         q=round(q,3),cq=round(mq,3),zq=round((q-mq)/sd,2),p_q=round(pq,4),out=s[:60]))
json.dump(rows,open('results.json','w'),indent=0)
print('tests',len(rows))
for r in sorted(rows,key=lambda r:min(r['p_q'],r['p_valid']))[:25]: print(r)
