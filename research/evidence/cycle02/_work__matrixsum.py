#!/usr/bin/env python3
"""matrixsumlist experiment: use 14x14 matrix-derived number lists as a
selector/index over the SalPhaseIon sequence. Each candidate string is also
tested as the AES password for the SalPhaseIon blob."""
import re, base64, hashlib, itertools
from Crypto.Cipher import AES

# ---------- data ----------
seq = open("salph_raw.txt", encoding="utf-8").read()
abba = [(m.start(), m.end()) for m in re.finditer(r'[ab]{20,}', seq)]
region1 = seq[:abba[0][0]]                  # 91 chars
# full "data" letters before the english tail (drop abba runs + tail)
tail_i = seq.find("shabef")
data = seq[:tail_i]
# remove the two long abba runs from data to get pure a-i/o stream
clean = data
for s, e in sorted(abba, reverse=True):
    clean = clean[:s] + clean[e:]

MATRIX = """0 0 1 1 0 1 0 0 1 0 1 1 0 0
1 1 1 1 0 0 1 1 1 0 1 0 1 1
1 1 0 1 1 1 0 1 0 0 1 0 0 1
0 1 1 0 1 0 0 0 0 1 1 1 0 1
0 1 1 0 0 0 1 1 0 0 0 1 1 0
1 0 0 1 1 0 0 0 1 0 0 0 1 1
1 0 0 1 1 1 0 0 0 1 0 0 0 0
1 1 1 0 0 0 0 0 0 0 1 0 0 0
0 0 0 1 1 1 0 1 1 1 1 1 0 1
1 1 1 1 1 1 0 0 1 1 0 0 0 1
1 1 0 1 0 0 0 0 0 1 1 0 1 1
1 1 1 1 0 0 1 0 1 0 1 1 0 0
0 1 0 1 1 1 0 1 0 0 0 1 1 0
0 1 1 0 1 1 0 1 1 0 1 0 1 1"""
M = [[int(x) for x in r.split()] for r in MATRIX.splitlines()]
rowsums = [sum(r) for r in M]
colsums = [sum(M[i][j] for i in range(14)) for j in range(14)]
diag    = [M[i][i] for i in range(14)]
adiag   = [M[i][13-i] for i in range(14)]
lists = {
    "rowsums": rowsums, "colsums": colsums,
    "rowsums_rev": rowsums[::-1], "colsums_rev": colsums[::-1],
}

# ---------- AES tester ----------
BLOB = base64.b64decode("".join(open("salphaseion_blob.txt").read().split()))
SALT, CT = BLOB[8:16], BLOB[16:]
def evp(pw, salt, kl=32, il=16):
    d=b"";pr=b""
    while len(d)<kl+il:
        pr=hashlib.sha256(pr+pw+salt).digest(); d+=pr
    return d[:kl], d[kl:kl+il]
def aes_ok(pwstr):
    for pw in (pwstr.encode(), hashlib.sha256(pwstr.encode()).hexdigest().encode()):
        k,iv=evp(pw,SALT); pt=AES.new(k,AES.MODE_CBC,iv).decrypt(CT)
        pad=pt[-1]
        if 1<=pad<=16 and pt[-pad:]==bytes([pad])*pad:
            body=pt[:-pad]
            if body and sum(1 for c in body if 32<=c<127)/len(body)>0.85:
                return body
    return None

def a2n(s):
    m={**{c:str(i+1) for i,c in enumerate("abcdefghi")}, 'o':'0'}
    return "".join(m.get(c,'?') for c in s)

def readable(s):
    # quick gate: does it look like english letters/digits?
    return s and re.fullmatch(r'[a-z0-9]+', s) is not None

hits=[]
log=[]
def consider(label, s):
    if not s: return
    log.append(f"{label}: {s}")
    body=aes_ok(s)
    if body:
        hits.append((label,s,body)); print(f"[+] AES HIT via {label} pw={s!r} -> {body!r}")
    # also test numeric form
    num=a2n(s)
    if '?' not in num:
        b2=aes_ok(num)
        if b2: hits.append((label+"#num",num,b2)); print(f"[+] AES HIT via {label}#num pw={num!r} -> {b2!r}")

for tgt_name, tgt in (("region1",region1),("clean",clean)):
    for lname, L in lists.items():
        # (1) cumulative indices (1-idx)
        idx=[]; c=0
        for v in L:
            c+=v
            if 1<=c<=len(tgt): idx.append(tgt[c-1])
        consider(f"{tgt_name}/{lname}/cumul", "".join(idx))
        # (2) direct indices (value as position, 1-idx)
        consider(f"{tgt_name}/{lname}/direct",
                 "".join(tgt[v-1] for v in L if 1<=v<=len(tgt)))
        # (3) zero-out: remove chars at cumulative positions, read remainder
        cumpos=set(); c=0
        for v in L:
            c+=v
            if 1<=c<=len(tgt): cumpos.add(c-1)
        consider(f"{tgt_name}/{lname}/zeroout_cumul",
                 "".join(ch for i,ch in enumerate(tgt) if i not in cumpos))
        # (4) chunk by list: take L[k] chars sequentially, keep first of each chunk
        firsts=[]; pos=0
        for v in L:
            if pos<len(tgt): firsts.append(tgt[pos]); pos+=v
        consider(f"{tgt_name}/{lname}/chunkfirst", "".join(firsts))

open("matrixsum_log.txt","w",encoding="utf-8").write("\n".join(log))
print(f"\n[*] matrix={ {k:v for k,v in lists.items()} }")
print(f"[*] region1 len={len(region1)} clean len={len(clean)}")
print(f"[*] candidates tried={len(log)} AES hits={len(hits)}")
print(f"[*] full log in matrixsum_log.txt")
