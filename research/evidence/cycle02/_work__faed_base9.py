#!/usr/bin/env python3
"""faed has flat IoC (~1/9) => high-entropy base-9 data, not enciphered text.
Convert base-9 (a-i) to bytes via several schemes and look for structure:
ascii text, OpenSSL 'Salted__', hex private-key shape, etc."""
import re
faed="faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic"

def report(tag, b: bytes):
    if not b: return
    asc=sum(1 for x in b if 32<=x<127 or x in (9,10,13))/len(b)
    txt="".join(chr(x) if 32<=x<127 else '.' for x in b)
    notable=[]
    if b[:8]==b"Salted__": notable.append("SALTED__!!")
    if asc>0.85: notable.append(f"ASCII{asc:.2f}!!")
    # printable runs >=6
    runs=re.findall(rb'[ -~]{6,}', b)
    if runs: notable.append("runs:"+b" | ".join(runs[:4]).decode('latin1'))
    print(f"[{tag}] {len(b)}B ascii={asc:.2f} {' '.join(notable)}")
    if notable: print("     hex:",b.hex()[:80]); print("     txt:",txt[:90])

for amap,desc in (("abcdefghi","a0..i8"),):
    # whole bignum, both digit orders & both endians
    for label,seq in (("fwd",faed),("rev",faed[::-1])):
        num=0
        for ch in seq: num=num*9+amap.index(ch)
        bl=(num.bit_length()+7)//8
        report(f"base9 {desc} {label} big-endian", num.to_bytes(bl,'big'))
        report(f"base9 {desc} {label} little-endian", num.to_bytes(bl,'little'))

# a1..i9 then subtract 1 == a0..i8, same. Try a1..i9 as base-10-ish (no, keep base9).
# Chunked: groups of k base-9 digits -> integer -> byte(s)
amap="abcdefghi"
vals=[amap.index(c) for c in faed]            # 0..8
vals1=[v+1 for v in vals]                      # 1..9
# 3 base-9 digits -> 0..728 -> mod 256 (and -> 2 bytes)
for k in (2,3,4):
    chunks=[vals[i:i+k] for i in range(0,len(vals)-k+1,k)]
    by=bytes((sum(d*(9**(k-1-j)) for j,d in enumerate(c))%256) for c in chunks)
    report(f"chunk{k}base9 mod256", by)
# pairs of digits as decimal 11..99 -> ascii (already ~random) skip
# Interpret as base-9 -> base-16 string directly (hex chars 0-8 only) then hex->bytes
hexish="".join(str(v) for v in vals)           # digits 0-8
if len(hexish)%2: hexish=hexish[:-1]
try: report("digits-as-hex", bytes.fromhex(hexish))
except Exception as e: print("digits-as-hex: ",e)

# base-9 whole number -> decimal string, look for ascii via decimal pairs
num=0
for ch in faed: num=num*9+amap.index(ch)
dec=str(num)
print("\nbase9->decimal length:",len(dec),"first60:",dec[:60])
# decimal pairs -> ascii
pr="".join(chr(int(dec[i:i+2])) if 32<=int(dec[i:i+2])<=126 else '.' for i in range(0,len(dec)-1,2))
print("decimal-pairs ascii:",pr[:90])
print("\nbase9->hex first80:",format(num,'x')[:80],"...len",len(format(num,'x')))
