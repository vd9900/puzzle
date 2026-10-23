"""Capacity-completion test: the prize key is a random 256-bit vanity key, so it must be stored verbatim; of the
unexplained page objects only faed (~1780 bits) and the three AES blobs can hold 256 bits (R60 ~190, tail ~106 bits).
If it is in faed as a decimal number (a..i=1..9, g=0|7: 'zeroed out', 'brute forcing might be required'), it sits in
SOME window of 75-78 letters. For every window (all offsets, fwd and reversed) every g-resolution is covered exactly by a
meet-in-the-middle on x-coordinates: x((base+sum_A)G) == x(PRIZE - sum_B G). Superset of the 7x77 partition test.
Planted control first. libsecp256k1 via ctypes."""
import sys, ctypes, secrets, time, functools, builtins
print = functools.partial(builtins.print, flush=True)
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
PRIZE = bytes.fromhex('04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559')
lib = ctypes.CDLL('libsecp256k1.so.1'); lib.secp256k1_context_create.restype = ctypes.c_void_p
ctx = ctypes.c_void_p(lib.secp256k1_context_create(0x301))
buf = ctypes.create_string_buffer(64); out = ctypes.create_string_buffer(33); ol = ctypes.c_size_t(33)
def ser():
    ol.value = 33; lib.secp256k1_ec_pubkey_serialize(ctx, out, ctypes.byref(ol), buf, 0x102); return out.raw[1:33]
def x_of_scalar(k):
    k %= N
    if k == 0 or lib.secp256k1_ec_pubkey_create(ctx, buf, k.to_bytes(32, 'big')) != 1: return None
    return ser()
def x_of_target_minus(tpub, k):
    k = (-k) % N
    ctypes.memmove(buf, tpub, 64)
    if k and lib.secp256k1_ec_pubkey_tweak_add(ctx, buf, k.to_bytes(32, 'big')) != 1: return None
    return ser()
def parse(pub65):
    p = ctypes.create_string_buffer(64); assert lib.secp256k1_ec_pubkey_parse(ctx, p, pub65, len(pub65)) == 1; return p.raw
def pub_of(k):
    lib.secp256k1_ec_pubkey_create(ctx, buf, (k % N).to_bytes(32, 'big')); u = ctypes.create_string_buffer(65); o = ctypes.c_size_t(65)
    lib.secp256k1_ec_pubkey_serialize(ctx, u, ctypes.byref(o), buf, 2); return u.raw
V = {c: i + 1 for i, c in enumerate('abcdefghi')}
def subsets(ws):
    acc = [0]
    for w in ws: acc = acc + [a + w for a in acc]
    return acc
def window(chunk, tpub):
    L = len(chunk); base = int(''.join('0' if c == 'g' else str(V[c]) for c in chunk))
    ws = [7 * 10 ** (L - 1 - p) for p, c in enumerate(chunk) if c == 'g']
    A, B = ws[:len(ws) // 2], ws[len(ws) // 2:]
    tab = {}
    for sa in subsets(A):
        x = x_of_scalar(base + sa)
        if x: tab.setdefault(x, []).append(sa)
    hits = []
    for sb in subsets(B):
        x = x_of_target_minus(tpub, sb)
        if x in tab:
            for sa in tab[x]:
                for k in (base + sa + sb, N - (base + sa + sb) % N):
                    if pub_of(k) == PRIZE_CHECK[0]: hits.append(k)
    return hits, len(ws)
PRIZE_CHECK = [None]
def scan(S, tpub, label, lens=(75, 76, 77, 78)):
    hits = []; ops = 0
    for L in lens:
        for o in range(0, len(S) - L + 1):
            h, ng = window(S[o:o + L], tpub); ops += (1 << (ng // 2)) + (1 << (ng - ng // 2))
            if h: hits.append((label, L, o, h)); print('HIT', label, L, o, h)
    return hits, ops
if __name__ == '__main__':
    t0 = time.time()
    # planted control: real-looking 570-letter string with a known key (77 digits) embedded at offset 300
    k = secrets.randbelow(10 ** 77 - 10 ** 76) + 10 ** 76
    rnd = ''.join(secrets.choice('0123456789') for _ in range(570)); d = rnd[:300] + str(k) + rnd[377:]
    fake = ''.join('g' if ch in '07' else 'abcdefghi'[int(ch) - 1] for ch in d)
    pp = pub_of(k); PRIZE_CHECK[0] = pp; tp = parse(pp)
    h, ops = scan(fake[290:390], tp, 'PLANT', lens=(77,))
    assert any(k in x[3] for x in h), 'plant failed'; print('planted control OK', h[0][:3], 'ops', ops, round(time.time() - t0, 1), 's')
    PRIZE_CHECK[0] = PRIZE; tp = parse(PRIZE); allh = []; tot = 0
    for label, S in (('fwd', FAED), ('rev', FAED[::-1])):
        h, ops = scan(S, tp, label); allh += h; tot += ops
        print(label, 'done ops', ops, 'hits', len(h), round(time.time() - t0, 1), 's')
    print('TOTAL point ops', tot, 'hits', allh)
