"""'Sal-Phase-Ion' = salt phase: are openssl salts deliberate (-S <hash prefix>)? Compare each blob salt (incl. solved
Phase 3 blob as control) with the first/last 8 bytes of sha256/md5/sha1 of every string in the local corpora + ledger.
A 64-bit match is self-verifying (false-positive ~2^-64 per comparison)."""
import sys, hashlib, json, re, glob
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import BLOBS
salts = {n: s for n, (s, c) in BLOBS.items()}; salts['phase3'] = bytes.fromhex('eefc4c5befc1656a')
strings = set()
for f in glob.glob('/home/vin/bitcoin_puzzle/scratch/corpora/*.txt') + glob.glob('/home/vin/bitcoin_puzzle/scratch/wf/cands_*.txt'):
    for line in open(f, errors='replace'):
        line = line.strip()
        if not line or len(line) > 300: continue
        strings.add(line); strings.add(line.lower()); strings.add(re.sub(r'[^a-z0-9]', '', line.lower()))
        for w in re.findall(r'[A-Za-z0-9]{3,}', line): strings.add(w); strings.add(w.lower())
for l in open('/home/vin/bitcoin_puzzle/research/candidates.jsonl'):
    for v in json.loads(l).values():
        if isinstance(v, str) and len(v) < 300: strings.add(v)
print('strings', len(strings))
tgt = {}
for n, s in salts.items(): tgt[s] = n
hits = 0
for st in strings:
    b = st.encode('utf-8', 'surrogatepass')
    for alg in ('sha256', 'md5', 'sha1'):
        for x in (b, hashlib.sha256(b).hexdigest().encode()):
            d = hashlib.new(alg, x).digest()
            for part in (d[:8], d[-8:]):
                if part in tgt: hits += 1; print('!!! SALT MATCH', tgt[part], alg, st[:80])
    if b[:8] in tgt or bytes.fromhex(b.hex())[:8] in tgt: print('!!! literal', st)
print('salt hits', hits)
