import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch/c42/ideas_ctf_player'); sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED
NUM={7:(-1,-1),8:(-1,0),9:(-1,1),4:(0,-1),5:(0,0),6:(0,1),1:(1,-1),2:(1,0),3:(1,1)}
def walk(s,start_down=True):
    r=c=0; down=start_down; pts=[]; ndown=0
    for ch in s:
        d=ord(ch)-96
        if d==5: down=not down; continue
        dr,dc=NUM[d]; r+=dr; c+=dc
        if down: pts.append((r,c)); ndown+=1
    return pts,ndown
def st(s,sd):
    p,n=walk(s,sd); return len(set(p)),n,len(set(p))/max(n,1)
rnd=random.Random(9)
for sd in (True,False):
    u,n,ratio=st(FAED,sd)
    # control 1: full shuffle; control 2: keep positions of 'e' fixed, shuffle other letters (isolates the move content)
    c1=[];c2=[]
    pos=[i for i,c in enumerate(FAED) if c!='e']; other=[FAED[i] for i in pos]
    for _ in range(2000):
        l=list(FAED); rnd.shuffle(l); c1.append(st(''.join(l),sd))
        o=other[:]; rnd.shuffle(o); l=list(FAED)
        for i,ch in zip(pos,o): l[i]=ch
        c2.append(st(''.join(l),sd))
    for lab,c in (('fullshuffle',c1),('e-fixed',c2)):
        pu=sum(x[0]<=u for x in c)/len(c); pr=sum(x[2]<=ratio for x in c)/len(c)
        nd=sorted(x[1] for x in c)[len(c)//2]
        print(f'start_down={sd} uniq={u} ndown={n} ratio={ratio:.3f} | {lab}: p(uniq<=)={pu:.4f} p(ratio<=)={pr:.4f} median ndown={nd}')
