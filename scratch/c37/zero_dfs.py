"""Cycle 37: which characters were '0' before being disguised?
Hypothesis: a letter-digit string S (a=1..i=9) is the decimal expansion of an integer M whose
big-endian bytes are text, except that some digits were written as a nonzero letter instead of 0.
Low k bytes of M depend only on the lowest 8k decimal digits (10^p = 0 mod 256^k for p>=8k),
so search from the least-significant end, pruning on the byte charset."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, Z1, Z2

LOWER = set(range(0x61, 0x7b))
PRINT = set(range(0x20, 0x7f))

def dfs(s, zero_letters, charset, max_nodes=2_000_000, allow=None):
    """s: letter string. zero_letters: letters that may stand for 0 (each occurrence independently).
    allow: optional set of 0-based positions eligible for zeroing. Returns list of (bytes_low, zeroed_positions)."""
    d = [ord(c) - 96 for c in s]          # a=1..i=9
    n = len(d)
    best = [0, None]
    nodes = [0]
    sols = []
    # process digits from least significant (index n-1) upward, 8 at a time = one byte
    def rec(k, val, zeroed):
        # val = integer of lowest 8k digits (as modified); bytes 0..k-1 already validated
        nodes[0] += 1
        if nodes[0] > max_nodes: return
        if k > best[0]: best[0] = k; best[1] = (val, list(zeroed))
        lo = n - 8 * (k + 1)
        hi = n - 8 * k  # digits indices lo..hi-1 are the next 8 (from the right)
        if hi <= 0:
            sols.append((val, list(zeroed))); return
        idxs = list(range(max(lo, 0), hi))
        # enumerate choices over eligible positions in this window
        elig = [i for i in idxs if s[i] in zero_letters and (allow is None or i in allow)]
        base = val + sum(d[i] * 10 ** (n - 1 - i) for i in idxs)
        for mask in range(1 << len(elig)):
            v = base
            z = []
            for b, i in enumerate(elig):
                if mask >> b & 1:
                    v -= d[i] * 10 ** (n - 1 - i); z.append(i)
            if lo <= 0:
                # final partial window: whole number known; check all remaining bytes
                bs = v.to_bytes((v.bit_length() + 7) // 8, 'big')
                tail = bs[:len(bs) - k] if k else bs
                if all(c in charset for c in tail):
                    sols.append((v, zeroed + z))
                continue
            byte = (v >> (8 * k)) & 0xFF
            if byte in charset:
                rec(k + 1, v, zeroed + z)
    rec(0, 0, [])
    return sols, best, nodes[0]

def show(name, s, letters, charset, cname):
    sols, best, nodes = dfs(s, letters, charset)
    k, (val, z) = best[0], best[1] if best[1] else (0, (0, []))
    lowbytes = (best[1][0] % (256 ** best[0])).to_bytes(best[0], 'big') if best[1] else b''
    print(f'{name} zero∈{letters!r:12} {cname}: solutions={len(sols)} deepest={best[0]} bytes nodes={nodes} tail={lowbytes[-40:]!r}')
    for v, z in sols[:3]:
        print('   SOLUTION', v.to_bytes((v.bit_length()+7)//8,'big'), z)
    return sols

if __name__ == '__main__':
    # sanity: re-encode Z1 with zeros disguised as a random letter, then recover
    from common import letters_to_digits
    z1 = Z1.replace('o', 'g')
    sols = show('Z1-disguised(o->g)', z1, 'g', LOWER, 'lower')
    assert any(v.to_bytes((v.bit_length()+7)//8,'big') == b'lastwordsbeforearchichoice' for v, _ in sols)
    for name, s in (('FAED', FAED), ('DBBI', DBBI)):
        for L in 'abcdefghi':
            show(name, s, L, LOWER, 'lower')
        for L in 'abcdefghi':
            show(name, s, L, PRINT, 'print')
