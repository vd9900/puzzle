# "sum list" = CHECKSUM list? Does faed/R60 split into fixed-length groups whose last digit is a check digit
# (digit-sum mod 9/10, Luhn, Damm 10x10 quasigroup "matrix", Verhoeff D5 "matrix")? Oracle: pass rate >> 1/9..1/10.
import sys, random; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
DAMM=[[0,3,1,7,5,9,8,6,4,2],[7,0,9,2,1,5,4,8,6,3],[4,2,0,6,8,7,1,3,5,9],[1,7,5,0,9,8,3,4,2,6],[6,1,2,3,0,4,5,9,7,8],
      [3,6,7,4,2,0,9,5,8,1],[5,8,6,9,7,2,0,1,3,4],[8,9,4,5,3,6,2,0,1,7],[9,4,3,8,6,1,7,2,0,5],[2,5,8,1,4,3,6,7,9,0]]
VD=[[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],[4,0,1,2,3,9,5,6,7,8],
    [5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],[8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]]
VP=[[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4]]
for i in range(2,8): VP.append([VP[1][VP[i-1][j]] for j in range(10)])
def damm(ds):
    x=0
    for d in ds: x=DAMM[x][d]
    return x==0
def verhoeff(ds):
    c=0
    for i,d in enumerate(reversed(ds)): c=VD[c][VP[i%8][d]]
    return c==0
def luhn(ds):
    s=0
    for i,d in enumerate(reversed(ds)):
        if i%2: d*=2; d=d-9 if d>9 else d
        s+=d
    return s%10==0
rules={'sum9':lambda ds:sum(ds[:-1])%9==ds[-1]%9,'sum10':lambda ds:sum(ds[:-1])%10==ds[-1],
       'damm':damm,'verhoeff':verhoeff,'luhn':luhn}
def digits(s,g):  # a..i=1..9, optional g->0
    return [0 if (c=='g' and g==0) else ord(c)-96 for c in s]
def best(s):
    out=[]
    for g in (7,0):
        d=digits(s,g)
        for L in range(2,21):
            for off in range(L):
                grp=[d[i:i+L] for i in range(off,len(d)-L+1,L)]
                if len(grp)<5: continue
                for rn,f in rules.items():
                    r=sum(f(x) for x in grp)/len(grp)
                    out.append((r,len(grp),g,L,off,rn))
    out.sort(reverse=True); return out
for name,s in (('faed',FAED),('faed538',FAED[:538]),('R60',R60)):
    b=best(s); print(name,'top',b[:3])
    random.seed(2); cm=[]
    for _ in range(20):
        t=list(s); random.shuffle(t); cm.append(best(''.join(t))[0][0])
    print('   shuffled-control best-of-search p50/max', sorted(cm)[10], max(cm))
