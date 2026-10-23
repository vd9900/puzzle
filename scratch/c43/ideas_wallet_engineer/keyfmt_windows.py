#!/usr/bin/env python3
"""Wallet-engineer pre-test: does any window of faed/dbbi/R60 (a..i = 1..9, g = 0 or 7, fwd/rev) decode,
under the puzzle's own decimal-integer convention, to a STANDARD private-key encoding?
  (A) integer = base58check payload of a WIF: 0x80||k||chk (uncompressed, 37 B) or 0x80||k||01||chk (compressed, 38 B)
  (B) integer = z-method of a key TEXT: 64-char hex (lower/upper), 51-char WIF '5..', 52-char WIF 'K..'/'L..'
Self-verifying oracle: base58check checksum (A, B-WIF) then k*G == target point (all forms).
Controls: a test key planted in every form into copies of faed (0 and 7 both written 'g') must be recovered.
Usage: python3 keyfmt_windows.py"""
import sys, hashlib, time
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c43/test0')
from common import FAED, DBBI
import ec

R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
B58 = ec.B58
def sha256d(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def b58enc(b):
    n = int.from_bytes(b, 'big'); s = ''
    while n: n, r = divmod(n, 58); s = B58[r] + s
    return s
def b58dec_int(s):
    n = 0
    for c in s: n = n * 58 + B58.index(c)
    return n
def wif(k, comp):
    p = b'\x80' + k.to_bytes(32, 'big') + (b'\x01' if comp else b'')
    return b58enc(p + sha256d(p)[:4])
def dvals(ch): return (0, 7) if ch == 'g' else (ord(ch) - 96,)
def letters(digs): return ''.join('g' if d in '07' else chr(96 + int(d)) for d in digs)

def key_ok(k, target):
    return 0 < k < ec.N and ec.mul(k) == target

def payload_check(P, nbytes, target):
    """P: integer candidate for a WIF base58check payload. Returns key or None."""
    b = P.to_bytes(nbytes, 'big')
    if b[0] != 0x80 or sha256d(b[:-4])[:4] != b[-4:]: return None
    if nbytes == 38 and b[33] != 1: return None
    k = int.from_bytes(b[1:33], 'big')
    return k if key_ok(k, target) else None

# ---------- (A) payload integers: top-down interval pruning ----------
PAYLOAD = {'wifU_payload': (37, 0x80 << 288, 0x81 << 288), 'wifC_payload': (38, 0x80 << 296, 0x81 << 296)}

def scan_payload(s, target, stats):
    hits = []
    for name, (nb, lo, hi) in PAYLOAD.items():
        L = len(str(lo))
        assert len(str(hi - 1)) == L
        for st in range(0, len(s) - L + 1):
            w = s[st:st + L]
            # suffix bounds: min/max value of digits i..L-1 (g -> 0 / 7)
            mn = [0] * (L + 1); mx = [0] * (L + 1)
            for i in range(L - 1, -1, -1):
                v = dvals(w[i]); p = 10 ** (L - 1 - i)
                mn[i] = mn[i + 1] + min(v) * p; mx[i] = mx[i + 1] + max(v) * p
            stack = [(0, 0)]
            while stack:
                i, acc = stack.pop()
                if acc + mx[i] < lo or acc + mn[i] >= hi: continue
                if i == L:
                    stats[name] += 1
                    k = payload_check(acc, nb, target)
                    if k: hits.append((name, st, k))
                    continue
                p = 10 ** (L - 1 - i)
                for d in dvals(w[i]): stack.append((i + 1, acc + d * p))
    return hits

# ---------- (B) z-method of a key TEXT: low-end byte DFS (low k bytes depend only on lowest 8k digits) ----------
HEXL = set(b'0123456789abcdef'); HEXU = set(b'0123456789ABCDEF'); B58S = set(B58.encode())
TEXT = {  # name: (T bytes, charset, allowed first bytes)
    'hex64_lower': (64, HEXL, HEXL), 'hex64_upper': (64, HEXU, HEXU),
    'wifU_text': (51, B58S, set(b'5')), 'wifC_text': (52, B58S, set(b'KL')),
}

def text_validate(name, tb, target):
    t = tb.decode()
    if name.startswith('hex'):
        k = int(t, 16)
        return k if key_ok(k, target) else None
    return payload_check(b58dec_int(t), 37 if name == 'wifU_text' else 38, target)

def scan_text(s, target, stats):
    hits = []
    for name, (T, cs, first) in TEXT.items():
        lo = min(first) << (8 * (T - 1)); hi = (max(first) + 1) << (8 * (T - 1))
        for D in range(len(str(lo)), len(str(hi - 1)) + 1):
            for st in range(0, len(s) - D + 1):
                w = s[st:st + D]
                stack = [(0, 0)]
                while stack:
                    k, V = stack.pop()
                    a = max(D - 8 * (k + 1), 0); b = D - 8 * k
                    idx = list(range(a, b))
                    choices = [()]
                    for i in idx:
                        choices = [c + (d,) for c in choices for d in dvals(w[i])]
                    for c in choices:
                        V2 = V + sum(d * 10 ** (D - 1 - i) for d, i in zip(c, idx))
                        if a == 0:
                            stats[name] += 1
                            if V2 >> (8 * (T - 1)) == 0 or V2 >> (8 * T): continue
                            tb = V2.to_bytes(T, 'big')
                            if tb[0] in first and all(x in cs for x in tb[k:]) and all(x in cs for x in tb):
                                kk = text_validate(name, tb, target)
                                if kk: hits.append((name, st, kk))
                        else:
                            if ((V2 >> (8 * k)) & 0xFF) in cs: stack.append((k + 1, V2))
    return hits

# ---------- controls + real run ----------
def run(s, target):
    from collections import Counter
    st = Counter()
    return scan_payload(s, target, st) + scan_text(s, target, st), st

if __name__ == '__main__':
    t0 = time.time()
    kt = int.from_bytes(hashlib.sha256(b'c43 wallet-engineer plant').digest(), 'big') % ec.N
    tt = ec.mul(kt)
    plants = {
        'wifU_payload': (str(int.from_bytes(b'\x80' + kt.to_bytes(32, 'big') + sha256d(b'\x80' + kt.to_bytes(32, 'big'))[:4], 'big')), 40),
        'wifC_payload': (str(b58dec_int(wif(kt, True))), 300),
        'hex64_lower': (str(int.from_bytes(format(kt, '064x').encode(), 'big')), 120),
        'hex64_upper': (str(int.from_bytes(format(kt, '064X').encode(), 'big')), 380),
        'wifU_text': (str(int.from_bytes(wif(kt, False).encode(), 'big')), 10),
        'wifC_text': (str(int.from_bytes(wif(kt, True).encode(), 'big')), 200),
    }
    ok = True
    for name, (digs, off) in plants.items():
        lt = letters(digs)
        s = FAED[:off] + lt + FAED[off + len(lt):]
        assert len(s) == len(FAED)
        hits, st = run(s, tt)
        good = any(h[0] == name and h[1] == off and h[2] == kt for h in hits)
        ok &= good
        print(f'control {name:13s} digits={len(digs)} g_in_plant={lt.count("g")} recovered={good} hits={[(h[0], h[1]) for h in hits]}')
    print('CONTROLS', 'ALL OK' if ok else 'FAILED', f'{time.time() - t0:.0f}s')
    srcs = {'faed': FAED, 'faed_rev': FAED[::-1], 'dbbi': DBBI, 'dbbi_rev': DBBI[::-1], 'R60': R60, 'R60_rev': R60[::-1]}
    total = {}
    allhits = []
    for nm, s in srcs.items():
        hits, st = run(s, ec.TGT)
        allhits += [(nm,) + h for h in hits]
        for k, v in st.items(): total[k] = total.get(k, 0) + v
        print(f'REAL {nm:8s} hits={len(hits)} candidates_reaching_oracle={dict(st)}')
    print('REAL TOTAL hits', len(allhits), allhits, 'candidates per form', total, f'{time.time() - t0:.0f}s')
