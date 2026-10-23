"""Zero-guess structural checks on the three blobs (protocol view):
1) XOR of the two 80-B ciphertexts (and full 96-B binaries / base64 texts): printable / hex / WIF structure?
2) 'Cosmic Duality' = two intertwined openssl blobs? search 'Salted__' in decoded bytes and 'U2FsdGVk' in the base64
   text, for every de-interleave stride 1..32 (char-level and line-level) and every phase.
3) repeated 16-byte ciphertext blocks within/between blobs (key+IV reuse signature)."""
import sys, base64, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import BLOBS, SMALL_B64, INNER_B64, COSMIC_B64, tas, printable_ratio
sb = base64.b64decode(SMALL_B64); ib = base64.b64decode(INNER_B64); cb = base64.b64decode(COSMIC_B64)
def struct(b):
    return printable_ratio(b), bool(re.fullmatch(rb'[0-9a-fA-F\s]+', b))
for nm, x in (('ct xor', bytes(a ^ b for a, b in zip(BLOBS['small'][1], BLOBS['inner'][1]))),
              ('full96 xor', bytes(a ^ b for a, b in zip(sb, ib))),
              ('b64text xor', bytes(ord(a) ^ ord(b) for a, b in zip(SMALL_B64, INNER_B64)))):
    print('1', nm, 'printable=%.2f hex=%s' % struct(x), x[:24].hex())
for off in range(0, len(cb) - 80 + 1, 16):
    for nm, other in (('small', BLOBS['small'][1]), ('inner', BLOBS['inner'][1])):
        x = bytes(a ^ b for a, b in zip(cb[off:off + 80], other))
        if printable_ratio(x) > 0.6: print('1b cosmic@%d xor %s printable %.2f' % (off, nm, printable_ratio(x)))
hits = []
lines = [l for l in tas[1].split('\n') if l.strip()]
for stride in range(1, 33):
    for ph in range(stride):
        s = COSMIC_B64[ph::stride]
        if 'U2FsdGVk' in s[1:] or (ph and 'U2FsdGVk' in s): hits.append(('char', stride, ph, s.index('U2FsdGVk')))
        try:
            d = base64.b64decode(s[:len(s) - len(s) % 4] + '')
            if b'Salted__' in d[1:] or (ph and b'Salted__' in d): hits.append(('charbytes', stride, ph))
        except Exception: pass
        ls = ''.join(lines[ph::stride]) if stride <= len(lines) else ''
        if ls and ('U2FsdGVk' in ls[1:] or (ph and ls.startswith('U2FsdGVk'))): hits.append(('line', stride, ph))
print('2 extra openssl headers inside Cosmic (any stride/phase):', hits if hits else 'none', '| lines:', len(lines), set(map(len, lines)))
print('2b Salted__ anywhere after offset 0 in decoded cosmic:', cb.find(b'Salted__', 1))
blocks = {}
for nm, (salt, ct) in BLOBS.items():
    for i in range(0, len(ct), 16): blocks.setdefault(ct[i:i + 16], []).append((nm, i // 16))
print('3 repeated ct blocks:', [v for v in blocks.values() if len(v) > 1] or 'none')
