import itertools, random
dbbi=open('/home/vin/bitcoin_puzzle/research/artifacts/cycle02/salphaseion-dbbi.txt').read().strip()
def parse(s,P):
    t=[];i=0
    while i<len(s):
        if s[i] in P:
            if i+1>=len(s): return None
            t.append(s[i:i+2]); i+=2
        else: t.append(s[i]); i+=1
    return t
hits=[]
for k in (1,2,3):
    for P in itertools.combinations('abcdefghi',k):
        t=parse(dbbi,P)
        if t and len(t)==64 and len(set(t))==16: hits.append(''.join(P))
print('prefix sets giving 64 tokens/16 symbols:', hits)
# control: shuffled dbbi (same letter counts), fraction where ANY 1-3 prefix set gives 64/16
random.seed(1); n=0; N=2000
for _ in range(N):
    s=''.join(random.sample(dbbi,len(dbbi)))
    ok=False
    for k in (1,2,3):
        for P in itertools.combinations('abcdefghi',k):
            t=parse(s,P)
            if t and len(t)==64 and len(set(t))==16: ok=True;break
        if ok: break
    n+=ok
print('shuffled-control rate (any prefix set):', n/N)
