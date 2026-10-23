import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
D=lambda s:[ord(c)-96 for c in s]
def rows_aligned(d,W):
    # greedy: prefix sums must hit each multiple of W
    s=0; hits=0; rows=0
    for x in d:
        s+=x
        if s%W==0: hits+=1
    return hits
def best_W(d, Ws=range(5,80)):
    tot=sum(d); out=[]
    for W in Ws:
        h=rows_aligned(d,W)
        out.append((h/(tot/W),W,h,tot/W))
    return sorted(out,reverse=True)[:3]
for name,s in [('dbbi',DBBI),('R60',R60),('faed',FAED),('faed538',FAED[:538]),('faed_nohdr',FAED[4:])]:
    d=D(s); print(name,len(d),'sum',sum(d),best_W(d))
# controls
random.seed(1)
for k in range(3):
    f=list(FAED); random.shuffle(f); d=D(''.join(f)); print('ctrl',best_W(d))
# matrix RLE
M=MATRIX
def rle(bits):
    out=[];cur=bits[0];n=0
    for b in bits:
        if b==cur:n+=1
        else: out.append(n);cur=b;n=1
    out.append(n);return out
rowbits=[b for r in M for b in r]
print('row-major RLE',rle(rowbits)[:40], 'len',len(rle(rowbits)),'max',max(rle(rowbits)))
# spiral ccw inward, down first from (0,0)
def spiral(n):
    top,left,bot,right=0,0,n-1,n-1; out=[]
    while top<=bot and left<=right:
        for r in range(top,bot+1): out.append((r,left))
        left+=1
        for c in range(left,right+1): out.append((bot,c))
        bot-=1
        if left<=right:
            for r in range(bot,top-1,-1): out.append((r,right))
            right-=1
        if top<=bot:
            for c in range(right,left-1,-1): out.append((top,c))
            top+=1
    return out
sp=[M[r][c] for r,c in spiral(14)]
by=bytes(int(''.join(map(str,sp[i:i+8])),2) for i in range(0,192,8)); print(by)
rs=rle(sp); print('spiral RLE',''.join(chr(96+x) if x<10 else '['+str(x)+']' for x in rs), len(rs))
print('dbbi',DBBI); print('R60 ',R60)
