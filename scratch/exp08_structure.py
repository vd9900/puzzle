from common import *
import math, random
from collections import Counter
f=letters_to_digits(FAED)
n=len(f)
def chi2_cols(s, w):
    # chi-square of digit distribution per column vs overall
    cols=[s[i::w] for i in range(w)]
    tot=Counter(s); N=len(s)
    chi=0; df=0
    for c in cols:
        m=len(c); cc=Counter(c)
        for dg in '123456789':
            e=tot[dg]*m/N
            if e>0: chi+=(cc[dg]-e)**2/e
        df+=8
    return chi, df
def z_from_chi(chi,df): return (chi-df)/math.sqrt(2*df)
print('column non-uniformity by width (z):')
res=[]
for w in range(2,41):
    chi,df=chi2_cols(f,w); res.append((z_from_chi(chi,df),w))
for z,w in sorted(res,reverse=True)[:8]: print(f'  w={w:3d} z={z:.2f}')
# compare against shuffled baseline max over widths
r=random.Random(0); l=list(f); mx=[]
for _ in range(200):
    r.shuffle(l); s=''.join(l)
    mx.append(max(z_from_chi(*chi2_cols(s,w)) for w in range(2,41)))
mx.sort(); print('shuffled max-z over widths: median',round(mx[100],2),'95%',round(mx[190],2),'99%',round(mx[198],2))
# windowed distributions
print('\nwindowed digit counts (windows of 95):')
for i in range(0,570,95):
    c=Counter(f[i:i+95]); print(f'  {i:3d}-{i+94:3d}', ' '.join(f'{dg}:{c[dg]:2d}' for dg in '123456789'))
print('\nwindows of 57:')
for i in range(0,570,57):
    c=Counter(f[i:i+57]); print(f'  {i:3d}-{i+56:3d}', ' '.join(f'{dg}:{c[dg]:2d}' for dg in '123456789'))
# half-split chi-square scan: where is the best split?
best=[]
for k in range(100,470,5):
    a=Counter(f[:k]); b=Counter(f[k:])
    chi=0
    for dg in '123456789':
        ea=(a[dg]+b[dg])*k/570; eb=(a[dg]+b[dg])*(570-k)/570
        chi+=(a[dg]-ea)**2/ea+(b[dg]-eb)**2/eb
    best.append((chi,k))
best.sort(reverse=True); print('\nbest split points (chi2, k):',best[:6])
# pair structure at lag 285
pairs=Counter((f[k],f[k+285]) for k in range(285))
sums=Counter((int(f[k])+int(f[k+285])) for k in range(285))
print('\nlag-285 pair sum distribution:',sorted(sums.items()))
diff=Counter((int(f[k])-int(f[k+285]))%9 for k in range(285)); print('lag-285 diff mod9:',sorted(diff.items()))
# digram counts vs expected
dg=Counter(zip(f,f[1:])); tot=Counter(f)
dev=[]
for (a,b),c in dg.items():
    e=tot[a]*tot[b]/569; dev.append(((c-e)/math.sqrt(e),a+b,c,round(e,1)))
dev.sort(); print('\nmost under-represented digrams:',dev[:6]); print('most over-represented:',dev[-6:])
# repeated n-grams
for L in (4,5,6):
    c=Counter(f[i:i+L] for i in range(570-L+1)); rep={k:v for k,v in c.items() if v>1}
    print(f'{L}-grams repeated: {len(rep)}', sorted(rep.items(), key=lambda x:-x[1])[:8])
