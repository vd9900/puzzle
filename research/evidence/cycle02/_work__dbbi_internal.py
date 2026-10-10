#!/usr/bin/env python3
"""Internal decode of dbbi using prime / BE-ABE-separator / matrixSUMlist
structure. Scans many segmentation+aggregation schemes for printable/English
output. Also tests results as the SalPhaseIon AES password."""
import base64, hashlib, re, itertools
from Crypto.Cipher import AES

dbbi="dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
N=len(dbbi)
VAL1={c:i+1 for i,c in enumerate("abcdefghi")}   # a=1..i=9
VAL0={c:i   for i,c in enumerate("abcdefghi")}   # a=0..i=8
def is_prime(n): return n>1 and all(n%k for k in range(2,int(n**.5)+1))

BLOB=base64.b64decode("".join(open("salphaseion_blob.txt").read().split()))
SALT,CT=BLOB[8:16],BLOB[16:]
def evp(pw,kl=32,il=16):
    d=b"";pr=b""
    while len(d)<kl+il: pr=hashlib.sha256(pr+pw+SALT).digest();d+=pr
    return d[:kl],d[kl:kl+il]
def aes_try(s):
    for c in {s,s.upper(),s.lower(),hashlib.sha256(s.encode()).hexdigest()}:
        if not c: continue
        k,iv=evp(c.encode());pt=AES.new(k,AES.MODE_CBC,iv).decrypt(CT);p=pt[-1]
        if 1<=p<=16 and pt[-p:]==bytes([p])*p:
            b=pt[:-p]
            if b and sum(1 for ch in b if 32<=ch<127)/len(b)>0.85: return c,b
    return None
WORDS={w for w in "THE AND KEY PRIVATE PASSWORD PUZZLE MATRIX PRIME ENTER DOOR HALF BETTER YELLOW BLUE YINYANG CRACK BITCOIN GIVE AWAY FRONT EYES LAST STEP TRUE GSMG BELONG FUNDS LIVE NEED ALSO YOUR THIS HASH SALT SOURCE CODE KEYNOTE WISEMAN NEO ARCHITECT".split() if len(w)>=3}
def eng(s): s=s.upper(); return sum(len(w)*s.count(w) for w in WORDS)
def printable(nums, lo=32, hi=126):
    out=[];ok=0
    for v in nums:
        if lo<=v<=hi: out.append(chr(v));ok+=1
        else: out.append('·')
    return "".join(out),ok

HITS=[];CAND=[]
def reg(label,s):
    if not s: return
    if re.fullmatch(r'[ -~]+',s):
        CAND.append((eng(s)+sum(c!='·' for c in s)//4,label,s))
        clean=s.replace('·','')
        if clean.isalnum():
            a=aes_try(clean)
            if a: HITS.append((label,clean,a));print(f"[+++AES] {label} pw={a[0]!r} -> {a[1]!r}")

def nums_to_variants(nums,label):
    # direct ascii
    reg(label+"/ascii", printable(nums)[0])
    # +offset to land in ascii ranges
    for off in (64,96,48,55,87):  # A-1, a-1, '0', A for 10.., a for 10..
        reg(f"{label}/+{off}", printable([n+off for n in nums])[0])
    # A1Z26 letters (1-26)
    if all(1<=n<=26 for n in nums):
        reg(label+"/a1z26", "".join(chr(64+n) for n in nums))
    if all(0<=n<=25 for n in nums):
        reg(label+"/a0z25", "".join(chr(65+n) for n in nums))
    # concatenated digits -> ascii 2/3
    ds="".join(str(n) for n in nums)
    reg(label+"/concat2", printable([int(ds[i:i+2]) for i in range(0,len(ds)-1,2)])[0])
    reg(label+"/concat3", printable([int(ds[i:i+3]) for i in range(0,len(ds)-2,3)])[0])

# ----- (A) segment by separators, aggregate -----
for sep in ("be","abe","e","b","bb"):
    parts=[p for p in dbbi.split(sep)]
    for VAL,vn in ((VAL1,"v1"),(VAL0,"v0")):
        for agg,fn in (("sum",lambda c:sum(VAL[x] for x in c)),
                       ("len",lambda c:len(c)),
                       ("sumNB",lambda c:sum(VAL[x] for x in c if x!='b')),
                       ("prod",lambda c:__import__('math').prod([VAL[x] for x in c] or [0]))):
            nums=[fn(p) for p in parts if p!='']
            nums_to_variants(nums,f"split[{sep}]/{vn}/{agg}")

# ----- (B) zero-out at prime positions, decode remainder -----
for VAL,vn in ((VAL1,"v1"),(VAL0,"v0")):
    rem=[VAL[dbbi[i]] for i in range(N) if not is_prime(i+1)]
    nums_to_variants(rem,f"dropPrimePos/{vn}")
    keep=[VAL[dbbi[i]] for i in range(N) if is_prime(i+1)]
    nums_to_variants(keep,f"keepPrimePos/{vn}")
    # remove b's entirely
    nob=[VAL[c] for c in dbbi if c!='b']
    nums_to_variants(nob,f"dropAllB/{vn}")
    # remove b's only at prime positions
    nopb=[VAL[dbbi[i]] for i in range(N) if not (dbbi[i]=='b' and is_prime(i+1))]
    nums_to_variants(nopb,f"dropPrimeB/{vn}")

# ----- (C) b-position structure -----
bpos=[i+1 for i in range(N) if dbbi[i]=='b']
gaps=[bpos[0]]+[bpos[i]-bpos[i-1] for i in range(1,len(bpos))]
nums_to_variants(bpos,"bpositions")
nums_to_variants(gaps,"bgaps")

# ----- (D) matrix sum list: 7x13 & 13x7 grids, row/col sums -----
for VAL,vn in ((VAL1,"v1"),(VAL0,"v0")):
    vals=[VAL[c] for c in dbbi]
    for r,c in ((7,13),(13,7)):
        g=[vals[i*c:(i+1)*c] for i in range(r)]
        rowsum=[sum(row) for row in g]
        colsum=[sum(g[i][j] for i in range(r)) for j in range(c)]
        nums_to_variants(rowsum,f"grid{r}x{c}.rowsum/{vn}")
        nums_to_variants(colsum,f"grid{r}x{c}.colsum/{vn}")

CAND.sort(reverse=True)
with open("dbbi_internal_out.txt","w",encoding="utf-8") as f:
    f.write(f"AES hits: {len(HITS)}\n\nTOP 40:\n")
    for sc,l,s in CAND[:40]:
        f.write(f"[{sc:4d}] {l:26} {s}\n")
print(f"AES hits={len(HITS)}; candidates={len(CAND)}; see dbbi_internal_out.txt")
print("TOP 12:")
for sc,l,s in CAND[:12]:
    print(f"  [{sc:4d}] {l:26} {s[:55]}")
