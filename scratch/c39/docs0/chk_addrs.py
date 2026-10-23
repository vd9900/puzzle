import hashlib, re, sys, math, collections
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58dec(s):
    n=0
    for c in s: n=n*58+B58.index(c)
    full=n.to_bytes(25,'big') if n.bit_length()<=200 else None
    return full
def valid(a):
    try:
        b=b58dec(a)
    except Exception: return False
    if b is None: return False
    return hashlib.sha256(hashlib.sha256(b[:21]).digest()).digest()[:4]==b[21:] and b[0]==0
s=open(sys.argv[1]).read().strip()
# greedy split: each address starts with '1' and is 26-34 chars; find split with all valid via DP
n=len(s); best={n:[]}
for i in range(n-1,-1,-1):
    if s[i]!='1': continue
    for L in range(34,25,-1):
        j=i+L
        if j in best and valid(s[i:j]):
            best[i]=[s[i:j]]+best[j]; break
r=best.get(0)
print('len',n,'parsed', None if r is None else len(r))
if r:
    for a in r: print(a)
    print('prize in list:', '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe' in r)
# entropy of the "verified" cosmic bin
d=open(sys.argv[2],'rb').read()
c=collections.Counter(d); H=-sum(v/len(d)*math.log2(v/len(d)) for v in c.values())
print('cosmic bin len',len(d),'entropy bits/byte %.3f'%H,'printable %.3f'%(sum(32<=x<127 for x in d)/len(d)), 'last bytes', d[-4:].hex())
