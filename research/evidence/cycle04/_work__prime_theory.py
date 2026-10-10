#!/usr/bin/env python3
import re
seq=open("salph_raw.txt",encoding="utf-8").read()
abba=[(m.start(),m.end()) for m in re.finditer(r'[ab]{20,}',seq)]
region1=seq[:abba[0][0]]   # 91 chars

def is_prime(n):
    if n<2: return False
    for d in range(2,int(n**0.5)+1):
        if n%d==0: return False
    return True

# 1) correlation: are b's at prime positions?
out=[]
out.append(f"len={len(region1)}")
bpos=[i+1 for i,c in enumerate(region1) if c=='b']
out.append(f"b positions (1-idx): {bpos}")
out.append(f"b at prime pos:    {[p for p in bpos if is_prime(p)]}")
out.append(f"b at composite:    {[p for p in bpos if not is_prime(p)]}")
primes=[p for p in range(1,len(region1)+1) if is_prime(p)]
out.append(f"all primes<=91:    {primes}")
out.append(f"primes with b:     {[p for p in primes if region1[p-1]=='b']}")
out.append(f"primes without b:  {[(p,region1[p-1]) for p in primes if region1[p-1]!='b']}")

# annotated view
ann="".join(f"[{c}]" if is_prime(i+1) else c for i,c in enumerate(region1))
out.append("\nannotated (prime pos in []):\n"+ann)

# 2) extraction strategies -> map a-i=1-9, o=0
def a2n(s):
    return "".join(str("abcdefghi".index(c)+1) if c in "abcdefghi" else ("0" if c=="o" else "?") for c in s)

comp = "".join(c for i,c in enumerate(region1) if not is_prime(i+1))
prim = "".join(c for i,c in enumerate(region1) if is_prime(i+1))
nob  = region1.replace("b","")
out.append(f"\ncomposite-pos chars: {comp}")
out.append(f"  -> a..i=1..9:      {a2n(comp)}")
out.append(f"prime-pos chars:     {prim}")
out.append(f"region without b:    {nob}")
out.append(f"  -> a..i=1..9:      {a2n(nob)}")

open("prime_out.txt","w",encoding="utf-8").write("\n".join(out))
print("written prime_out.txt")
