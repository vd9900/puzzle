# Test 0b: which plaintext types under a VIC checkerboard (AT ONE SIR, S random) give a letter profile consistent with faed?
# Statistic: optimistic-merge L1 between sorted 9-letter profile and faed's; consistency threshold = 95th pct of
# L1 for i.i.d. samples from faed's own unigram (=60, computed in t0_unigram.py).
import sys, re, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch/c37/vic_cipher'); sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
import vic, numpy as np
from collections import Counter
from common import FAED
txt=re.sub('[^A-Z]','',open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt').read().upper())
bip=[w.strip().upper() for w in open('/home/vin/.venvs/open-crypto-puzzles/lib/python3.12/site-packages/mnemonic/wordlist/english.txt')]
obs=sorted(Counter(FAED).values(),reverse=True)
rnd=random.Random(7)
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def numblock(ds, enc):  # VIC number mode: '/' then each digit tripled, then '/'
    return enc['/'] + ''.join(d*3 for d in ds) + enc['/']
def gen(kind, enc, n=565):
    st=''
    if kind=='english':
        i=rnd.randrange(len(txt)-3000)
        while len(st)<n:
            st+=enc[txt[i]]; i+=1
    elif kind=='bip39':
        while len(st)<n:
            st+=''.join(enc[c] for c in rnd.choice(bip))
    elif kind=='decimal_numbermode':
        while len(st)<n: st+=numblock(''.join(rnd.choice('0123456789') for _ in range(20)),enc)
    elif kind=='hex_mixed':   # hex string: digits in number mode runs, letters A-F as letters
        while len(st)<n:
            h=''.join(rnd.choice('0123456789ABCDEF') for _ in range(64))
            for run in re.findall('[0-9]+|[A-F]+',h):
                st+= numblock(run,enc) if run[0].isdigit() else ''.join(enc[c] for c in run)
    elif kind=='hex_digits_plain':  # hex where digits encoded as plain digit chars (no tripling, digit = own code '/'-less)
        while len(st)<n:
            h=''.join(rnd.choice('0123456789ABCDEF') for _ in range(64))
            for c in h: st+= c if c.isdigit() else enc[c]
    elif kind=='english_plus_key':   # English text plus one 77-digit decimal key in number mode
        k=''.join(rnd.choice('0123456789') for _ in range(77)); st=numblock(k,enc)
        i=rnd.randrange(len(txt)-3000)
        while len(st)<n: st+=enc[txt[i]]; i+=1
    elif kind=='random_letters':
        while len(st)<n: st+=enc[rnd.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')]
    return st[:n]
def profile(st, m):
    c=Counter(st); v={d:c.get(d,0) for d in '123456789'}; v[m]+=c.get('0',0)
    return sorted(v.values(),reverse=True)
def L1(p): return sum(abs(a-b) for a,b in zip(p,obs))
for kind in ['english','bip39','english_plus_key','hex_mixed','hex_digits_plain','decimal_numbermode','random_letters']:
    best=[]; mx=[]
    for t in range(1500):
        S=list(range(10)); rnd.shuffle(S); enc,dec,esc=vic.vic_board(S)
        st=gen(kind,enc)
        ps=[profile(st,m) for m in '123456789']
        best.append(min(L1(p) for p in ps)); mx.append(min(p[0] for p in ps))
    best=np.array(best); mx=np.array(mx)
    print('%-20s optimistic L1 median %5.0f  P(L1<=60)=%.4f  min-max-letter median %4.0f P(<=107)=%.3f'%(kind,np.median(best),(best<=60).mean(),np.median(mx),(mx<=107).mean()))
