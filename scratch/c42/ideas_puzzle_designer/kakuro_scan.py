import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
M=MATRIX
def runs_for(v, order='row'):
    cells=[(r,c) for r in range(14) for c in range(14) if M[r][c]==v] if order=='row' else [(r,c) for c in range(14) for r in range(14) if M[r][c]==v]
    idx={cell:i for i,cell in enumerate(cells)}
    runs=[]
    for r in range(14):
        cur=[]
        for c in range(15):
            if c<14 and M[r][c]==v: cur.append(idx[(r,c)])
            else:
                if len(cur)>=2: runs.append(cur)
                cur=[]
    for c in range(14):
        cur=[]
        for r in range(15):
            if r<14 and M[r][c]==v: cur.append(idx[(r,c)])
            else:
                if len(cur)>=2: runs.append(cur)
                cur=[]
    return len(cells), runs
def viol(s, runs):
    return sum(len(run)-len(set(s[i] for i in run)) for run in runs)
for v in (0,1):
  for order in ('row','col'):
    n,runs=runs_for(v,order)
    best=[]
    for name,src in [('faed',FAED),('dbbi',DBBI),('faed_rev',FAED[::-1]),('dbbi_rev',DBBI[::-1])]:
        for off in range(0,len(src)-n+1):
            best.append((viol(src[off:off+n],runs),name,off))
    best.sort()
    random.seed(3); ctrl=[]
    for k in range(2000):
        s=''.join(random.choice('abcdefghi') for _ in range(n)); ctrl.append(viol(s,runs))
    print('v',v,order,'cells',n,'runs',len(runs),'best',best[:3],'ctrl min',min(ctrl),'mean',sum(ctrl)/len(ctrl))
