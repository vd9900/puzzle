import hashlib, base64, re, html, json
from pathlib import Path
from Crypto.Cipher import AES
from collections import Counter

ROOT = Path('/home/vin/bitcoin_puzzle')
SRC = ROOT/'research'/'sources'

doc = (SRC/'salphaseion.html').read_text()
tas = [html.unescape(c) for c in re.findall(r"<textarea\b[^>]*>(.*?)</textarea>", doc, re.S|re.I)]
compact = ''.join(tas[0].split())
DBBI = compact[:91]
BIN1 = compact[91:91+104]
FAED = compact[195:195+570]
rest = compact[765:]
assert DBBI.startswith('dbbi') and FAED.startswith('faed') and rest.startswith('z')
before, tail = rest.split('U2FsdGVkX1',1)
parts = before.split('z')
assert parts[0]=='' and len(parts)==4, parts
Z1, Z2, Z3 = parts[1], parts[2], parts[3]
pre = Z3
SMALL_B64 = 'U2FsdGVkX1'+tail.split('shabef')[0]
BIN2 = re.findall(r'[ab]{16,}', SMALL_B64)[0]
SMALL_B64 = SMALL_B64.replace(BIN2,'',1)
COSMIC_B64 = ''.join(tas[1].split())

def b2a(s):
    bits = s.translate(str.maketrans('ab','01'))
    return bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8)).decode()

def zmethod_digits(digits):
    n = int(digits)
    h = hex(n)[2:]
    if len(h)%2: h='0'+h
    return bytes.fromhex(h)

def letters_to_digits(s, zero='o'):
    return s.translate(str.maketrans('abcdefghi'+zero, '1234567890'))

assert b2a(BIN1)=='matrixsumlist' and b2a(BIN2)=='enter'
assert zmethod_digits(letters_to_digits(Z1))==b'lastwordsbeforearchichoice'
assert zmethod_digits(letters_to_digits(Z2))==b'thispassword'

def parse_salted(b64):
    p = base64.b64decode(b64)
    assert p[:8]==b'Salted__'
    return p[8:16], p[16:]

SMALL_SALT, SMALL_CT = parse_salted(SMALL_B64)
COSMIC_SALT, COSMIC_CT = parse_salted(COSMIC_B64)
# phase 3.2 inner blob
INNER_B64 = ('U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46z'
             'gKlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4')
INNER_SALT, INNER_CT = parse_salted(INNER_B64)
BLOBS = {'small':(SMALL_SALT,SMALL_CT),'inner':(INNER_SALT,INNER_CT),'cosmic':(COSMIC_SALT,COSMIC_CT)}

def evp(password, salt, digest='sha256'):
    m=b''; prev=b''
    while len(m)<48:
        prev=hashlib.new(digest, prev+password+salt).digest(); m+=prev
    return m[:32], m[32:48]

def try_pw(password, which='all', digests=('sha256','md5')):
    """returns list of (blob, digest, plaintext) with valid pkcs7 padding"""
    if isinstance(password,str): password=password.encode()
    hits=[]
    for name,(salt,ct) in BLOBS.items():
        if which!='all' and name!=which: continue
        for d in digests:
            k,iv = evp(password,salt,d)
            pt = AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
            pad = pt[-1]
            if 1<=pad<=16 and pt.endswith(bytes([pad])*pad):
                hits.append((name,d,pt[:-pad]))
    return hits

def printable_ratio(b):
    return sum(32<=c<127 for c in b)/max(1,len(b))

def sha256hex(s):
    if isinstance(s,str): s=s.encode()
    return hashlib.sha256(s).hexdigest()

def test_candidates(cands, label=''):
    """cands: iterable of (desc, password_str). tries raw, sha256hex. Reports structured hits."""
    n=0; good=[]
    for desc,pw in cands:
        for form,p in (('raw',pw),('sha256',sha256hex(pw))):
            n+=1
            for name,d,pt in try_pw(p):
                pr=printable_ratio(pt)
                if pr>0.85 or b'Salted__' in pt or b'U2FsdGVk' in pt:
                    good.append((desc,form,name,d,pt))
                    print('!!! STRUCTURED HIT', desc, form, name, d, pt[:80])
    print(f'[{label}] tried {n} password forms; structured hits: {len(good)}')
    return good

MATRIX = [[int(x) for x in r.split()] for r in """0 0 1 1 0 1 0 0 1 0 1 1 0 0
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
0 1 1 0 1 1 0 1 1 0 1 0 1 1""".splitlines()]

def primes_upto(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**.5)+1):
        if s[i]:
            for j in range(i*i,n+1,i): s[j]=False
    return [i for i in range(n+1) if s[i]]

if __name__=='__main__':
    print('DBBI',len(DBBI),DBBI)
    print('FAED',len(FAED))
    print('Z3 pre-blob text:', pre)
    print('after blob:', tail.split('shabef',1)[1] if 'shabef' in tail else None)
    for n,(s,c) in BLOBS.items(): print(n, s.hex(), len(c))
    print('dbbi freq', Counter(DBBI).most_common())
    print('faed freq', Counter(FAED).most_common())
