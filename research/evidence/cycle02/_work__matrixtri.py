#!/usr/bin/env python3
"""Refine the community's promising lead: dbbi (91=C(14,2)) fills upper triangle
of a 14x14 symmetric matrix -> 14 row-sums = KEY ('matrixsumlist'). faed (570)
-> 38 groups of 15, summed = R. Combine R with KEY to get 38 letters.
Sweep operation / mapping / grouping / key-alignment to maximise English.
Original gave fragments SENDTHE / BLUENET / SETHE."""
import itertools, re
A="dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
B="faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic"
WORDS={w for w in "THE AND KEY PRIVATE PASSWORD PUZZLE MATRIX PRIME ENTER DOOR HALF BETTER YELLOW BLUE YIN YANG SEND NET CRACK BITCOIN GIVE AWAY FRONT EYES LAST STEP TRUE GSMG BELONG FUNDS LIVE NEED ALSO YOUR THIS WORD PASS CODE SOURCE WALLET ADDRESS SECRET MESSAGE NEO ONE TWO FOR YOU ARE NOW HERE".split()}
W2={w for w in WORDS if len(w)>=3}
def eng(s):
    s=s.upper();return sum(len(w)*s.count(w) for w in W2)

def build_key(Avals, zero=set(), diag=False):
    M=[[0]*14 for _ in range(14)];k=0
    for i in range(14):
        for j in range(i+1,14):
            v=0 if (i,j) in zero else Avals[k]; M[i][j]=M[j][i]=v; k+=1
    return [sum(r) for r in M]

def faed_rows(Bvals, g):
    return [sum(Bvals[j:j+g]) for j in range(0,len(Bvals),g)]

def comb(R,K,op,m):
    out=[]
    for i in range(len(R)):
        a,b=R[i],K[i%len(K)]
        if op=="xor": v=a^b
        elif op=="add": v=a+b
        elif op=="sub": v=a-b
        elif op=="rsub": v=b-a
        out.append(chr(v%m+65))
    return "".join(out)

best=[]
for amap in ("a1i9","a0i8"):
    off=1 if amap=="a1i9" else 0
    Av=[ "abcdefghi".index(c)+off for c in A]
    Bv=[ "abcdefghi".index(c)+off for c in B]
    for g in (15,):                       # 570/15=38 (matches lead)
        R=faed_rows(Bv,g)
        for keysrc in ("tri","trirev","triT"):
            if keysrc=="tri": K=build_key(Av)
            elif keysrc=="trirev": K=build_key(Av[::-1])
            else:
                # transpose fill (column-major triangle)
                M=[[0]*14 for _ in range(14)];k=0
                for j in range(14):
                    for i in range(j+1,14):
                        M[i][j]=M[j][i]=Av[k];k+=1
                K=[sum(r) for r in M]
            for op in ("xor","add","sub","rsub"):
                for m in (26,):
                    for koff in range(14):
                        Kk=K[koff:]+K[:koff]
                        s=comb(R,Kk,op,m)
                        sc=eng(s)
                        if sc>=6:
                            best.append((sc,f"{amap}/{keysrc}/{op}/m{m}/koff{koff}",s))
best.sort(reverse=True)
print(f"candidates with score>=6: {len(best)}")
for sc,l,s in best[:20]:
    print(f"[{sc:3d}] {l:30} {s}")
# also always show the base no-zero xor a1i9 for reference
Av=[ "abcdefghi".index(c)+1 for c in A]; Bv=[ "abcdefghi".index(c)+1 for c in B]
print("\nreference xor a1i9:",comb(faed_rows(Bv,15),build_key(Av),"xor",26))
