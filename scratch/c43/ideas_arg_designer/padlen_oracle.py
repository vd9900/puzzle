"""Format-agnostic, splice-tolerant AES oracle (tier 1: re-score the curated ledger only; no new candidates).
HIT if (a) PKCS7 pad length >= 4 (chance 2^-32/trial; pad=16 <=> 64-byte plaintext: 64-hex, raw 64-byte BIP39 seed, 2 raw keys),
or (b) padding invalid but plaintext block 0 is 16 hex chars / 16 printable (tail-corruption tolerance),
or (c) pad-valid and blocks 0 and last-unpadded block hex/printable while block 1 is not (base64 index-63 'z' splice overwrite).
Plant controls: raw 64-byte seed; 64-hex with tail char substituted; 64-hex with index 63 overwritten by 'z'."""
import sys, json, hashlib, os, base64, re
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
from Crypto.Cipher import AES
HEX=re.compile(rb'[0-9a-fA-F]{16}')
def pr16(b): return all(32<=c<127 or c in (9,10,13) for c in b)
def score(pw, blobs):
    out=[]
    for name,(salt,ct) in blobs.items():
        for dg in ('sha256','md5'):
            k,iv=evp(pw,salt,dg); pt=AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
            p=pt[-1]; padok=1<=p<=16 and pt.endswith(bytes([p])*p)
            b0=pt[:16]
            if padok and p>=4: out.append((name,dg,'pad%d'%p))
            elif (not padok) and (HEX.fullmatch(b0) or pr16(b0)): out.append((name,dg,'b0-tolerant'))
            elif padok and pr16(b0) and len(pt)>=48 and pr16(pt[len(pt)-16-16:len(pt)-16]) and not pr16(pt[16:32]): out.append((name,dg,'splice63'))
    return out
# --- plant controls
def mk(msg, pw):
    salt=os.urandom(8); k,iv=evp(pw,salt); pad=16-len(msg)%16
    return salt, AES.new(k,AES.MODE_CBC,iv).encrypt(msg+bytes([pad])*pad)
def corrupt(salt,ct,idx,ch):
    b=base64.b64encode(b'Salted__'+salt+ct).decode(); 
    if b[idx]==ch: ch='A' if ch!='A' else 'B'
    raw=base64.b64decode(b[:idx]+ch+b[idx+1:]); return raw[8:16], raw[16:]
pw=b'plantpw'
ctl={'seed64':mk(os.urandom(64),pw)}
s,c=mk(os.urandom(32).hex().encode()+b'\r\n',pw); ctl['tail_sub']=corrupt(s,c,120,'Q')
s,c=mk(os.urandom(32).hex().encode()+b'\r\n',pw); ctl['z63']=corrupt(s,c,63,'z')
for n,v in ctl.items(): print('control',n,score(pw,{n:v}))
# --- tier 1: curated ledger strings only
cands=set()
for l in open('/home/vin/bitcoin_puzzle/research/candidates.jsonl'):
    j=json.loads(l)
    for v in j.values():
        if isinstance(v,str) and 0<len(v)<400: cands.add(v)
cands |= {Z1,Z2,Z3,'lastwordsbeforearchichoice','thispassword','shabefanstoo','matrixsumlist','enter','salphaseion','cosmicduality','yinyang'}
forms=set()
for c in cands:
    for x in (c, c.lower()): forms.add(x); forms.add(hashlib.sha256(x.encode()).hexdigest())
n=0; hits=[]
for f in forms:
    h=score(f.encode(),BLOBS); n+=1
    if h: hits.append((f[:70],h))
print('tier1 forms',len(forms),'x3 blobs x2 digests; hits',len(hits))
for h in hits[:20]: print('  ',h)
