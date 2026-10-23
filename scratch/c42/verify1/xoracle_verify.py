#!/usr/bin/env python3
"""Cycle 42 verify1: independent x-coordinate oracle vs the revealed prize public key.
For every derived scalar k (small derivation-backed core set) test k, 2k, k/2 (mod n); matching only the x-coordinate also
covers n-k, n-2k, n-k/2. Controls: planted random key, chain control (sha256('causality') -> 1Jqq37...), and a
same-breadth negative control (random targets looked up against the same x-table). Scalar multiplication uses the
`cryptography` package; a sample is cross-checked against the system libsecp256k1 via ctypes.
Usage: python3 xoracle_verify.py"""
import sys, re, json, hashlib, itertools, secrets, time, ctypes
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED  # puzzle data only
from cryptography.hazmat.primitives.asymmetric import ec

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 2**256 - 2**32 - 977
INV2 = pow(2, -1, N)
PRIZE_ADDR = '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
SECOND_ADDR = '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
PUB_UNC = ('04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559')
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58check(payload):
    data = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    n = int.from_bytes(data, 'big'); s = ''
    while n: n, r = divmod(n, 58); s = B58[r] + s
    return '1' * (len(data) - len(data.lstrip(b'\0'))) + s

def p2pkh(enc):
    return b58check(b'\0' + hashlib.new('ripemd160', hashlib.sha256(enc).digest()).digest())

def addrs_xy(x, y):
    xb = x.to_bytes(32, 'big')
    return {p2pkh(bytes([2 + (y & 1)]) + xb), p2pkh(b'\x04' + xb + y.to_bytes(32, 'big'))}

def mul(k):
    pn = ec.derive_private_key(k, ec.SECP256K1()).public_key().public_numbers()
    return pn.x, pn.y

# ---------------- target sanity
TX, TY = int(PUB_UNC[2:66], 16), int(PUB_UNC[66:], 16)
assert (TY * TY - TX ** 3 - 7) % P == 0, 'prize pubkey not on curve'
assert PRIZE_ADDR in addrs_xy(TX, TY), 'prize pubkey does not hash to prize address'
print('prize pubkey on curve and hashes to', PRIZE_ADDR, '(uncompressed)' if p2pkh(bytes.fromhex(PUB_UNC)) == PRIZE_ADDR else '(compressed)')

# ---------------- libsecp256k1 cross-check helper
lib = ctypes.CDLL('libsecp256k1.so.1')
lib.secp256k1_context_create.restype = ctypes.c_void_p
ctx = ctypes.c_void_p(lib.secp256k1_context_create(0x201))
def mul_lib(k):
    pub = ctypes.create_string_buffer(64); out = ctypes.create_string_buffer(65); ol = ctypes.c_size_t(65)
    assert lib.secp256k1_ec_pubkey_create(ctx, pub, k.to_bytes(32, 'big')) == 1
    lib.secp256k1_ec_pubkey_serialize(ctx, out, ctypes.byref(ol), pub, 2)
    return int.from_bytes(out.raw[1:33], 'big'), int.from_bytes(out.raw[33:65], 'big')

# ---------------- core derivation-backed candidate set
sha = lambda b: hashlib.sha256(b).digest()
art = '/home/vin/bitcoin_puzzle/research/artifacts/'
speech = open(art + 'phase32-beaufort.txt').read().strip()
message = open(art + 'phase32-checkerboard.txt').read().strip()
PHASE3 = ('causalitySafenetLunaHSM11110'
          '0x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F'
          '20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854'
          'B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1')
PHASE32 = 'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple'
SALPH = 'GSMGIO5BTCPUZZLECHALLENGE' + PRIZE_ADDR
STRINGS = ['gsmg.io/theseedisplanted', 'theseedisplanted', 'theflowerblossomsthroughwhatseemstobeaconcretesurface',
           'choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself',
           'causality', PHASE3, PHASE32, SALPH, 'thematrixhasyou', 'matrixsumlist', 'enter', 'lastwordsbeforearchichoice',
           'thispassword', 'shabefourfirsthintisyourlastcommand', 'ourfirsthintisyourlastcommand', 'shabefanstoo',
           'halfandbetterhalf', 'half', 'betterhalf', 'yinyang', 'cosmicduality', 'yellowblueprimes',
           'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist',
           'matrixsumlistlastwordsbeforearchichoicethispassword', speech, message, speech[-len('ciaobellao'):]]
scalars = {}  # k -> label
def add(k, label):
    k %= N
    if k and k not in scalars: scalars[k] = label
for s in STRINGS:
    for f in {s, s.lower(), re.sub(r'[^a-z0-9]', '', s.lower())}:
        if not f: continue
        h = sha(f.encode())
        add(int.from_bytes(h, 'big'), f'sha256({f[:40]!r})')
        add(int.from_bytes(sha(h), 'big'), f'sha256d({f[:40]!r})')
        add(int.from_bytes(sha(h.hex().encode()), 'big'), f'sha256(hex)({f[:40]!r})')
# seven_pw T2 reimplemented: sums / xors of the 7 stage-password digests over all subsets of size>=2
P7 = ['theseedisplanted', 'theflowerblossomsthroughwhatseemstobeaconcretesurface',
      'choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself',
      'causality', PHASE32, 'thematrixhasyou', SALPH]
H7 = [int.from_bytes(sha(p.encode()), 'big') for p in P7]
for r in range(2, 8):
    for sub in itertools.combinations(range(7), r):
        x = 0
        for i in sub: x ^= H7[i]
        add(sum(H7[i] for i in sub), f'sum7{sub}'); add(x, f'xor7{sub}')
# ec_remainder_sum reimplemented
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
v = lambda s: int(''.join(str(ord(c) - 96) for c in s))
objs = {'dbbi': v(DBBI), 'R60': v(R60), 'faed': v(FAED), 'faedA': v(FAED[:285]), 'faedB': v(FAED[285:]),
        'dbbi_rev': v(DBBI[::-1]), 'faed_rev': v(FAED[::-1])}
for k_, x_ in objs.items(): add(x_ % N, k_ + '%n'); add(x_ % P, k_ + '%p')
for a, b in [('dbbi', 'faed'), ('R60', 'faed'), ('faedA', 'faedB'), ('dbbi', 'R60'), ('dbbi_rev', 'faed_rev')]:
    add(objs[a] + objs[b], f'{a}+{b}'); add(objs[a] - objs[b], f'{a}-{b}'); add(objs[a] * objs[b], f'{a}*{b}')
# 64-hex tokens in research/candidates.jsonl
toks = sorted(set(m.lower() for m in re.findall(r'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])',
                                                open('/home/vin/bitcoin_puzzle/research/candidates.jsonl').read())))
for t in toks: add(int(t, 16), 'cands.jsonl:' + t[:16])
print('core scalars', len(scalars), '(jsonl hex tokens', len(toks), ')')

# ---------------- build x-table for k, 2k, k/2; also address check of +-Q against both prize addresses
TF = {'id': lambda k: k, 'dbl(2k)': lambda k: 2 * k % N, 'half(k/2)': lambda k: k * INV2 % N}
def build(scs):
    xt = {}; addr_hits = []
    for k, lab in scs.items():
        for tn, f in TF.items():
            t = f(k); x, y = mul(t)
            xt.setdefault(x, []).append((lab, tn))
            a = addrs_xy(x, y) | addrs_xy(x, P - y)
            for A in (PRIZE_ADDR, SECOND_ADDR, '1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ'):
                if A in a: addr_hits.append((A, lab, tn))
    return xt, addr_hits
t0 = time.time(); XT, AH = build(scalars); dt = time.time() - t0
print(f'x-table entries {sum(map(len, XT.values()))} distinct x {len(XT)} in {dt:.1f}s')
# cross-check a sample against libsecp256k1
samp = list(scalars)[:200]
assert all(mul(k) == mul_lib(k) for k in samp), 'cryptography vs libsecp256k1 mismatch'
print('libsecp256k1 cross-check OK on', len(samp), 'scalars')

res = {}
# ---------------- MAIN: prize x lookup
main_hits = XT.get(TX, [])
main_addr = [h for h in AH if h[0] in (PRIZE_ADDR, SECOND_ADDR)]
res['main_x_hits'] = main_hits; res['main_addr_hits'] = main_addr
print('MAIN prize-x hits:', main_hits, '| prize/secondary address hits:', main_addr)

# ---------------- CONTROL 1: chain control, sha256('causality') must be found in all transforms
c = int.from_bytes(sha(b'causality'), 'big')
ctl = {}
for name, tgt in (('pub(c)', c), ('pub(n-c)', N - c), ('pub(2c)', 2 * c % N), ('pub(c/2)', c * INV2 % N), ('pub(n-2c)', (N - 2 * c) % N)):
    ctl[name] = XT.get(mul(tgt)[0], [])
ok1 = (('sha256(\'causality\')', 'id') in ctl['pub(c)'] and ('sha256(\'causality\')', 'id') in ctl['pub(n-c)']
       and ('sha256(\'causality\')', 'dbl(2k)') in ctl['pub(2c)'] and ('sha256(\'causality\')', 'half(k/2)') in ctl['pub(c/2)']
       and ('sha256(\'causality\')', 'dbl(2k)') in ctl['pub(n-2c)'])
ok1b = any(h[0] == '1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ' and h[2] == 'id' for h in AH)
print('CONTROL chain (causality) x-lookups:', 'PASS' if ok1 else 'FAIL', '| address path:', 'PASS' if ok1b else 'FAIL')
res['control_chain'] = ok1 and ok1b

# ---------------- CONTROL 2: planted random key d; plant n-d, 2d, d/2 as candidates (unknown to table otherwise)
d = secrets.randbelow(N - 1) + 1
plant = {(N - d) % N: 'plant:n-d', 2 * d % N: 'plant:2d', d * INV2 % N: 'plant:d/2'}
XP, _ = build(plant)
got = XP.get(mul(d)[0], [])
exp = {('plant:n-d', 'id'), ('plant:2d', 'half(k/2)'), ('plant:d/2', 'dbl(2k)')}
ok2 = exp <= set(got) and XT.get(mul(d)[0]) is None
print('CONTROL planted:', 'PASS' if ok2 else 'FAIL', sorted(got))
res['control_planted'] = ok2

# ---------------- CONTROL 3: same-breadth negative control (random targets vs the same x-table)
NR = 2000; fp = sum(1 for _ in range(NR) if mul(secrets.randbelow(N - 1) + 1)[0] in XT)
print(f'NEGATIVE control: {fp}/{NR} random targets hit the core x-table (expected 0; analytic rate ~{len(XT)}/2^256)')
res['negative_fp'] = fp; res['scalars'] = len(scalars); res['xtable'] = len(XT)

# ---------------- timing (claims: cryptography ~915us, libsecp256k1 ~70us)
ks = [secrets.randbelow(N - 1) + 1 for _ in range(2000)]
t0 = time.perf_counter(); [mul(k) for k in ks]; tc = (time.perf_counter() - t0) / len(ks)
t0 = time.perf_counter(); [mul_lib(k) for k in ks]; tl = (time.perf_counter() - t0) / len(ks)
print(f'timing per key: cryptography {tc*1e6:.0f}us  libsecp256k1 {tl*1e6:.0f}us')
res['timing_us'] = [round(tc * 1e6), round(tl * 1e6)]
json.dump(res, open('/home/vin/bitcoin_puzzle/scratch/c42/verify1/results.json', 'w'), indent=1, default=str)
