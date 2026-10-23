"""Oracle-gap audit. Every prior AES sweep (scratch/oracle.py, common.try_pw/test_candidates) accepted a decryption only if
the body was >=80-85% printable or contained Salted__/U2FsdGVk; padding-only hits were discarded unlogged. A blob whose
plaintext is BINARY (two raw 32-byte keys 'half and better half', a 64-byte BIP39 seed / BIP32 I=IL||IR, a -nosalt inner
openssl layer, compressed data) would have been thrown away even for the right password.
Content-agnostic oracle: PKCS#7 pad length. Only the LAST block is decrypted (P_n = D_K(C_n) xor C_{n-1}; IV not needed).
pad>=4 has false-positive rate 2^-32 per trial; for the 80-B blobs pad==16 (64-B plaintext) is 2^-128.
Re-scores ONLY already-derived, stored candidate lists (no new candidates). Planted control first.
Usage: python3 padlen_rescore.py [nproc]"""
import sys, glob, hashlib, os, time
from multiprocessing import Pool
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import BLOBS
from Crypto.Cipher import AES
TARGETS = [(n, s, ct[-32:-16], ct[-16:]) for n, (s, ct) in BLOBS.items()]
def key_of(pw, salt, dg):
    if dg == 'sha256': return hashlib.sha256(pw + salt).digest()
    d1 = hashlib.md5(pw + salt).digest(); return d1 + hashlib.md5(d1 + pw + salt).digest()
def padlen(last):
    p = last[-1]
    return p if 1 <= p <= 16 and last.endswith(bytes([p]) * p) else 0
def score(pw, targets=TARGETS):
    out = []
    for n, s, prev, c in targets:
        for dg in ('sha256', 'md5'):
            last = bytes(a ^ b for a, b in zip(AES.new(key_of(pw, s, dg), AES.MODE_ECB).decrypt(c), prev))
            p = padlen(last)
            if p >= 3: out.append((n, dg, p))
    return out
def forms(c):
    fs = {c, c.lower(), c.strip(), c.lower().strip()}
    fs |= {hashlib.sha256(x.encode('utf-8', 'surrogatepass')).hexdigest() for x in list(fs)}
    return fs
def work(chunk):
    hits = []; n = 0
    for c in chunk:
        for f in forms(c):
            n += 1
            for h in score(f.encode('utf-8', 'surrogatepass')):
                hits.append((c[:100], f[:70]) + h)
    return n, hits
if __name__ == '__main__':
    # planted control: a 64-byte BINARY plaintext (two raw keys) under a known password must give pad==16
    salt = os.urandom(8); pw = hashlib.sha256(b'controlanswer').hexdigest().encode()
    k = hashlib.sha256(pw + salt).digest(); iv = hashlib.sha256(k + pw + salt).digest()[:16]
    ct = AES.new(k, AES.MODE_CBC, iv).encrypt(os.urandom(64) + bytes([16]) * 16)
    assert score(pw, [('plant', salt, ct[-32:-16], ct[-16:])]) == [('plant', 'sha256', 16)], 'control failed'
    print('planted binary-plaintext control OK (pad=16 detected)', flush=True)
    files = sorted(set(glob.glob('/home/vin/bitcoin_puzzle/scratch/wf/cands_*.txt') + glob.glob('/home/vin/bitcoin_puzzle/scratch/c3*/**/cands*.txt', recursive=True)
                       + glob.glob('/home/vin/bitcoin_puzzle/scratch/c4*/**/cands*.txt', recursive=True) + ['/home/vin/bitcoin_puzzle/scratch/c39/docs0/claimed_pw.txt']))
    cands = set()
    for f in files:
        for l in open(f, encoding='utf-8', errors='replace'):
            l = l.rstrip('\r\n')
            if l.strip() and not l.startswith('#'): cands.add(l)
    cands = sorted(cands); print(len(files), 'files,', len(cands), 'unique stored candidates', flush=True)
    t = time.time(); np_ = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    chunks = [cands[i:i + 5000] for i in range(0, len(cands), 5000)]
    tot = 0; allh = []
    with Pool(np_) as pool:
        for i, (n, h) in enumerate(pool.imap_unordered(work, chunks)):
            tot += n; allh += h
            if i % 20 == 0: print(f'  {i + 1}/{len(chunks)} chunks, {tot} pw forms, {len(allh)} pad>=3 events, {time.time() - t:.0f}s', flush=True)
    print(f'DONE {tot} password forms x 3 blobs x 2 KDFs = {tot * 6} trials in {time.time() - t:.0f}s')
    print(f'expected false positives: pad>=3 ~{tot * 6 / 2**24:.2f}, pad>=4 ~{tot * 6 / 2**32:.4f}')
    for h in sorted(allh, key=lambda r: -r[-1]): print('PAD>=3', h)
