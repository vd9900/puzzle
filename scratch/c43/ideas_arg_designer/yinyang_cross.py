"""Yin-yang cross-seeding: each half holds the seed of its opposite -> each blob keyed by the OTHER textarea's visible
content. Small, derivation-bound candidate set; oracle = PKCS7 + structured plaintext (printable>=0.9 or 64-hex)."""
import sys, hashlib, base64, re
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
A=tas[0]; B=tas[1]
cosmic_lines=B.strip('\n')
forms_cosmic={'raw':B,'strip':B.strip(),'b64_nl':cosmic_lines,'b64_nl_trail':cosmic_lines+'\n','b64_flat':COSMIC_B64,
  'ct_hex':COSMIC_CT.hex(),'salt_hex':COSMIC_SALT.hex(),'all_hex':base64.b64decode(COSMIC_B64).hex()}
small_nl=SMALL_B64[:64]+'\n'+SMALL_B64[64:]
forms_salph={'raw':A,'compact':compact,'compact_noblob':compact.split('U2FsdGVkX1')[0],'b64_nl':small_nl,'b64_nl_trail':small_nl+'\n',
  'b64_flat':SMALL_B64,'b64_with_enter':SMALL_B64[:64]+BIN2+SMALL_B64[64:],'ct_hex':SMALL_CT.hex(),'salt_hex':SMALL_SALT.hex(),
  'dbbi':DBBI,'faed':FAED,'dbbi+faed':DBBI+FAED,'all_hex':base64.b64decode(SMALL_B64).hex()}
forms_inner={'b64_nl':INNER_B64[:64]+'\n'+INNER_B64[64:],'b64_flat':INNER_B64,'ct_hex':INNER_CT.hex(),'salt_hex':INNER_SALT.hex()}
def variants(s):
    b=s.encode()
    yield 'sha256hex', hashlib.sha256(b).hexdigest()
    yield 'sha256hex_nl', hashlib.sha256(b+b'\n').hexdigest()
    yield 'literal', s
n=0; hits=[]
for src,forms in (('cosmic',forms_cosmic),('salph',forms_salph),('inner',forms_inner)):
    for fk,fv in forms.items():
        for vk,pw in variants(fv):
            for h in try_pw(pw):
                if h[0]==src: continue
                n+=1
                pt=h[2]; pr=printable_ratio(pt)
                flag = pr>=0.9 or re.fullmatch(rb'[0-9a-f]{64}\s*',pt)
                print('PADOK',src,fk,vk,'->',h[0],h[1],len(pt),'%.2f'%pr,'STRUCTURED' if flag else '')
                if flag: hits.append((src,fk,vk,h))
print('pad-valid (expected ~1/256 per trial):',n,'structured hits:',len(hits))
# positive control: phase-2 style check of try_pw machinery on a synthetic blob
import os
from Crypto.Cipher import AES
salt=os.urandom(8); pw=hashlib.sha256(COSMIC_B64.encode()).hexdigest().encode(); k,iv=evp(pw,salt)
msg=b'0'*64; pad=16-len(msg)%16; ct=AES.new(k,AES.MODE_CBC,iv).encrypt(msg+bytes([pad])*pad)
BLOBS['plant']=(salt,ct)
print('control plant found:', any(h[0]=='plant' for h in try_pw(pw)))
