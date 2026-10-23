"""Feasibility + quick run: faed (head 538/539/540, full 570; fwd/rev) read by the puzzle's own z-method
(letters a..i=1..9, g in {0,7}, ONE big decimal integer -> big-endian bytes) as a BINARY payload of 32-byte scalars.
(A) top 32-byte slice: every g that can influence it is enumerated exhaustively; lower g's only shift it by a carry,
    bounded exactly by evaluating the lower part at all-0 and all-7. Oracle: x-coordinate of k*G == prize x (covers n-k).
(B) deterministic zero rules (all 0, all 7, prime-position zeroing 0/1-based and inverse, colour-sequence zeroing of the
    1-based-prime g's): every 32-byte window at every byte offset of the payload.
Planted control first. Uses system libsecp256k1 via ctypes."""
import sys, ctypes, secrets, time
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, primes_upto
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
PRIZE_X = bytes.fromhex('f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464')
lib = ctypes.CDLL('libsecp256k1.so.1'); lib.secp256k1_context_create.restype = ctypes.c_void_p
ctx = ctypes.c_void_p(lib.secp256k1_context_create(0x201))
pub = ctypes.create_string_buffer(64); out = ctypes.create_string_buffer(33); ol = ctypes.c_size_t(33)
def xof(k):
    k %= N
    if k == 0: return None
    if lib.secp256k1_ec_pubkey_create(ctx, pub, k.to_bytes(32, 'big')) != 1: return None
    ol.value = 33; lib.secp256k1_ec_pubkey_serialize(ctx, out, ctypes.byref(ol), pub, 0x102)
    return out.raw[1:33]
V = {c: i + 1 for i, c in enumerate('abcdefghi')}
def top_slice_scan(s, target_x, label):
    L = len(s); gpos = [i for i, c in enumerate(s) if c == 'g']
    base = int(''.join('0' if c == 'g' else str(V[c]) for c in s))
    nbytes = (int(''.join('7' if c == 'g' else str(V[c]) for c in s)).bit_length() + 7) // 8
    nb0 = (base.bit_length() + 7) // 8
    hits = []; tested = 0
    for nb in sorted({nb0, nbytes}):
        sh = 8 * (nb - 32)
        # choose h: g's with index < h enumerated; the rest bounded
        for h in range(1, L + 1):
            low = [p for p in gpos if p >= h]
            span = sum(7 * 10 ** (L - 1 - p) for p in low)
            if (span >> sh) <= 1: break
        hi = [p for p in gpos if p < h]
        W = [7 * 10 ** (L - 1 - p) for p in hi]; lowspan = sum(7 * 10 ** (L - 1 - p) for p in gpos if p >= h)
        for m in range(1 << len(hi)):
            v = base + sum(W[j] for j in range(len(hi)) if m >> j & 1)
            ks = set(range(v >> sh, ((v + lowspan) >> sh) + 1))
            for k in ks:
                if k >> 256: continue
                tested += 1
                if xof(k) == target_x: hits.append((nb, m, k))
        print(f'  [{label}] bytes={nb} enumerated g={len(hi)} (h={h}) keys={tested} hits={len(hits)}')
    return hits
if __name__ == '__main__':
    # planted control: build a fake 538-letter string whose top slice is a known key, with g's in it
    t0 = time.time()
    k = secrets.randbelow(N); kx = xof(k)
    for _ in range(100):
        tail_digits = ''.join(secrets.choice('0123456789') for _ in range(538 - 0))
        n = (k << 1536) | int.from_bytes(secrets.token_bytes(192), 'big')
        d = str(n)
        if len(d) == 538: break
    fake = ''.join('g' if ch in '07' else 'abcdefghi'[int(ch) - 1] for ch in d)
    h = top_slice_scan(fake, kx, 'PLANT')
    assert any(x[2] == k for x in h), 'planted control FAILED'
    print('planted control OK', round(time.time() - t0, 1), 's')
    allhits = []
    for nm, s in (('head538', FAED[:538]), ('head539', FAED[:539]), ('head540', FAED[:540]), ('full570', FAED),
                  ('rev570', FAED[::-1]), ('rev_head538', FAED[:538][::-1])):
        allhits += [(nm,) + x for x in top_slice_scan(s, PRIZE_X, nm)]
    # (B) deterministic rules, every 32-byte window
    PR = set(primes_upto(1000)); colour = [int(b) for b in format(int.from_bytes(b'gsmg.io/theseedisplanted', 'big'), '0192b')[7::8]]
    assert sum(colour) == 15 and len(colour) == 24
    def rule_digits(s, rule):
        out = []; ci = 0
        for i, c in enumerate(s):
            if c != 'g': out.append(str(V[c])); continue
            if rule == 'g0': out.append('0')
            elif rule == 'g7': out.append('7')
            elif rule in ('p1', 'p1inv', 'p0', 'p0inv'):
                b = 1 if rule[1] == '1' else 0; isp = (i + b) in PR
                out.append(('0' if isp else '7') if not rule.endswith('inv') else ('7' if isp else '0'))
            elif rule in ('col', 'colinv'):
                if (i + 1) in PR and ci < 24:
                    bit = colour[ci]; ci += 1
                    out.append(('7' if bit else '0') if rule == 'col' else ('0' if bit else '7'))
                else: out.append('7')
        return ''.join(out)
    nB = 0; hitsB = []
    for nm, s in (('head538', FAED[:538]), ('full570', FAED), ('rev570', FAED[::-1])):
        for rule in ('g0', 'g7', 'p1', 'p1inv', 'p0', 'p0inv', 'col', 'colinv'):
            v = int(rule_digits(s, rule)); b = v.to_bytes((v.bit_length() + 7) // 8, 'big')
            for bb in (b, b[::-1]):
                for o in range(0, len(bb) - 31):
                    nB += 1
                    if xof(int.from_bytes(bb[o:o + 32], 'big')) == PRIZE_X: hitsB.append((nm, rule, o))
    print('(B) deterministic-rule windows tested', nB, 'hits', hitsB)
    print('(A) hits', allhits)
