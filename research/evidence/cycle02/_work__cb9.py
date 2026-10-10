#!/usr/bin/env python3
"""Base-9 straddling checkerboard (RB's 'mod 9' insight) on dbbi.
9 columns; 2 escape digits -> 7 top-row letters + 2 rows of 9 = 25 cells.
26 letters -> merge I/J (classic). Sweep alphabets, escape pairs, digit mapping."""
import itertools
dbbi="dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"

def board9(alpha25, e1, e2, digitset):
    # digitset: the 9 column labels e.g. '123456789' or '012345678'
    e1,e2=sorted((e1,e2),key=lambda d:digitset.index(d))
    cols=list(digitset)
    top=[c for c in cols if c not in (e1,e2)]   # 7
    bd={}
    i=0
    for c in top: bd[c]=alpha25[i]; i+=1
    for c in cols: bd[e1+c]=alpha25[i]; i+=1
    for c in cols: bd[e2+c]=alpha25[i]; i+=1
    return bd
def decode9(digits, alpha25, e1, e2, digitset):
    bd=board9(alpha25,e1,e2,digitset)
    out=[];i=0
    while i<len(digits):
        c=digits[i]
        if c in (e1,e2):
            if i+1>=len(digits): break
            out.append(bd.get(digits[i:i+2],'?')); i+=2
        else:
            out.append(bd.get(c,'?')); i+=1
    return "".join(out)

def kw25(key):
    s="".join(dict.fromkeys((key+"ABCDEFGHIKLMNOPQRSTUVWXYZ").upper()))  # no J (I/J merge)
    return s[:25]
alphabets={"matrixsumlist":kw25("MATRIXSUMLIST"),"enter":kw25("ENTER"),
 "plain":kw25(""),"yellowblue":kw25("YELLOWBLUE"),"fubcdora":kw25("FUBCDORALETHINGKYMVPS"),
 "salphaseion":kw25("SALPHASEION"),"thispassword":kw25("THISPASSWORD")}
WORDS=set("THE AND THAT HAVE FOR NOT WITH YOU THIS BUT FROM THEY KEY PRIVATE PASSWORD MATRIX PRIME ENTER DOOR HALF BETTER YELLOW BLUE CRACK BITCOIN GIVE AWAY FRONT EYES LAST STEP TRUE GSMG BELONG FUNDS LIVE NEED ALSO YOUR WORD PASS CODE SOURCE WALLET SECRET MESSAGE FOLLOW WHITE RABBIT HERE OPEN LOCK ARE NOW ONE TWO SUM LIST BEFORE CHOICE YANG YIN ANSWER ROOM NEO TAKE WISEMAN HUNDRED".split())
W=set(w for w in WORDS if len(w)>=4)
Wall=set(w for w in WORDS if len(w)>=3)
def eng(s):
    s=s.upper().replace('?','')
    return sum(len(w)*s.count(w) for w in Wall), sum(1 for w in W if w in s)

best=[]
for ds in ("123456789","012345678"):
    mp={c:str((i+1) if ds[0]=='1' else i) for i,c in enumerate("abcdefghi")}
    digits="".join(mp[c] for c in dbbi)
    for an,al in alphabets.items():
        if len(al)<25: continue
        for e1,e2 in itertools.combinations(ds,2):
            s=decode9(digits,al,e1,e2,ds)
            sc,lh=eng(s)
            if lh>=3 or sc>=14:
                best.append((lh,sc,f"{ds[0]}../{an}/e{e1}{e2}",s))
best.sort(reverse=True)
print(f"base-9 checkerboard sweep: hits={len(best)}")
for lh,sc,l,s in best[:20]:
    print(f"[L{lh} s{sc}] {l:22} {s[:60]}")
if not best:
    print("none above threshold. Top 8 by raw score:")
    allr=[]
    for ds in ("123456789","012345678"):
        mp={c:str((i+1) if ds[0]=='1' else i) for i,c in enumerate("abcdefghi")}
        digits="".join(mp[c] for c in dbbi)
        for an,al in alphabets.items():
            for e1,e2 in itertools.combinations(ds,2):
                s=decode9(digits,al,e1,e2,ds);sc,lh=eng(s)
                allr.append((sc,lh,f"{ds[0]}../{an}/e{e1}{e2}",s))
    allr.sort(reverse=True)
    for sc,lh,l,s in allr[:8]: print(f"[s{sc} L{lh}] {l:22} {s[:60]}")
