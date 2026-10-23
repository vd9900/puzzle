"""'matrix sumlist' = 'Your life is the SUM of a REMAINDER...': is faed a list of per-WORD a1z26 sums reduced to one digit
(mod 10 with 0 shown as g [zeroed out], or digital root 1..9) of a text we have? Known-plaintext exact-substring scan,
faed fwd/rev, vs shuffled-faed controls. (c41 scanned per-LETTER digital roots only.)"""
import sys, re, glob, os, json, random
FAED=open('/home/vin/bitcoin_puzzle/scratch/c43/ideas_transcript_specialist/faed.txt').read().strip()

B='/home/vin/bitcoin_puzzle'
files=glob.glob('/home/vin/bitcoin_puzzle/scratch/c43/ideas_transcript_specialist/dl_transcripts/*.txt')
corp={os.path.basename(f):open(f,errors='replace').read().lower() for f in files}
try:
    raise Exception('skip')
except Exception as e: print('no telegram',e)
def words(t): return [w for w in re.findall(r"[a-z]+(?:'[a-z]+)?",t)]
def S(w): return sum(ord(c)-96 for c in w if c.isalpha())
encs={
 'mod10_0g': lambda w: 'g' if S(w)%10 in (0,7) else chr(96+S(w)%10),
 'droot':    lambda w: chr(96+(S(w)-1)%9+1),
 'len':      lambda w: chr(96+len(w)) if 1<=len(w)<=9 else ('g' if len(w)%10 in (0,7) else '?'),
}
def norm(s): return s.replace('g','g')
K=8
def longest(target, seq, ws=None):
    idx={}
    for i in range(len(target)-K+1): idx.setdefault(target[i:i+K],[]).append(i)
    best=(0,None)
    for j in range(len(seq)-K+1):
        for i in idx.get(seq[j:j+K],()):
            L=K
            while i+L<len(target) and j+L<len(seq) and target[i+L]==seq[j+L]: L+=1
            if L>best[0]:
                span=ws[j:j+L]
                if sum(len(w)==1 for w in span)>0.3*L or sum(len(w)>=3 for w in span)<0.4*L: continue
                best=(L,(i,j,' '.join(span[:12])))
    return best
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
tgt={'faed':FAED,'faedrev':FAED[::-1],'R60':R60,'R60rev':R60[::-1]}
random.seed(1)
ctrl={f'shuf{k}':''.join(random.sample(FAED,len(FAED))) for k in range(3)}
for en,fn in encs.items():
    res={}
    for cn,t in corp.items():
        ws=words(t)
        if len(ws)<20: continue
        seq=''.join(fn(w) for w in ws)
        for tn,tg in list(tgt.items())+list(ctrl.items()):
            L,pos=longest(tg,seq,ws)
            if L>res.get(tn,(0,))[0]: res[tn]=(L,cn,pos)
    print(en,res)
