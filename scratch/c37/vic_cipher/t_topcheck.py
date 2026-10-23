# Exact permutation p-values (20k shuffles) for the top-z derivation of faed and of each control (main sweep).
import sys, json; sys.argv=['x']; sys.path.insert(0,'.')
import numpy as np, vic, vicfast as V, cands, run_main as R
M=json.load(open('results/main_results.json')); T=R.make_targets()
PH=dict(cands.usable_phrases()); D=dict(cands.DATES)
for name in ['faed','ctrl0','ctrl1','ctrl2']:
    rec=M['targets'][name]['top_z'][0]
    z,ez,_,ptag,dtag,postag,gi,mp,rd,kgd,pn,mode=rec[:12]
    s=T[name]; body=s[:5*gi]+s[5*gi+5:]; a=V.to_idx(body)
    k=vic.derive(PH[ptag],D[dtag],pn,kgd); u=a[V.untranspose_index(565,tuple(k['Q']),tuple(k['R']),mode)]
    h=V.hcond_arr(u,9); r=np.random.default_rng(99); b=a.copy(); vals=np.empty(20000)
    for i in range(20000): r.shuffle(b); vals[i]=V.hcond_arr(b,9)
    p=(vals<=h).mean(); zz=(h-vals.mean())/vals.std()
    print(name, ptag, dtag, pn, kgd, mode, 'stored z %.2f  recomputed z(20k) %.2f  perm p=%.5f (0 => <5e-5)  Bonferroni x%d' % (z, zz, p, M['targets'][name]['n']))
