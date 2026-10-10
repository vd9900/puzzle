"""Custom check for claimed hex keys: (a) raw 32/16 bytes as the OpenSSL password (EVP sha256 & md5), (b) hex bytes as direct AES-256 key with IV in {zero, salt||salt, key[:16]}.
Hit criterion: valid PKCS7 pad AND printable>0.8 (or Salted__ marker). Padding-only hits are reported as counts only."""
import sys, hashlib, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import BLOBS, evp, printable_ratio
from Crypto.Cipher import AES
hexes = [l.strip() for l in open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_web_osint.txt') if re.fullmatch(r'[0-9a-fA-F]{16,}\s*', l) and len(l.strip()) % 2 == 0]
print('hex candidates', len(hexes))
def pad_ok(pt):
    p = pt[-1]; return 1 <= p <= 16 and pt.endswith(bytes([p]) * p)
pad_only = 0; hits = []
for h in hexes:
    raw = bytes.fromhex(h)
    for name, (salt, ct) in BLOBS.items():
        trials = []
        for dg in ('sha256', 'md5'):
            k, iv = evp(raw, salt, dg); trials.append((f'rawpw-{dg}', k, iv))
        if len(raw) == 32:
            for ivn, iv in (('iv0', bytes(16)), ('ivsalt2', salt + salt), ('ivkey16', raw[:16])):
                trials.append((f'directkey-{ivn}', raw, iv))
        for tag, k, iv in trials:
            pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
            if pad_ok(pt):
                body = pt[:-pt[-1]]
                if printable_ratio(body) > 0.8 or b'Salted__' in body or b'U2FsdGVk' in body:
                    hits.append((h[:16], name, tag, body[:60])); print('!!! STRUCTURED HIT', h[:16], name, tag, body[:60])
                else: pad_only += 1
            elif len(raw) == 32 and tag.startswith('directkey') and printable_ratio(pt[:16]) > 0.9:
                print('note: printable first block (no pad)', h[:16], name, tag, pt[:32])
print('structured hits', len(hits), 'padding-only', pad_only)
