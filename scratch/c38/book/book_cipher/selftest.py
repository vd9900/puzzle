"""Planted self-test: encode an English message with the book via each reading family, then run the same detector."""
import random, sys
sys.argv=['x']
exec(open('run_tests.py').read().split("NC=200")[0])   # reuse model + decode + scorer (no test loop)
msg='thetruthisinfrontofyoureyesbutyouarenotseeingit'
rng=random.Random(5)
def enc(kind,sizes):
    out=''
    for ch in msg:
        if kind=='pw':
            c=[(p,i+1) for p in PW for i,w in enumerate(PW[p]) if w[0]==ch and p<10**sizes[0] and i+1<10**sizes[1]]
        elif kind=='pl':
            c=[(p,i+1) for p in PL for i,x in enumerate(PL[p]) if x==ch and p<10**sizes[0] and i+1<10**sizes[1]]
        elif kind=='bw':
            c=[(i+1,) for i,w in enumerate(BOOKW) if w[0]==ch and i+1<10**sizes[0]]
        if not c: return None
        t=rng.choice(c); out+=''.join(str(v).zfill(s) for v,s in zip(t,sizes))
    return out
for kind,sizes,mode in [('pw',(3,2),'first'),('pw',(3,3),'first'),('pl',(3,3),'letter'),('bw',(5,),'first')]:
    d=enc(kind,sizes); v,s,n=decode(d,kind,sizes,mode); q=qscore(s)
    cq=[];cv=[]
    for _ in range(200):
        x=list(d); rng.shuffle(x); vv,ss,_=decode(''.join(x),kind,sizes,mode); cq.append(qscore(ss)); cv.append(vv)
    print(kind,sizes,len(d),'digits valid',v,'ctrl',round(sum(cv)/200,3),'q',round(q,3),'ctrl max',round(max(cq),3),'p_q',(1+sum(c>=q for c in cq))/201,'p_valid',(1+sum(c>=v for c in cv))/201)
