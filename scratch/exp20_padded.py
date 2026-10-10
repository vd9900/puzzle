from common import *
from serial import hcond_z
from exp12_spiral import spiral_coords, boustro
import sys
f=letters_to_digits(FAED); N=len(f)
res=[]
def ev(t,s): res.append((hcond_z(s,trials=40),t))
grids=[]
for h in range(10,41):
    for w in range(10,61):
        if h*w>=N and h*w<=N+30 and h*w!=N: grids.append((h,w))
print(len(grids),'padded grids',file=sys.stderr)
for h,w in grids:
    paths={}
    for st in ('tl','tr','bl','br'):
        for fi in ('down','right','up','left'):
            for cw in (False,True):
                p=spiral_coords(h,w,st,fi,cw)
                if p: paths[f'sp {st} {fi} {"cw" if cw else "ccw"}']=p
    paths['boustro']=boustro(h,w)
    for pn,path in paths.items():
        # A: write rows (first N cells), read along path skipping empties
        grid={}
        for i,ch in enumerate(f): grid[(i//w,i%w)]=ch
        sA=''.join(grid[p] for p in path if p in grid)
        # B: write along path (first N cells of path), read rows
        g2={p:ch for p,ch in zip(path,f)}
        sB=''.join(g2[(r,c)] for r in range(h) for c in range(w) if (r,c) in g2)
        # C: write rows, read path REVERSED (from centre outward)
        sC=sA[::-1]
        ev(f'{h}x{w} {pn} rows->path',sA); ev(f'{h}x{w} {pn} path->rows',sB)
# numeric keyed columnar
def rank_key(nums):
    idx=sorted(range(len(nums)), key=lambda i:(nums[i],i)); order=[0]*len(nums)
    for r,i in enumerate(idx): order[i]=r
    return order
def irregular_coldec(ct, order):
    n=len(order); L=len(ct); rows=L//n; extra=L%n
    lens=[rows+(1 if c<extra else 0) for c in range(n)]
    cols=[None]*n; pos=0
    for r in range(n):
        c=order.index(r); cols[c]=ct[pos:pos+lens[c]]; pos+=lens[c]
    return ''.join(cols[c][r] for r in range(rows+1) for c in range(n) if r<lens[c])
def irregular_colenc(pt, order):
    n=len(order); cols=[[] for _ in range(n)]
    for i,ch in enumerate(pt): cols[i%n].append(ch)
    return ''.join(''.join(cols[order.index(r)]) for r in range(n))
for key in ['1812','21','11110','1141','14','1616','486604799','11092001','2001','1999','915','159','101','42','140','2357','23571113','11235813','31415926','2718281','3079','422','336','341','0101','022350','89727','1357','196','570','91','13','7','38','15','1234567891','123456789','987654321','0123456789']:
    nums=[int(c) for c in key]
    if len(nums)<2: continue
    order=rank_key(nums)
    ev(f'num {key} idec',irregular_coldec(f,order)); ev(f'num {key} ienc',irregular_colenc(f,order))
# autokey / lag differences
for k in range(1,120):
    d9=''.join(str(((int(f[i])-int(f[i-k]))%9)+1) for i in range(k,N))
    s9=''.join(str(((int(f[i])+int(f[i-k])-2)%9)+1) for i in range(k,N))
    ev(f'lagdiff k={k}',d9); ev(f'lagsum k={k}',s9)
res.sort(); print('N',len(res))
for z,t in res[:15]: print(round(z,2),t)
print('tail',[(round(z,2),t) for z,t in res[-3:]])
