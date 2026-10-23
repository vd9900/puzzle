"""H: faed head (538/539 letters, before the e/g-free tail) = z-method (one decimal integer -> big-endian bytes) of
224 bytes = 7 x 32 bytes = seven sha256 digests ('seven intertwined passwords'; every chain password is a sha256 digest).
The TOP digest depends only on the first ~76 letters (17 g's) + a carry, so all 2^17 g-resolutions are enumerated.
Oracle: digest-hex as password on small/inner/cosmic blobs (EVP sha256/md5), PKCS7 valid + structured plaintext;
and equality with sha256 of the known chain answers. Planted control first. (c42 linguist ran only g=7, 540 letters.)"""
import sys, time, hashlib, secrets, functools, builtins
print = functools.partial(builtins.print, flush=True)
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, BLOBS, evp, printable_ratio
from Crypto.Cipher import AES
V = {c: i + 1 for i, c in enumerate('abcdefghi')}
def top_candidates(s, nbytes=224):
    L = len(s); gpos = [i for i, c in enumerate(s) if c == 'g']
    base = int(''.join('0' if c == 'g' else str(V[c]) for c in s)); sh = 8 * (nbytes - 32)
    for h in range(1, L + 1):
        if (sum(7 * 10 ** (L - 1 - p) for p in gpos if p >= h) >> sh) <= 1: break
    hi = [p for p in gpos if p < h]; W = [7 * 10 ** (L - 1 - p) for p in hi]
    lowspan = sum(7 * 10 ** (L - 1 - p) for p in gpos if p >= h)
    out = set()
    for m in range(1 << len(hi)):
        v = base + sum(W[j] for j in range(len(hi)) if m >> j & 1)
        for k in range(v >> sh, ((v + lowspan) >> sh) + 1):
            if k < (1 << 256): out.add(k)
    return out, len(hi)
PREP = [(n, salt, ct[-32:-16], ct[-16:], ct) for n, (salt, ct) in BLOBS.items()]
def check(pw):
    pb = pw.encode(); hits = []
    for n, salt, ivl, last, ct in PREP:
        for d in ('sha256', 'md5'):
            k, iv = evp(pb, salt, d)
            p = AES.new(k, AES.MODE_CBC, ivl).decrypt(last); pad = p[-1]
            if 1 <= pad <= 16 and p.endswith(bytes([pad]) * pad):
                full = AES.new(k, AES.MODE_CBC, iv).decrypt(ct); body = full[:-pad]
                if printable_ratio(body) > 0.85 or b'Salted__' in body: hits.append((n, d, body[:60]))
    return hits
KNOWN = ['causality', 'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple', 'theseedisplanted',
         'gsmg.io/theseedisplanted', 'matrixsumlist', 'lastwordsbeforearchichoice', 'thispassword', 'enter',
         'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe', 'shabefourfirsthintisyourlastcommand', 'shabefanstoo']
KD = {int.from_bytes(hashlib.sha256(x.encode()).digest(), 'big'): x for x in KNOWN}
if __name__ == '__main__':
    # planted control: top digest = sha256('causality') hidden under g's -> must be in candidate set and open phase-2-like check
    t = int.from_bytes(hashlib.sha256(b'causality').digest(), 'big')
    t >>= 4  # keep the planted 224-byte number at 538-539 digits (top digest gets leading zero nibble)
    n = (t << 1536) | int.from_bytes(secrets.token_bytes(192), 'big'); d = str(n); print('plant digits', len(d))
    fake = ''.join('g' if ch in '07' else 'abcdefghi'[int(ch) - 1] for ch in d)
    cs, ng = top_candidates(fake); assert t in cs, 'plant failed'; print('planted control OK: digest recovered among', len(cs), 'cands, g enumerated', ng)
    t0 = time.time(); tot = 0; hits = []
    for nm, s in (('head538', FAED[:538]), ('head539', FAED[:539]), ('rev_head538', FAED[:538][::-1])):
        cs, ng = top_candidates(s)
        kn = [KD[k] for k in cs if k in KD]
        print(nm, 'cands', len(cs), 'g', ng, 'known-digest matches', kn)
        for k in cs:
            tot += 1
            hx = k.to_bytes(32, 'big').hex()
            r = check(hx)
            if r: hits.append((nm, hx, r)); print('HIT', nm, hx, r)
    print('passwords tested', tot, 'structured hits', len(hits), 'time', round(time.time() - t0, 1))
