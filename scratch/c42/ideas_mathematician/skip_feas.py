# "sum list" = prefix sums used as POSITIONS (skip cipher): key digits from dbbi tokenizations; read faed at running sums.
import sys, re; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, zmethod_digits
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
t81=re.findall(r'be|[a-i]',DBBI)
val=lambda t:25 if t=='be' else ord(t)-96
keys={'raw91':list(DBBI),'tok81':t81,'R60':list(R60),'R56':[t for t in t81 if t not in('b','be')]}
for k,v in keys.items(): print(k,len(v),'sum',sum(val(t) for t in v))
def pr(b): return sum(32<=c<127 for c in b)/max(1,len(b))
res=[]
for kn,ks in keys.items():
    steps=[val(t) for t in ks]
    for src,S in (('faed',FAED),('faed_rev',FAED[::-1])):
        for start in (0,-1):
            pos=[];p=start
            for s in steps:
                p+=s
                if p>=len(S): break
                pos.append(p)
            letters=''.join(S[i] for i in pos)
            for g0 in (0,1):
                ds=''.join('0' if (c=='g' and g0) else str(ord(c)-96) for c in letters)
                b=zmethod_digits(ds.lstrip('0') or '0')
                res.append((pr(b),kn,src,start,g0,len(pos),letters[:40],b[:30]))
res.sort(key=lambda r:-r[0])
for r in res[:6]: print(r)
