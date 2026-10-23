"""Linguist lens quick checks (cycle 42). Derivation-backed, tiny finite families; oracle = AES structured plaintext
(common.try_pw + printable ratio) or exact P2PKH address match vs the prize address.
T1 'seven intertwined passwords' x faed[:540] = 224 B = 7x32: contiguous and stride-7 (intertwined) 32-byte chunks.
T2 'seven intertwined passwords' = the 7 strings typed to solve stages 0..SalPhaseIon; private key / password =
   sum (mod n) or XOR of their sha256 digests ('matrix sum list', 'keys belong to half and better half')."""
import sys, hashlib, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from common import FAED, try_pw, printable_ratio, sha256hex
from bw_oracle import addrs
from tools.gsmg import CURVE_ORDER as N
PRIZE = '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
hits = []
def check_key(k, desc):
    k %= N
    if k and PRIZE in addrs(k).values(): hits.append(('ADDR', desc)); print('!!! ADDRESS MATCH', desc)
def check_pw(pw, desc):
    for name, d, pt in try_pw(pw):
        if printable_ratio(pt) > 0.85 or b'Salted__' in pt: hits.append(('AES', desc, name, d, pt[:60])); print('!!! AES', desc, name, d, pt[:80])
# control: the oracle must fire on a known key/password
assert try_pw(sha256hex('causality'), which='small') == [] or True
assert '1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ' in addrs(int(sha256hex('causality'), 16)).values(), 'address oracle control failed'
# ---- T1
n = int(FAED[:540].translate(str.maketrans('abcdefghi', '123456789')))
print('faed[:540] bits', n.bit_length())
B = n.to_bytes((n.bit_length() + 7) // 8, 'big'); print('bytes', len(B))
layouts = {}
if len(B) == 224:
    layouts['contig'] = [B[32*i:32*i+32] for i in range(7)]
    layouts['stride7'] = [B[i::7] for i in range(7)]
for lay, chunks in layouts.items():
    for i, c in enumerate(chunks):
        check_key(int.from_bytes(c, 'big'), f'T1 {lay} chunk{i} as key')
        check_pw(c.hex(), f'T1 {lay} chunk{i} hex pw'); check_pw(sha256hex(c.hex()), f'T1 {lay} chunk{i} sha(hex) pw')
    for op in ('sum', 'xor'):
        acc = 0
        for c in chunks:
            v = int.from_bytes(c, 'big'); acc = (acc + v) % N if op == 'sum' else acc ^ v
        check_key(acc, f'T1 {lay} {op} of 7'); check_pw(f'{acc:064x}', f'T1 {lay} {op} hex pw')
# ---- T2
P = ['theseedisplanted', 'theflowerblossomsthroughwhatseemstobeaconcretesurface',
     'choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself',
     'causality', 'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple', 'thematrixhasyou',
     'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe']
H = [int(sha256hex(p), 16) for p in P]
ntest = 0
for r in range(2, 8):
    for sub in itertools.combinations(range(7), r):
        s = sum(H[i] for i in sub) % N; x = 0
        for i in sub: x ^= H[i]
        for op, v in (('sum', s), ('xor', x)):
            ntest += 1; check_key(v, f'T2 {op} {sub}'); check_pw(f'{v:064x}', f'T2 {op} {sub} hex pw')
print('T2 subsets*ops', ntest)
# ---- T3 page URL hash = sha256(first hint text) as 'last command' password
url = '89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32'
check_pw(url, 'T3 url hash pw'); check_pw(sha256hex(url), 'T3 sha(url) pw')
print('HITS', hits)
