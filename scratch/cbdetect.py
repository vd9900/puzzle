from common import *
import random, itertools, math
from collections import Counter

def tokenize(digs, esc):
    toks=[]; i=0; n=len(digs)
    while i<n:
        if digs[i] in esc:
            if i+1<n: toks.append(digs[i:i+2]); i+=2
            else: toks.append(digs[i]); i+=1
        else: toks.append(digs[i]); i+=1
    return toks

def ioc(toks):
    c=Counter(toks); n=len(toks)
    if n<2: return 0
    return sum(v*(v-1) for v in c.values())/(n*(n-1))

def cb_score(digs, esc):
    toks=tokenize(digs,esc)
    return ioc(toks), len(toks), len(set(toks))

def all_escape_pairs(alphabet='0123456789'):
    return list(itertools.combinations(alphabet,2))

def best_cb(digs, pairs=None):
    pairs = pairs or all_escape_pairs(''.join(sorted(set(digs))))
    res=[]
    for e in pairs:
        s,n,k=cb_score(digs,e)
        res.append((s,e,n,k))
    res.sort(reverse=True)
    return res

def shuffled_baseline(digs, esc, trials=200, seed=1):
    r=random.Random(seed); l=list(digs); vals=[]
    for _ in range(trials):
        r.shuffle(l); vals.append(cb_score(''.join(l),esc)[0])
    m=sum(vals)/len(vals); sd=(sum((v-m)**2 for v in vals)/len(vals))**.5
    return m,sd

if __name__=='__main__':
    vic='15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
    print('3.2.2 stream, true escapes (1,4):', cb_score(vic,('1','4')))
    print('3.2.2 ranking:', best_cb(vic)[:5])
    m,sd=shuffled_baseline(vic,('1','4')); print('shuffled baseline', m, sd, 'z=', (cb_score(vic,("1","4"))[0]-m)/sd)
    f=letters_to_digits(FAED); d=letters_to_digits(DBBI)
    print('faed ranking:', best_cb(f)[:5])
    for e in [('7','9'),('5','7'),('5','9')]:
        m,sd=shuffled_baseline(f,e); s=cb_score(f,e)[0]; print(' faed',e,'ioc',round(s,4),'z',round((s-m)/sd,2))
    print('dbbi ranking:', best_cb(d)[:5])
    for e in [('2','5')]:
        m,sd=shuffled_baseline(d,e); s=cb_score(d,e)[0]; print(' dbbi',e,'ioc',round(s,4),'z',round((s-m)/sd,2))
