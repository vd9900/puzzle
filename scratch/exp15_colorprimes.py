from common import *
import itertools, sys, time
sys.path.insert(0,'/home/vin/bitcoin_puzzle')
from tools.gsmg import extract_grid, SOURCES
g=extract_grid(SOURCES/'gsmg-puzzle.png'); colors=g['colors']
CN=['black','white','blue','yellow','near_white']
rows=[[CN.index(colors[r][c]) for c in range(14)] for r in range(14)]
cols=[[rows[r][c] for r in range(14)] for c in range(14)]
d1=[rows[i][i] for i in range(14)]; d2=[rows[i][13-i] for i in range(14)]
speech=open('speech32_words.txt').read().split()
primes=[2,3,5,7,11,13,17,19,23,29,31]
W_black=[0,1,2,3,5,7,11,13]; W_white=[0,1,2,3,5]; W_col=[0,1]+primes
# fast AES padding oracle: decrypt last block only needs key, prev ct block
from Crypto.Cipher import AES
def fast_hits(pw):
    out=[]
    for name,(salt,ct) in BLOBS.items():
        for dg in ('sha256','md5'):
            k,iv=evp(pw,salt,dg)
            prev=ct[-32:-16] if len(ct)>16 else iv
            last=AES.new(k,AES.MODE_ECB).decrypt(ct[-16:])
            pt=bytes(a^b for a,b in zip(last,prev))
            pad=pt[-1]
            if 1<=pad<=16 and pt.endswith(bytes([pad])*pad):
                out.append((name,dg))
    return out
def fmt_list(L):
    yield ''.join(map(str,L))
    yield ','.join(map(str,L))
    yield ' '.join(map(str,L))
    yield '[%s]'%', '.join(map(str,L))
    yield '-'.join(map(str,L))
n=0; t0=time.time(); hits=[]
def check(desc,s):
    global n
    for form,pw in (('raw',s),('sha',sha256hex(s))):
        n+=1
        h=fast_hits(pw.encode())
        if h:
            # verify full decrypt
            for bn,dg,pt in try_pw(pw):
                pr=printable_ratio(pt)
                hits.append((desc,form,bn,dg,pr,pt[:40]))
                if pr>0.8: print('!!! STRUCTURED', desc, form, bn, dg, pt[:80], flush=True)
seen=set()
for wb,ww,wB,wY in itertools.product(W_black,W_white,W_col,W_col):
    for wN in {ww,0,1} if True else [ww]:
        w=[wb,ww,wB,wY,wN]
        rs=[sum(w[c] for c in r) for r in rows]; cs=[sum(w[c] for c in col) for col in cols]
        ds=[sum(w[c] for c in d1)]+[sum(w[c] for c in d2)]
        lists={'r':rs,'c':cs,'rc':rs+cs,'cr':cs+rs,'rcd':rs+cs+ds,'total':[sum(rs)],'rsum,csum':[sum(rs),sum(cs)]}
        for ln,L in lists.items():
            for s in fmt_list(L):
                if s in seen: continue
                seen.add(s); check(f'w={w} {ln}',s)
            # word selection from speech (1-based and 0-based)
            if ln in ('r','c','rc'):
                for base in (0,1):
                    ws=[speech[(x-base)%len(speech)] for x in L]
                    s=''.join(ws).lower()
                    if s not in seen: seen.add(s); check(f'w={w} {ln} words b{base}',s)
                    s2=''.join(ws)
                    if s2 not in seen: seen.add(s2); check(f'w={w} {ln} WORDS b{base}',s2)
print('tried',n,'password forms in',round(time.time()-t0),'s; padding hits',len(hits))
for h in hits[:20]: print(h)
