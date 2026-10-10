from common import *
import sys, itertools
sys.path.insert(0,'/home/vin/bitcoin_puzzle')
from tools.gsmg import extract_grid, SOURCES, spiral_coordinates
g=extract_grid(SOURCES/'gsmg-puzzle.png'); colors=g['colors']
events={(r,c):colors[r][c] for r in range(14) for c in range(14) if colors[r][c] in ('blue','yellow','near_white')}
# token bits from dbbi physical order: lone b ->1 (blue), be -> 0
toks=[]; i=0
while i<len(DBBI):
    if DBBI[i]=='b':
        if i+1<len(DBBI) and DBBI[i+1]=='e': toks.append('0'); i+=2
        else: toks.append('1'); i+=1
    else: i+=1
T=''.join(toks); print('token bits',T,len(T))
def bits_for(order, white='0'):
    return ''.join('1' if events[p]=='blue' else ('0' if events[p]=='yellow' else white) for p in order if p in events)
def spiral_generic(h,w,start,first,cw):
    dirs={'down':(1,0),'up':(-1,0),'right':(0,1),'left':(0,-1)}
    order=['down','left','up','right'] if cw else ['down','right','up','left']
    i=order.index(first); order=order[i:]+order[:i]
    r,c={'tl':(0,0),'tr':(0,w-1),'bl':(h-1,0),'br':(h-1,w-1)}[start]
    seen=set(); out=[]; di=0
    for _ in range(h*w):
        out.append((r,c)); seen.add((r,c))
        dr,dc=dirs[order[di]]; nr,nc=r+dr,c+dc
        if not(0<=nr<h and 0<=nc<w and (nr,nc) not in seen):
            di=(di+1)%4; dr,dc=dirs[order[di]]; nr,nc=r+dr,c+dc
            if not(0<=nr<h and 0<=nc<w and (nr,nc) not in seen): break
        r,c=nr,nc
    return out if len(out)==196 else None
orders={}
for st in ('tl','tr','bl','br'):
    for fi in ('down','right','up','left'):
        for cw in (False,True):
            p=spiral_generic(14,14,st,fi,cw)
            if p: orders[f'spiral {st} {fi} {"cw" if cw else "ccw"}']=p; orders[f'spiral {st} {fi} {"cw" if cw else "ccw"} outward']=p[::-1]
orders['rowmajor']=[(r,c) for r in range(14) for c in range(14)]
orders['colmajor']=[(r,c) for c in range(14) for r in range(14)]
orders['rowmajor rev']=orders['rowmajor'][::-1]; orders['colmajor rev']=orders['colmajor'][::-1]
orders['boustro rows']=[(r,c if r%2==0 else 13-c) for r in range(14) for c in range(14)]
orders['boustro cols']=[(r if c%2==0 else 13-r,c) for c in range(14) for r in range(14)]
orders['diag']=[(r,s-r) for s in range(27) for r in range(14) if 0<=s-r<14]
orders['antidiag']=[(r,r-s+13) for s in range(27) for r in range(14) if 0<=r-s+13<14]
# the original phase-0 spiral from the repo
orders['repo spiral']=spiral_coordinates(14)
best=[]
for name,order in orders.items():
    for white in ('0','1','x'):
        b=bits_for(order,white)
        if white=='x': b=b.replace('x','')
        for tgt_name,tgt in (('T',T),('Trev',T[::-1]),('Tinv',T.translate(str.maketrans('01','10'))),('Tinvrev',T[::-1].translate(str.maketrans('01','10')))):
            m=sum(x==y for x,y in zip(b,tgt)); 
            pref=0
            for x,y in zip(b,tgt):
                if x!=y: break
                pref+=1
            best.append((m,pref,name,white,tgt_name,b))
best.sort(reverse=True)
for m,pref,name,white,tn,b in best[:12]: print(m,pref,name,'W='+white,tn,b)
