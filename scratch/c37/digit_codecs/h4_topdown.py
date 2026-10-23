"""H4: TOP-DOWN (most-significant-first) z-method searches.
Bottom-up pruning needs 8 decimal digits per verified byte (10^p == 0 mod 2^p); top-down interval pruning fixes
one more leading byte every ~2.41 digits, so families that are supercritical bottom-up become subcritical.
At a node with prefix value A and r digits still unplaced, N lies in [A, A+10^r-1]; all bytes above the highest
differing bit of A ^ (A+10^r-1) are determined (if both ends have the same byte length) and must lie in the charset.

T1 'zeros deleted, reinsert freely': the letter string (a=1..i=9) is the decimal expansion of text with every
   0 digit DELETED; for each total count Z, try every placement of Z zeros (no leading zero). Expected number of
   false full solutions for n=60, Z<=25, lowercase: sum_Z C(n+Z,Z)*(26/256)^bytes  << 1e-10 (decisive).
T2 H6 family top-down: any bijection letters->1..9 plus zero merged into letter M (each occurrence 0 or its digit),
   exhaustive with the printnl charset that was intractable bottom-up.
Self-tests: planted texts for both."""
import sys, time, json, random, math
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import CHARSETS, to_bytes, text_to_digits
from common_dc import DBBI, FAED, R60, R61
from h1b_markers import tokens
R56 = ''.join(t for t, m, _ in tokens('G') if not m)
CHARSETS = dict(CHARSETS)
CHARSETS['textish'] = set(range(0x41, 0x5b)) | set(range(0x61, 0x7b)) | set(range(0x30, 0x3a)) | set(b" \n.,;:!?'\"-()/")


class TD:
    def __init__(self, L, cs, max_nodes):
        self.L = L; self.cs = cs; self.max_nodes = max_nodes
        self.p10 = [10 ** i for i in range(L + 1)]
        self.nodes = 0; self.trunc = False; self.sols = []; self.deepest = 0

    def check(self, A, r, kd):
        """returns new count of verified top bytes or -1. kd = top bytes already verified."""
        hi = A + self.p10[r] - 1
        nb_lo = (A.bit_length() + 7) // 8; nb_hi = (hi.bit_length() + 7) // 8
        if nb_lo != nb_hi: return kd
        nb = nb_hi
        j0 = ((A ^ hi).bit_length() + 7) // 8   # bytes j >= j0 (from LSB) are determined
        top_det = nb - j0                       # number of determined top bytes
        for t in range(kd, top_det):
            if ((A >> (8 * (nb - 1 - t))) & 255) not in self.cs: return -1
        if top_det > self.deepest: self.deepest = top_det
        return max(kd, top_det)


def td_insert(digs, Z, cs, max_nodes=20_000_000, max_sol=20):
    n = len(digs); L = n + Z; T = TD(L, cs, max_nodes)
    dv = [int(c) for c in digs]
    sys.setrecursionlimit(10000)
    def go(i, z, A, kd):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        t = i + z
        if t == L:
            if all(c in cs for c in to_bytes(A)): T.sols.append(A)
            return
        r = L - t - 1
        if i < n:
            nA = A + dv[i] * T.p10[r]; nk = T.check(nA, r, kd)
            if nk >= 0: go(i + 1, z, nA, nk)
        if z < Z and t > 0:
            nk = T.check(A, r, kd)
            if nk >= 0: go(i, z + 1, A, nk)
        if T.trunc or len(T.sols) >= max_sol: return
    go(0, 0, 0, 0)
    return T


def td_perm(s, M, cs, max_nodes=200_000_000, max_sol=50):
    n = len(s); T = TD(n, cs, max_nodes); assign = {}; used = set()
    sys.setrecursionlimit(10000)
    def go(t, A, kd):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        if t == n:
            if all(c in cs for c in to_bytes(A)): T.sols.append((A, dict(assign)))
            return
        c = s[t]; r = n - t - 1
        fresh = c not in assign
        choices = [d for d in range(1, 10) if d not in used] if fresh else [assign[c]]
        for d in choices:
            if fresh: assign[c] = d; used.add(d)
            for v in ((d, 0) if (c == M and t > 0) else (d,)):
                nA = A + v * T.p10[r]; nk = T.check(nA, r, kd)
                if nk >= 0: go(t + 1, nA, nk)
                if T.trunc or len(T.sols) >= max_sol: break
            if fresh: del assign[c]; used.discard(d)
            if T.trunc or len(T.sols) >= max_sol: return
    go(0, 0, 0)
    return T


def selftest():
    for Tt in ('lastwordsbeforearchichoice', 'thispassword', 'reinsertingtheprimebasics'):
        D = text_to_digits(Tt); Z = D.count('0'); stripped = D.replace('0', '')
        T = td_insert(stripped, Z, CHARSETS['lower'], max_sol=1000)
        hit = any(to_bytes(v) == Tt.encode() for v in T.sols)
        print(f'T1 selftest {Tt!r} Z={Z} nsol={len(T.sols)} recovered={hit} nodes={T.nodes}', flush=True)
        assert hit
    rnd = random.Random(4)
    for Tt in ('lastwordsbeforearchichoicethispassword', 'Raising the stakes, without extra chances of winning.'):
        D = text_to_digits(Tt); perm = list('abcdefghi'); rnd.shuffle(perm)
        M = rnd.choice('abcdefghi'); mp = {str(d): perm[d - 1] for d in range(1, 10)}; mp['0'] = M
        s = ''.join(mp[ch] for ch in D)
        T = td_perm(s, M, CHARSETS['printnl'], max_nodes=50_000_000, max_sol=1000)
        hit = any(to_bytes(v) == Tt.encode() for v, a in T.sols)
        print(f'T2 selftest {Tt!r} M={M} nsol={len(T.sols)} recovered={hit} nodes={T.nodes} trunc={T.trunc}', flush=True)
        assert hit


STRS = {'DBBI': DBBI, 'R60': R60, 'R61': R61, 'R56': R56, 'FAED': FAED}
STRS.update({k + '_rev': v[::-1] for k, v in list(STRS.items())})


def run_T1(names, csns, out):
    rows = []
    for name in names:
        s = STRS[name]; digs = ''.join(str(ord(c) - 96) for c in s); n = len(digs)
        if 'FAED' in name: Zs = range(0, 131)
        else: Zs = range(0, 31)
        for csn in csns:
            t0 = time.time(); tot = 0; sols = []; trunc = False; deep = 0; expect = 0.0
            for Z in Zs:
                T = td_insert(digs, Z, CHARSETS[csn], max_nodes=20_000_000)
                tot += T.nodes; trunc |= T.trunc; deep = max(deep, T.deepest)
                sols += [(Z, to_bytes(v)[:80].decode('latin1')) for v in T.sols[:5]]
                nbytes = math.ceil((n + Z) * math.log2(10) / 8)
                expect += math.comb(n + Z - 1, Z) * (len(CHARSETS[csn]) / 256) ** nbytes
            row = dict(test='T1', s=name, cs=csn, Zmax=max(Zs), nodes=tot, trunc=trunc, deepest_top_bytes=deep,
                       nsol=len(sols), sols=sols[:5], expected_false_solutions=expect, secs=round(time.time() - t0, 1))
            rows.append(row); print(('!!! ' if sols else '    ') + json.dumps(row)[:400], flush=True)
    json.dump(rows, open(out, 'w'), indent=0)


def run_T2(name, M, csn, maxn, out):
    s = STRS[name]; t0 = time.time()
    T = td_perm(s, M, CHARSETS[csn], max_nodes=maxn)
    row = dict(test='T2', s=name, M=M, cs=csn, nodes=T.nodes, trunc=T.trunc, deepest_top_bytes=T.deepest, nsol=len(T.sols),
               sols=[(to_bytes(v)[:80].decode('latin1'), a) for v, a in T.sols[:5]], secs=round(time.time() - t0, 1))
    print(json.dumps(row)[:400], flush=True); json.dump(row, open(out, 'w'))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'selftest': selftest()
    elif cmd == 'T1': run_T1(sys.argv[2].split(','), sys.argv[3].split(','), sys.argv[4])
    elif cmd == 'T2': run_T2(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6])
