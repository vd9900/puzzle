# Is a full beam-LM sweep on the 55-digit res60 body able to separate a planted VIC from the null?
import sys, random, time; sys.argv=['x']; sys.path.insert(0,'.')
import numpy as np, vic, vicfast as V, beam, cands, run2 as R
R.SET='res60'; T=R.make_targets()
PH=cands.usable_phrases(); rnd=random.Random(5)
s=T['ctrl60_0']; sc=[]
t=time.time()
for i in range(1500):
    tag,ph=rnd.choice(PH); dtag,date=rnd.choice(cands.DATES); pn=rnd.randint(1,20)
    postag,gi=rnd.choice(V.kg_positions(date,12)); body=s[:5*gi]+s[5*gi+5:]; kgl=s[5*gi:5*gi+5]
    mp=rnd.choice(['a1','a0']); rd,kgd=rnd.choice(V.kg_readings(kgl,mp))
    k=vic.derive(ph,date,pn,kgd)
    if len(k['Q'])!=k['wa'] or len(k['R'])!=k['wb']: continue
    u=V.to_idx(body)[V.untranspose_index(55,tuple(k['Q']),tuple(k['R']),rnd.choice(['disrupted','plain']))]
    tab=V.board_tables(k['S'])
    best=max(beam.beam_decode(u,mp,tab,X=X,B=200)[0] for X in (None,6))
    sc.append(best)
sc=np.array(sc); print('n',len(sc),'sec/deriv %.4f'%((time.time()-t)/len(sc)))
print('null beam score: mean %.3f sd %.3f max %.3f q999 %.3f'%(sc.mean(),sc.std(),sc.max(),np.quantile(sc,0.999)))
# Gaussian-tail extrapolation to 8e5 derivations: mean + 4.9 sd
print('extrapolated max over 8e5: %.3f  (planted right key: -4.107)'%(sc.mean()+4.9*sc.std()))
