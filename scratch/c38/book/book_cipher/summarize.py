import json, random
R=json.load(open('results.json'))
n=len(R); print('tests',n,'Bonferroni alpha',0.05/n,'min attainable p',1/201)
print('p_q<=0.005:',sum(r['p_q']<=0.005 for r in R),'expected under null ~',round(n*0.005,1))
print('p_q<=0.05:',sum(r['p_q']<=0.05 for r in R),'expected ~',round(n*0.05,1))
print('p_valid<=0.05 (nontrivial):',sum(r['p_valid']<=0.05 for r in R),'expected ~',round(n*0.05,1))
nt=[r for r in R if r['cvalid']<0.95]
b=max(nt,key=lambda r:r['valid']); print('max validity among readings where controls <0.95:',b['src'],b['kind'],b['sizes'],b['mode'],b['valid'],'ctrl',b['cvalid'])
for s in sorted(set(r['src'] for r in R)):
    rr=[r for r in R if r['src']==s]; print(s,len(rr),'min p_q',min(r['p_q'] for r in rr),'max zq(nondegenerate)',max(r['zq'] for r in rr if r['zq']<100))
# zero-digit argument: digit '0' share in fixed-width (page,word) encodings of random valid tuples
M=json.load(open('model.json')); import re
PW={m['pdf']-4:[w for l in m['lines'] for w in l if re.sub('[^a-zA-Z]','',w)] for m in M if 1<=m['pdf']-4<=137}
rng=random.Random(1); pages=[p for p in PW if PW[p]]
for a,b2 in [(3,3),(3,2),(2,2),(3,1)]:
    ds=''
    for _ in range(5000):
        p=rng.choice(pages); w=rng.randrange(1,min(len(PW[p]),10**b2-1)+1)
        if p>=10**a: continue
        ds+=str(p).zfill(a)+str(w).zfill(b2)
    z=ds.count('0')/len(ds); print(f'pw({a},{b2}) zero share {z:.3f}; P(0 zeros in 570 digits) ~ {(1-z)**570:.1e}')
