"""H9: binary payloads. Length feasibility (h7) shows a 570-digit number has top byte 4..45 and faed (identity, any
zeroing) has top byte 27..31, so the only common binary magics reachable are gzip (1f 8b 08) and ESC-led text
(ANSI '\x1b['). Test, top-down with position-dependent byte sets:
  P1  T2 family (any bijection letters->1..9, zero merged into g; 9! maps) for gzip header 1f 8b 08 and for
      ANSI text (0x1b '[' then printable/ESC);
  P2  T3 family (identity map, any subset of digits zeroed) on DBBI/FAED (+rev) for gzip header;
  P3  marker reinsertion (h1b classes, id/a0 residual) top-down is unnecessary: WIF/Salted__ were already checked
      exhaustively in h1b (232,698 assignments, 0 hits).
Self-test: a planted gzip stream encoded under a random permutation + merged zero is found."""
import sys, json, random, gzip, time
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from h4_topdown import TD, STRS
from h5_topdown_more import CHARSETS
from engine import to_bytes
ALL = set(range(256))


class TDP(TD):
    """top-down with per-position byte sets: sets[t] for top byte t (t < len(sets)), default for the rest."""
    def __init__(self, L, sets, default, max_nodes):
        super().__init__(L, default, max_nodes); self.sets = sets; self.default = default

    def check(self, A, r, kd):
        hi = A + self.p10[r] - 1
        nb_lo = (A.bit_length() + 7) // 8; nb_hi = (hi.bit_length() + 7) // 8
        if nb_lo != nb_hi: return kd
        nb = nb_hi; j0 = ((A ^ hi).bit_length() + 7) // 8; top_det = nb - j0
        for t in range(kd, top_det):
            allowed = self.sets[t] if t < len(self.sets) else self.default
            if ((A >> (8 * (nb - 1 - t))) & 255) not in allowed: return -1
        if top_det > self.deepest: self.deepest = top_det
        return max(kd, top_det)


def perm_search(s, M, sets, default, max_nodes=50_000_000, need=None):
    n = len(s); T = TDP(n, sets, default, max_nodes); assign = {}; used = set()
    sys.setrecursionlimit(10000)
    def go(t, A, kd):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        if need is not None and kd >= need:       # enough leading bytes verified: record and stop this branch
            T.sols.append((A, dict(assign), t)); return
        if t == n:
            T.sols.append((A, dict(assign), t)); return
        c = s[t]; r = n - t - 1; fresh = c not in assign
        for d in ([d for d in range(1, 10) if d not in used] if fresh else [assign[c]]):
            if fresh: assign[c] = d; used.add(d)
            for v in ((d, 0) if (c == M and t > 0) else (d,)):
                nA = A + v * T.p10[r]; nk = T.check(nA, r, kd)
                if nk >= 0: go(t + 1, nA, nk)
            if fresh: del assign[c]; used.discard(d)
            if T.trunc: return
    go(0, 0, 0)
    return T


def zero_any_search(digs, sets, default, Kmax, need, max_nodes=50_000_000):
    n = len(digs); T = TDP(n, sets, default, max_nodes); dv = [int(c) for c in digs]
    sys.setrecursionlimit(10000)
    def go(t, A, kd, K):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        if kd >= need: T.sols.append((A, t)); return
        if t == n: return
        r = n - t - 1
        nA = A + dv[t] * T.p10[r]; nk = T.check(nA, r, kd)
        if nk >= 0: go(t + 1, nA, nk, K)
        if t > 0 and K < Kmax:
            nk = T.check(A, r, kd)
            if nk >= 0: go(t + 1, A, nk, K + 1)
    go(0, 0, 0, 0)
    return T


GZ = [{0x1f}, {0x8b}, {0x08}, set(range(0, 32))]          # magic, deflate, flags (reserved bits 5-7 zero)


def selftest():
    rnd = random.Random(9)
    payload = gzip.compress(b'reinserting the prime basics ' * 3, mtime=0)
    while True:   # need a stream whose decimal starts with a digit pattern compatible; any stream works top-down
        D = str(int.from_bytes(payload, 'big'))
        perm = list('abcdefghi'); rnd.shuffle(perm)
        mp = {str(d): perm[d - 1] for d in range(1, 10)}; M = mp['7']; mp['0'] = M
        s = ''.join(mp[ch] for ch in D)
        T = perm_search(s, M, GZ, ALL, need=4)
        true = {perm[d - 1]: d for d in range(1, 10)}
        hit = any(all(true[L] == dv for L, dv in a.items()) and to_bytes(v)[:3] == payload[:3] for v, a, t in T.sols)
        print(f'selftest gzip plant: len={len(payload)}B digits={len(D)} prefix-solutions={len(T.sols)} true-map-among-them={hit} nodes={T.nodes}')
        assert hit
        break


def main():
    selftest()
    rows = []
    ANSI = [{0x1b}, {0x5b}]
    ansi_default = CHARSETS['printnl'] | {0x1b}
    for name in ('FAED', 'FAED_rev'):
        t0 = time.time(); T = perm_search(STRS[name], 'g', GZ, ALL, need=4)
        rows.append(dict(test='P1_gzip', s=name, nodes=T.nodes, trunc=T.trunc, n_prefix_solutions=len(T.sols),
                         sols=[(to_bytes(v)[:8].hex(), a) for v, a, t in T.sols[:5]], secs=round(time.time() - t0, 1)))
        print(json.dumps(rows[-1])[:300], flush=True)
        t0 = time.time(); T = perm_search(STRS[name], 'g', ANSI, ansi_default, max_nodes=100_000_000)
        rows.append(dict(test='P1_ansi_text', s=name, nodes=T.nodes, trunc=T.trunc, deepest_top_bytes=T.deepest, n_full=len(T.sols),
                         secs=round(time.time() - t0, 1)))
        print(json.dumps(rows[-1])[:300], flush=True)
    for name in ('DBBI', 'DBBI_rev', 'FAED', 'FAED_rev'):
        digs = ''.join(str(ord(c) - 96) for c in STRS[name])
        T = zero_any_search(digs, GZ, ALL, Kmax=len(digs), need=4)
        rows.append(dict(test='P2_gzip_anyzero', s=name, nodes=T.nodes, trunc=T.trunc, n_prefix_solutions=len(T.sols),
                         sols=[to_bytes(v)[:8].hex() for v, t in T.sols[:5]]))
        print(json.dumps(rows[-1])[:300], flush=True)
    json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h9_magic.json', 'w'), indent=0)


if __name__ == '__main__':
    main()
