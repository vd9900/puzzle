# Digits 1..9 as keypad DIRECTIONS (numpad 789/456/123 or phone 123/456/789); 5 = centre (no move / pen toggle).
# A drawing would show stroke structure: many revisits, bounded box; random walk diffuses ~sqrt(n). Render + stats vs shuffles.
import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
NUM={7:(-1,-1),8:(-1,0),9:(-1,1),4:(0,-1),5:(0,0),6:(0,1),1:(1,-1),2:(1,0),3:(1,1)}
PHO={1:(-1,-1),2:(-1,0),3:(-1,1),4:(0,-1),5:(0,0),6:(0,1),7:(1,-1),8:(1,0),9:(1,1)}
def walk(s,L,pen_toggle=False):
    r=c=0; pts=[(0,0)]; down=True
    for ch in s:
        d=ord(ch)-96
        if d==5 and pen_toggle: down=not down; continue
        dr,dc=L[d]; r+=dr; c+=dc
        if down: pts.append((r,c))
    return pts
def stats(pts):
    rs=[p[0] for p in pts]; cs=[p[1] for p in pts]
    return len(set(pts)), (max(rs)-min(rs)+1)*(max(cs)-min(cs)+1), (abs(pts[-1][0])+abs(pts[-1][1]))
def render(pts,maxw=120):
    rs=[p[0] for p in pts]; cs=[p[1] for p in pts]; r0,c0=min(rs),min(cs)
    H=max(rs)-r0+1; W=max(cs)-c0+1
    g=[[' ']*W for _ in range(H)]
    for (r,c) in pts: g[r-r0][c-c0]='#'
    return '\n'.join(''.join(row[:maxw]) for row in g[:60])
rnd=random.Random(2)
for name,s in [('dbbi',DBBI),('R60',R60),('faed',FAED)]:
    for lname,L in [('numpad',NUM),('phone',PHO)]:
        for pt in (False,True):
            p=walk(s,L,pt); st=stats(p)
            ctrl=[]
            for _ in range(200):
                l=list(s); rnd.shuffle(l); ctrl.append(stats(walk(''.join(l),L,pt)))
            uniq=sorted(x[0] for x in ctrl); area=sorted(x[1] for x in ctrl)
            pu=sum(x<=st[0] for x in uniq)/len(uniq)
            print(f'{name:5s} {lname:6s} pen5={pt!s:5s} uniqcells={st[0]:4d} (ctrl med {uniq[100]}, p_low={pu:.3f}) box={st[1]} (ctrl med {area[100]}) end_dist={st[2]}')
print(render(walk(FAED,NUM)))
