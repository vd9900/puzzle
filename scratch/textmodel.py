import re, math, pickle, os
from collections import Counter
from pathlib import Path
CACHE=Path('/home/vin/bitcoin_puzzle/scratch/quadgrams.pkl')
def build():
    T=Path('/home/vin/bitcoin_puzzle/research/evidence/cycle02/_work__chat_transcript.txt').read_text(errors='ignore')
    R=Path('/home/vin/bitcoin_puzzle/research/sources/community-README.md').read_text(errors='ignore')
    text=(T+R)
    # keep only lines that are mostly ascii letters (drop headers)
    lines=[l for l in text.splitlines() if not l.startswith('=== [') and len(l)>20]
    s=re.sub('[^a-z]','',' '.join(lines).lower())
    q=Counter(s[i:i+4] for i in range(len(s)-3))
    total=sum(q.values())
    logp={k:math.log10(v/total) for k,v in q.items()}
    floor=math.log10(0.01/total)
    pickle.dump((logp,floor),open(CACHE,'wb'))
    return logp,floor
if CACHE.exists(): LOGP,FLOOR=pickle.load(open(CACHE,'rb'))
else: LOGP,FLOOR=build()
def score(t):
    t=re.sub('[^a-z]','',t.lower())
    if len(t)<4: return FLOOR
    return sum(LOGP.get(t[i:i+4],FLOOR) for i in range(len(t)-3))/(len(t)-3)
if __name__=='__main__':
    print(score('yourlifeisthesumofaremainderofanunbalancedequation'))
    print(score('incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalf'))
    print(score('qzxjvkwpqzxjvkwpqzxjvkwpqzxjvkwpqzxjvkwpqzxjvkwpqzxjvkwp'))
    import random; r=random.Random(1); print(score(''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(60))))
    print(score('deoemckeadhbschdkbdcsdkdvbxcpcochcrdicibqeebddbcndsbdcpdgcpdncncsescgddclen'))
