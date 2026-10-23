"""Critic feasibility check for idea 'faed = per-word a1z26 sums of a (Matrix) text, mod 10 with 0,7->g / digital root / length'.
If any English dialogue text produced faed, faed's letter distribution must match that text's per-word letter distribution.
Compare faed's 9-letter histogram with the per-word distribution of several English texts (chi-square, 8 dof), and with
the per-window distribution (570-word windows) to get an empirical null of how far a real text's 570-word window can drift."""
import sys, re, random, math
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED
from collections import Counter
B='/home/vin/bitcoin_puzzle'
texts={'speech':open(B+'/research/artifacts/phase32-beaufort.txt',errors='replace').read(),
       'carroll':open(B+'/scratch/corpora/carroll_public_domain.txt',errors='replace').read(),
       'chat':open(B+'/scratch/corpora/chat_substantive.txt',errors='replace').read()[:3_000_000],
       'imsdb_matrix':open(B+'/scratch/c43/ideas_transcript_specialist/dl_transcripts/r_a9ae3fc8.html.txt',errors='replace').read(),
       'imsdb_reloaded':open(B+'/scratch/c43/ideas_transcript_specialist/dl_transcripts/r_5e6350bd.html.txt',errors='replace').read()}
def words(t): return re.findall(r"[a-z]+",t.lower())
S=lambda w: sum(ord(c)-96 for c in w)
enc={'mod10_0g':lambda w:'g' if S(w)%10 in (0,7) else chr(96+S(w)%10),
     'droot':lambda w:chr(96+(S(w)-1)%9+1)}
L='abcdefghi'
fc=Counter(FAED); n=len(FAED)
print('faed', {c:fc[c] for c in L})
def chi(obs,p,n): return sum((obs[c]-n*p[c])**2/(n*p[c]) for c in L if p[c]>0)
for en,f in enc.items():
    for tn,t in texts.items():
        seq=[f(w) for w in words(t)]
        cc=Counter(seq); N=len(seq); p={c:cc[c]/N for c in L}
        x=chi(fc,p,n)
        # empirical: chi of random 570-word contiguous windows of this text vs the text's own distribution
        random.seed(0); ws=[]
        for _ in range(2000):
            i=random.randrange(0,max(1,N-n)); win=Counter(seq[i:i+n]); ws.append(chi(win,p,n))
        ws.sort()
        print(f'{en:9s} {tn:15s} words={N:8d} faed_chi2={x:7.1f}  window-chi2 95%={ws[1899]:.1f} 99.9%={ws[1997]:.1f} max={ws[-1]:.1f}  dist='+' '.join(f'{c}{100*p[c]:.0f}' for c in L))
