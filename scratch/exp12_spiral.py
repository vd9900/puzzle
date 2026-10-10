from common import *
from serial import hcond_z
import sys
f=letters_to_digits(FAED)
def spiral_coords(h,w,start='tl',first='down',cw=False):
    # generic spiral: start corner, initial direction; produce list of (r,c)
    dirs={'down':(1,0),'up':(-1,0),'right':(0,1),'left':(0,-1)}
    # order of turning
    ccw_order=['down','right','up','left']; cw_order=['down','left','up','right']
    order=cw_order if cw else ccw_order
    # rotate order so it starts at 'first'
    i=order.index(first); order=order[i:]+order[:i]
    r,c={'tl':(0,0),'tr':(0,w-1),'bl':(h-1,0),'br':(h-1,w-1)}[start]
    seen=[[False]*w for _ in range(h)]
    out=[]; di=0
    for _ in range(h*w):
        out.append((r,c)); seen[r][c]=True
        dr,dc=dirs[order[di]]
        nr,nc=r+dr,c+dc
        if not(0<=nr<h and 0<=nc<w and not seen[nr][nc]):
            di=(di+1)%4; dr,dc=dirs[order[di]]; nr,nc=r+dr,c+dc
            if not(0<=nr<h and 0<=nc<w and not seen[nr][nc]): break
        r,c=nr,nc
    return out if len(out)==h*w else None
def boustro(h,w):
    return [(r,c if r%2==0 else w-1-c) for r in range(h) for c in range(w)]
def diag(h,w):
    out=[]
    for s in range(h+w-1):
        for r in range(h):
            c=s-r
            if 0<=c<w: out.append((r,c))
    return out
def antidiag(h,w):
    out=[]
    for s in range(h+w-1):
        for r in range(h-1,-1,-1):
            c=s-r
            if 0<=c<w: out.append((r,c))
    return out
grids=[(h,570//h) for h in (2,3,5,6,10,15,19,30,38,57,95,114,190,285)]
res=[]
def ev(tag,s):
    res.append((hcond_z(s,trials=40),tag))
for h,w in grids:
    paths={}
    for start in ('tl','tr','bl','br'):
        for first in ('down','right','up','left'):
            for cw in (False,True):
                p=spiral_coords(h,w,start,first,cw)
                if p: paths[f'spiral {start} {first} {"cw" if cw else "ccw"}']=p
    paths['boustro']=boustro(h,w); paths['diag']=diag(h,w); paths['antidiag']=antidiag(h,w)
    for pn,path in paths.items():
        # A: text written row-wise into grid, read along path
        grid=[f[r*w:(r+1)*w] for r in range(h)]
        sA=''.join(grid[r][c] for r,c in path)
        # B: text written along path, read row-wise
        g2=[[None]*w for _ in range(h)]
        for ch,(r,c) in zip(f,path): g2[r][c]=ch
        sB=''.join(g2[r][c] for r in range(h) for c in range(w))
        # C: written column-wise, read along path; D: written along path, read column-wise
        gcol=[[None]*w for _ in range(h)]
        for i,ch in enumerate(f): gcol[i%h][i//h]=ch
        sC=''.join(gcol[r][c] for r,c in path)
        sD=''.join(g2[r][c] for c in range(w) for r in range(h))
        for lab,s in (('rows->path',sA),('path->rows',sB),('cols->path',sC),('path->cols',sD)):
            ev(f'{h}x{w} {pn} {lab}',s)
    print(h,w,'done',len(res),file=sys.stderr,flush=True)
res.sort()
print('N',len(res))
for z,t in res[:20]: print(round(z,2),t)
print('tail',[(round(z,2),t) for z,t in res[-3:]])
