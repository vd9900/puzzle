"""T4: 'matrixsumlist' acting on the btcseed Bifid output (cycle-29's untested 38x15 -> 15-item edge) and
structural decodes of its forced pair structure.
(a) BIF (570 letters) or BIF[7:] / faed laid as 38x15 (and 15x38, 30x19, 19x30): column/row sum lists with letter
    values (square index 0..24, a0z25 alphabet index, a1z26) -> BIP39 15-word checksum test when the list has 15
    entries < 2048 (detector: checksum, chance 1/32 per vector), and 12/18/24-length lists likewise.
(b) BIF even letters are forced into {b,c,d,e} (square cells 0..3), odd letters free (25).  A designed plaintext
    would then be (4 x 25 = 100)-valued pairs = two decimal digits; read pairs (aligned at 0 and after the 7-letter
    btcseed header) as base-100 digits -> page z-method (decimal -> int -> bytes) and as raw byte values.
    Detector: printable ratio / longest printable run vs 200 random-faed controls pushed through the same Bifid.
Planted self-test for (b): encode a known text as base-100 pairs, Bifid-encrypt with the source square, decode."""
import sys, hashlib, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
import bifid
SQ = bifid.CANON
A26 = 'abcdefghijklmnopqrstuvwxyz'

def bip39_ok(idx):
    n = len(idx)
    if n not in (12, 15, 18, 21, 24) or any(not (0 <= x < 2048) for x in idx):
        return None
    bits = ''.join(format(x, '011b') for x in idx)
    cs = n // 3; ent = bits[:-cs]
    h = hashlib.sha256(int(ent, 2).to_bytes(len(ent) // 8, 'big')).digest()
    return format(h[0], '08b')[:cs] == bits[-cs:]

VALS = {
    'sqidx': lambda ch: SQ.index(ch),
    'a0z25': lambda ch: A26.index(ch),
    'a1z26': lambda ch: A26.index(ch) + 1,
}

def part_a():
    out = []
    srcs = {'bif': bifid.BIF, 'bif_body': bifid.BIF[7:], 'faed': FAED}
    for sn, s in srcs.items():
        for vn, f in VALS.items():
            v = [f(c) for c in s]
            for w in (15, 38, 19, 30, 12, 18, 24):
                for axis in ('rows', 'cols'):
                    L = grid_sums(v, w, axis)
                    for nm, LL in ((axis, L), (axis + '_rev', L[::-1])):
                        r = bip39_ok(LL)
                        if r is not None:
                            out.append((sn, vn, w, nm, r, LL))
    return out

def pair_values(s, start, order):
    vals = []
    for i in range(start, len(s) - 1, 2):
        x, y = s[i], s[i + 1]
        e, o = (x, y) if order == 'eo' else (y, x)
        if e not in 'dbce':
            return None
        hi = 'dbce'.index(e)   # square cells 0..3 = d,b,i? no: cells 0,1,5,6 -> use square order
        vals.append((hi, SQ.index(o)))
    return vals

def even_code(ch):
    # even letters occupy square cells (0,0)=d,(0,1)=b,(1,0)=c,(1,1)=e -> 2-bit value r*2+c
    r, c = divmod(SQ.index(ch), 5)
    return r * 2 + c

def decodes_b(s):
    res = []
    for start in (0, 7, 1, 8):
        for order in ('eo', 'oe'):
            prs = []
            ok = True
            for i in range(start, len(s) - 1, 2):
                x, y = s[i], s[i + 1]
                e, o = (x, y) if order == 'eo' else (y, x)
                if SQ.index(e) not in (0, 1, 5, 6):
                    ok = False; break
                prs.append((even_code(e), SQ.index(o)))
            if not ok or not prs:
                continue
            for comb in ('e*25+o', 'o*4+e'):
                vals = [a * 25 + b if comb == 'e*25+o' else b * 4 + a for a, b in prs]
                digs = [int(ch) for v in vals for ch in f'{v:02d}']
                res.append(((start, order, comb, 'z100'), zdec(digs)))
                res.append(((start, order, comb, 'bytes'), bytes(vals)))
                res.append(((start, order, comb, 'bytes+32'), bytes(v + 32 for v in vals if v + 32 < 256)))
    return res

def stat(res):
    return max(longest_printable_run(b) for p, b in res), max(pr(b) for p, b in res if len(b) > 20)

if __name__ == '__main__':
    # self-test for (b): plant a text as base-100 pair digits -> plaintext letters -> Bifid-encrypt -> decode
    T = b'planted test key 5Kxxxx'
    n = int.from_bytes(T, 'big'); ds = str(n)
    if len(ds) % 2: ds = '0' + ds
    vals = [int(ds[i:i + 2]) for i in range(0, len(ds), 2)]
    cells = {0: 0, 1: 1, 2: 5, 3: 6}
    pt = ''.join(SQ[cells[v // 25]] + SQ[v % 25] for v in vals)
    ct = bifid.bifid_encrypt(pt, SQ, len(pt))
    dec = bifid.bifid_decrypt(ct, SQ, len(ct))
    assert dec == pt
    rec = [b for p, b in decodes_b(dec) if p == (0, 'eo', 'e*25+o', 'z100')][0]
    assert rec == T, rec
    print('planted self-test (b) OK')
    # (a)
    A = part_a()
    npass = sum(1 for x in A if x[4])
    print(f'(a) BIP39-length sum-list vectors tested: {len(A)}; checksum passes: {npass} (expected by chance {len(A)/32:.1f} for 15-word, varies)')
    for x in A:
        if x[4]: print('   pass', x[:4], x[5])
    # (b)
    R = decodes_b(bifid.BIF)
    run, bpr = stat(R)
    print(f'(b) real decodes {len(R)}: longest printable run {run}, best printable ratio {bpr:.3f}')
    for p, b in sorted(R, key=lambda r: -pr(r[1]))[:4]:
        print('   ', p, round(pr(b), 3), b[:50])
    # control: random a..i strings with faed's unigram -> Bifid decrypt -> same decodes
    rnd = random.Random(99)
    cr = []; cp = []
    for t in range(200):
        fake = shuffled(FAED, 500 + t)
        d = bifid.bifid_decrypt(fake, SQ, 570)
        rr = decodes_b(d)
        if rr:
            a, b2 = stat(rr); cr.append(a); cp.append(b2)
    cr.sort(); cp.sort()
    print(f'(b) control (n={len(cr)}): run median {cr[len(cr)//2]} max {cr[-1]}; printable median {cp[len(cp)//2]:.3f} max {cp[-1]:.3f}')
