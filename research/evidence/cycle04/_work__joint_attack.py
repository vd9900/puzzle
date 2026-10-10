#!/usr/bin/env python3
"""JOINT 4-parameter VIC attack with END-OF-CHAIN AES verification.
Pipeline (RB's reading): decode(dbbi) -> ANSWER -> sha256(ANSWER) -> AES key -> blob.
Enumerate {alphabet x a-i mapping x escapes x transposition x over-encryption} and
verify ONLY via the real signal: does sha256(answer) open the SalPhaseIon/Cosmic blob.
The English score is NOT trusted (verification problem); the AES open is the oracle."""
import base64, hashlib, itertools, re
from Crypto.Cipher import AES

dbbi="dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"

# ---- blobs (the verifier) ----
def load(p):
    b=base64.b64decode("".join(open(p).read().split())); return b[8:16],b[16:]
BLOBS={"SALPH":load("salphaseion_blob.txt"),"COSMIC":load("cosmic_blob.txt")}
def evp(pw,salt,kl=32,il=16):
    d=b"";pr=b""
    while len(d)<kl+il: pr=hashlib.sha256(pr+pw+salt).digest(); d+=pr
    return d[:kl],d[kl:kl+il]
def aes_open(keystr):
    """keystr is the openssl -pass string. Return plaintext if valid+printable."""
    for tag,(salt,ct) in BLOBS.items():
        k,iv=evp(keystr.encode(),salt)
        pt=AES.new(k,AES.MODE_CBC,iv).decrypt(ct); p=pt[-1]
        if 1<=p<=16 and pt[-p:]==bytes([p])*p:
            b=pt[:-p]
            if b and sum(1 for c in b if 32<=c<127 or c in(9,10,13))/len(b)>0.85:
                return tag,b
    return None

# ---- checkerboard decode ----
def cb_decode(digits, alpha28, e1, e2):
    e1,e2=sorted((e1,e2))
    top=[c for c in range(10) if c not in (e1,e2)]
    bd={}
    for k,c in enumerate(top): bd[str(c)]=alpha28[k]
    for c in range(10): bd[f"{e1}{c}"]=alpha28[8+c]
    for c in range(10): bd[f"{e2}{c}"]=alpha28[18+c]
    out=[];i=0
    while i<len(digits):
        d=int(digits[i])
        if d in (e1,e2):
            if i+1>=len(digits): break
            out.append(bd.get(digits[i:i+2],'?')); i+=2
        else: out.append(bd.get(digits[i],'?')); i+=1
    return "".join(out)

def pad28(seed):
    s="".join(dict.fromkeys(re.sub(r'[^A-Za-z]','',seed).upper()))
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if ch not in s: s+=ch
    s=s[:26]; return s[:8]+"."+s[8:17]+"."+s[17:26]

# ---- transposition ----
def key_order(key): return [i for i,_ in sorted(enumerate(key),key=lambda x:(x[1],x[0]))]
def col_decrypt(c,key):
    w=len(key);n=len(c);order=key_order(key);nr=-(-n//w);rem=n%w
    cl={x:(nr if(rem==0 or x<rem) else nr-1) for x in range(w)}
    cols={};pos=0
    for x in order: cols[x]=c[pos:pos+cl[x]];pos+=cl[x]
    return "".join(cols[x][r] for r in range(nr) for x in range(w) if r<len(cols[x]))

# ---- parameter candidates ----
ALPHAS={"322":"FUBCDORA.LETHINGKYMVPS.JQZXW"}
for kw in ["MATRIXSUMLIST","ENTER","LASTWORDSBEFOREARCHICHOICE","THISPASSWORD","THEMATRIXHASYOU",
           "THESEEDISPLANTED","FOLLOWTHEWHITERABBIT","YELLOWBLUEPRIME","CAUSALITY","",
           "THEWARNING","HASHTHETEXT","SALPHASEION","COSMICDUALITY","THEFLOWERBLOSSOMS"]:
    ALPHAS[kw or "PLAIN"]=pad28(kw)
MAPS={"a0i8":{c:i for i,c in enumerate("abcdefghi")},"a1i9":{c:i+1 for i,c in enumerate("abcdefghi")}}
ESCAPES=[(1,4),(2,5),(0,4)]
TRANSPOS={"none":lambda s:s,"rev":lambda s:s[::-1],
          "colMSL":lambda s:col_decrypt(s,"matrixsumlist")}
def seqkey(w):
    w=w.upper();o=sorted(range(len(w)),key=lambda i:(w[i],i));r=[0]*len(w)
    for k,i in enumerate(o): r[i]=k+1
    return r
OVERENC={"none":None,"mslseq":seqkey("MATRIXSUMLIST"),
         "shaflower":[int(c,16) for c in hashlib.sha256(b"theflowerblossomsthroughwhatseemstobeaconcretesurface").hexdigest()]}

def answer_forms(s):
    a=re.sub(r'[^A-Za-z]','',s)
    return {s, s.upper(), s.lower(), a, a.upper(), a.lower()}

tested=0;
print("[*] joint attack: decode(dbbi) -> sha256(answer) -> AES verify ...")
for an,alpha in ALPHAS.items():
    if len(alpha)!=28: continue
    for mn,mp in MAPS.items():
        for tn,tf in TRANSPOS.items():
            d2=tf(dbbi)
            base=[mp[c] for c in d2]
            for on,ov in OVERENC.items():
                for mod in ((9,10) if ov is not None else (10,)):
                    if ov is None:
                        digs="".join(str(x) for x in base)
                    else:
                        digs="".join(str((base[i]-ov[i%len(ov)])%mod) for i in range(len(base)))
                    for e1,e2 in ESCAPES:
                        ans=cb_decode(digs,alpha,e1,e2)
                        if '?' in ans: continue
                        for form in answer_forms(ans):
                            tested+=1
                            # try sha256(answer)-hex as pass, and answer raw as pass
                            for keystr in (hashlib.sha256(form.encode()).hexdigest(), form):
                                r=aes_open(keystr)
                                if r:
                                    print(f"\n[+++ SOLVED {r[0]}] alpha={an} map={mn} trans={tn} over={on} mod={mod} esc={e1}{e2}")
                                    print(f"    answer={ans!r}\n    form={form!r}\n    plaintext={r[1][:200]!r}")
print(f"\n[*] done. tested {tested} decode-forms against AES. (no SOLVED line above = no hit)")
