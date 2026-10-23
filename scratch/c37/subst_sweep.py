"""Every injective letter->digit map (a..i -> 0..9) for base 10, and every bijection to 0..8 for base 9.
Base 10: low k bytes depend only on the lowest 8k digits, so test byte by byte and stop at the first failure.
Base 9: full conversion. Oracle: big-endian bytes all lowercase / all printable."""
import sys, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
LO = range(0x61, 0x7b)
def ok_lower(b): return 0x61 <= b <= 0x7a
def ok_print(b): return 0x20 <= b <= 0x7e or b in (9, 10, 13)

def sweep10(name, s, okf, need=6):
    letters = sorted(set(s)); n = len(s)
    best = []
    for digs in itertools.permutations(range(10), len(letters)):
        m = dict(zip(letters, digs))
        if m[s[0]] == 0: continue
        val = 0; k = 0; good = True
        # incrementally add 8 digits then check next byte
        p = 0
        for i in range(n - 1, -1, -1):
            val += m[s[i]] * 10 ** p; p += 1
            if p % 8 == 0:
                if not okf((val >> (8 * k)) & 0xFF): good = False; break
                k += 1
        if good:
            v = val; bs = v.to_bytes((v.bit_length() + 7) // 8, 'big')
            if all(okf(c) for c in bs): print('!!! FULL', name, m, bs[:100]); best.append((m, bs))
        if k >= need: print(f'  deep {name} k={k} map={"".join(str(m[c]) for c in letters)}')
    return best

def sweep9(name, s, okf):
    letters = sorted(set(s)); hits = 0
    for digs in itertools.permutations(range(9), len(letters)):
        m = dict(zip(letters, digs))
        v = int(''.join(str(m[c]) for c in s), 9)
        bs = v.to_bytes((v.bit_length() + 7) // 8, 'big')
        r = sum(okf(c) for c in bs) / len(bs)
        if r > 0.8: print('  b9', name, digs, round(r, 2), bs[:60]); hits += 1
    return hits

if __name__ == '__main__':
    for name, s in (('DBBI', DBBI), ('RES60', RES60), ('FAED', FAED)):
        print('==', name, 'base10 lower'); sweep10(name, s, ok_lower, need=5)
        print('==', name, 'base10 print'); sweep10(name, s, ok_print, need=8)
        print('==', name, 'base9 print>0.8:', sweep9(name, s, ok_print))
