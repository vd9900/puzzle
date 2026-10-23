"""Implementation forensics of the creator's encryption 'software': collect every openssl blob in the sources,
decrypt the solved ones with their KNOWN passwords, and test whether salts are derived (not random):
salt == prefix/suffix of hash(password|answer|plaintext|previous salt) for sha256/md5/sha1, hex/raw.
Oracle: 8-byte equality (false-positive rate 2^-64 per comparison)."""
import sys, re, base64, hashlib, html
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import evp, BLOBS
from Crypto.Cipher import AES
from pathlib import Path
R = Path('/home/vin/bitcoin_puzzle/research')
texts = {}
for p in list((R/'sources').glob('*')) + list((R/'artifacts').glob('*.txt')) + list((R/'artifacts').glob('*.b64')):
    try: t = p.read_text(errors='ignore')
    except Exception: continue
    t = html.unescape(t).replace('\\n', '\n')
    for m in re.finditer(r'U2FsdGVkX1[A-Za-z0-9+/=\s]{20,}', t):
        b = ''.join(m.group(0).split())
        b = b[:len(b) - len(b) % 4]
        try: raw = base64.b64decode(b)
        except Exception: continue
        texts.setdefault(raw[8:16], (p.name, raw))
answers = ['causality', 'theseedisplanted', 'gsmg.io/theseedisplanted',
           'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple',
           'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe']
p3 = Path('/home/vin/bitcoin_puzzle/scratch/common.py')  # phase-3 7-part answer is in repo notes; grab any 'sha256' known pw lists
known_pw = {a: hashlib.sha256(a.encode()).hexdigest() for a in answers}
print('distinct salted blobs found:', len(texts))
solved = {}
for salt, (src, raw) in texts.items():
    ct = raw[16:]; ct = ct[:len(ct) - len(ct) % 16]
    for a, pw in known_pw.items():
        for d in ('sha256', 'md5'):
            k, iv = evp(pw.encode(), salt, d)
            pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
            if pt[-1] in range(1, 17) and pt.endswith(bytes([pt[-1]]) * pt[-1]) and sum(32 <= c < 127 or c in (9, 10, 13) for c in pt[:64]) > 60:
                solved[salt] = (a, pw, d, pt, src)
    print(src[:45].ljust(45), salt.hex(), 'ct', len(ct), 'SOLVED by ' + solved[salt][0][:30] if salt in solved else '')
H = {'sha256': hashlib.sha256, 'md5': hashlib.md5, 'sha1': hashlib.sha1, 'sha512': hashlib.sha512}
def derived(salt, material):
    out = []
    for mname, m in material:
        for hn, hf in H.items():
            for form, x in (('raw', m), ('hexstr', hf(m).hexdigest().encode())):
                d = hf(x).digest() if form == 'raw' else hf(m).hexdigest().encode()
                for pos in ('pre', 'suf'):
                    seg = d[:8] if pos == 'pre' else d[-8:]
                    if seg == salt: out.append((mname, hn, form, pos))
        if salt in m: out.append((mname, 'substring', '', ''))
    return out
allsalts = list(texts) + [v[0] for v in BLOBS.values()]
material = []
for a, pw in known_pw.items(): material += [('ans:' + a, a.encode()), ('pwhex:' + a, pw.encode())]
for s, (a, pw, d, pt, src) in solved.items(): material.append(('pt:' + a, pt))
for s in allsalts: material.append(('salt:' + s.hex(), s))
nhit = 0
for s in set(allsalts):
    mats = [mm for mm in material if mm[0] != 'salt:' + s.hex()]
    h = derived(s, mats)
    if h: nhit += 1; print('!!! salt', s.hex(), 'derived from', h)
print('salts checked', len(set(allsalts)), 'derivation hits', nhit)
