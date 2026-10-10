#!/usr/bin/env python3
"""Triangle/XOR framework with principled zeroing sweep.
dbbi -> upper triangle of 14x14 -> row sums = KEY. faed -> 38x15 -> row sums = R.
out[i] = chr((R[i] OP K[i%14]) %26 +65). Zero matrix cells and/or faed cells by
blue/yellow/prime predicates ('some characters need to be zeroed out'). Maximize English."""
import itertools, re
A="dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
B="faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic"
G="00110b0010110y 11b1001110b011 1101110b001001 0110b000011101 0b1000110y0110 100110y010y011 100b1100010y00 b11000000010y0 00011b0111110b 11b111y0110001 1101000y011011 11110010b01100 0b0111010y0110 01b0110110b011".split()
blue={r*14+c for r,row in enumerate(G) for c,x in enumerate(row) if x=='b'}   # 0-idx linear
yellow={r*14+c for r,row in enumerate(G) for c,x in enumerate(row) if x=='y'}
def isp(n): return n>1 and all(n%k for k in range(2,int(n**.5)+1))

WORDS={w for w in "THE AND KEY PRIVATE PASSWORD PUZZLE MATRIX PRIME ENTER DOOR HALF BETTER YELLOW BLUE YIN YANG SEND NET CRACK BITCOIN GIVE AWAY FRONT EYES LAST STEP TRUE GSMG BELONG FUNDS LIVE NEED ALSO YOUR THIS WORD PASS CODE SOURCE WALLET ADDRESS SECRET MESSAGE FOLLOW WHITE RABBIT HOLE DOWN ONE TWO ARE NOW HERE OPEN LOCK WITH THAT NOT YOU FOR ALL HAS GET".split()}
W3={w for w in WORDS if len(w)>=3}
def eng(s): s=s.upper(); return sum(len(w)*s.count(w) for w in W3)

def make(amap_off, key_zero, faed_zero, op, krev=False, kfill='row'):
    Av=[ "abcdefghi".index(c)+amap_off for c in A]
    Bv=[ "abcdefghi".index(c)+amap_off for c in B]
    if krev: Av=Av[::-1]
    # build 14x14 symmetric from triangle
    M=[[0]*14 for _ in range(14)]; k=0
    if kfill=='row':
        cells=[(i,j) for i in range(14) for j in range(i+1,14)]
    else:  # column-major
        cells=[(i,j) for j in range(14) for i in range(j+1,14)]
    for idx,(i,j) in enumerate(cells):
        lin=i*14+j
        v=0 if key_zero(i,j,lin) else Av[idx]
        M[i][j]=M[j][i]=v
    K=[sum(r) for r in M]
    # faed rows of 15 with zeroing
    R=[]
    for g in range(0,570,15):
        s=0
        for off in range(15):
            p=g+off
            if not faed_zero(p, B[p]): s+=Bv[p]
        R.append(s)
    out=[]
    for i in range(38):
        a,b=R[i],K[i%14]
        if op=='xor': v=a^b
        elif op=='add': v=a+b
        elif op=='sub': v=a-b
        elif op=='rsub': v=b-a
        out.append(chr(v%26+65))
    return "".join(out)

# zeroing predicate library
keyZ={
 "none": lambda i,j,lin: False,
 "primeLin": lambda i,j,lin: isp(lin+1),
 "blueLin": lambda i,j,lin: lin in blue,
 "yellowLin": lambda i,j,lin: lin in yellow,
 "byLin": lambda i,j,lin: lin in blue or lin in yellow,
 "primeI": lambda i,j,lin: isp(i+1),
 "primeJ": lambda i,j,lin: isp(j+1),
 "diagNear": lambda i,j,lin: j==i+1,
}
faedZ={
 "none": lambda p,ch: False,
 "primePos": lambda p,ch: isp(p+1),
 "nonPrimePos": lambda p,ch: not isp(p+1),
 "blueMod": lambda p,ch: p in blue,
 "yellowMod": lambda p,ch: p in yellow,
 "charB": lambda p,ch: ch=='b',
 "primePosInGroup": lambda p,ch: isp(p%15+1),
}

best=[]
for amap_off in (1,0):
  for op in ('xor','add','sub','rsub'):
    for krev in (False,True):
      for kfill in ('row','col'):
        for kzn,kz in keyZ.items():
          for fzn,fz in faedZ.items():
            s=make(amap_off,kz,fz,op,krev,kfill)
            sc=eng(s)
            if sc>=8:
                best.append((sc,f"off{amap_off}/{op}/rev{krev}/{kfill}/K:{kzn}/F:{fzn}",s))
best.sort(reverse=True)
print(f"candidates score>=8: {len(best)}")
for sc,l,s in best[:25]:
    print(f"[{sc:3d}] {l:48} {s}")
