#!/usr/bin/env python3
import re
seq=open("salph_raw.txt",encoding="utf-8").read()
abba=[(m.start(),m.end()) for m in re.finditer(r'[ab]{20,}',seq)]
region1=seq[:abba[0][0]]

def is_prime(n):
    if n<2: return False
    for d in range(2,int(n**0.5)+1):
        if n%d==0: return False
    return True

out=[]
# --- approach A: reset counter; b should land on primes, reset when pattern needs ---
# split by 'be' and 'abe' separators, inspect chunks
for sep in ['abe','be']:
    chunks=region1.split(sep)
    out.append(f"\n=== split by '{sep}' -> {len(chunks)} chunks ===")
    for c in chunks:
        bp=[i+1 for i,ch in enumerate(c) if ch=='b']
        out.append(f"  '{c}' len={len(c)} b@{bp} primes?={[is_prime(p) for p in bp]}")

# --- approach B: PoW reset counting. Walk region1, counter increments each char;
# every time we hit 'b' it should be prime; if not, reset counter to 1 at that point.
out.append("\n=== PoW reset-counting walk ===")
cnt=0; segs=[]; cur=""
for ch in region1:
    cnt+=1; cur+=ch
    if ch=='b':
        if not is_prime(cnt):
            # reset: close segment
            segs.append((cur,cnt)); cur=""; cnt=1
segs.append((cur,cnt))
for s,c in segs:
    out.append(f"  seg='{s}' endcount={c}")

# --- approach C: the count of chars between consecutive b's (gaps) ---
bpos=[i for i,ch in enumerate(region1) if ch=='b']
gaps=[bpos[0]]+[bpos[i]-bpos[i-1] for i in range(1,len(bpos))]
out.append(f"\ngaps between b's: {gaps}")
# differences from prime gaps
primes=[p for p in range(2,200) if is_prime(p)]
out.append(f"prime gaps:       {[primes[i]-(primes[i-1] if i else 0) for i in range(len(gaps))]}")

# --- approach D: positions of b's vs prime sequence; the "extra" letters to remove ---
# If we DELETE the b's at prime positions, what remains? and a-i=1-9 of remainder
prime_b=[i for i,ch in enumerate(region1) if ch=='b' and is_prime(i+1)]
rem="".join(ch for i,ch in enumerate(region1) if i not in prime_b)
def a2n(s): return "".join(str("abcdefghio".index(c)+1 if c!='o' else 0) if c in "abcdefghi" else ('0' if c=='o' else '?') for c in s)
out.append(f"\nremove b@prime ({len(prime_b)} removed): {rem}")
out.append(f"  a-i=1-9: {a2n(rem)}")

open("prime2_out.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
