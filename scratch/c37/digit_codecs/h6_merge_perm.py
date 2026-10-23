"""H6: faed as the decimal expansion of text where the 10 decimal digits were written with 9 letters:
a bijection letters->{1..9} (ANY permutation, 9! maps) and the zero digit merged into one letter M
(each occurrence of M independently = 0 or its own digit). Motivation: faed's unigram fits '10 uniform digits,
two merged into g' (g=107 ~ 2x57; other 8 letters chi2 p~0.15). zero_dfs.py covered only the identity map;
subst_sweep.py covered permutations WITHOUT a merged zero. Search: digit-by-digit DFS from the least significant
end, lazy map assignment, byte-local pruning on partial low bits (10^p == 0 mod 2^p). Exhaustive unless truncated.
Self-test: planted text encoded with a random permutation + merged zero must be recovered."""
import sys, time, json, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import CHARSETS, to_bytes, text_to_digits, lowmasks
from common_dc import FAED, DBBI, R60, R61


def search(s, M, cs, max_nodes=50_000_000, max_sol=50):
    low = lowmasks(cs)
    n = len(s)
    letters = sorted(set(s))
    p10 = [10 ** i for i in range(n + 2)]
    st = dict(nodes=0, trunc=False, deepest=0)
    sols = []
    assign = {}
    used = set()
    sys.setrecursionlimit(10000)

    def okp(val, p, k):
        while 8 * (k + 1) <= p:
            if ((val >> (8 * k)) & 255) not in cs: return -1
            k += 1
        r = p - 8 * k
        if r and ((val >> (8 * k)) & ((1 << r) - 1)) not in low[r]: return -1
        return k

    def go(i, val, k):
        st['nodes'] += 1
        if st['nodes'] > max_nodes: st['trunc'] = True; return
        if len(sols) >= max_sol: return
        p = n - 1 - i  # number of digits already placed
        if k > st['deepest']: st['deepest'] = k
        if i < 0:
            nb = (val.bit_length() + 7) // 8
            if val and all(((val >> (8 * j)) & 255) in cs for j in range(k, nb)):
                sols.append((val, dict(assign)))
            return
        c = s[i]
        if c in assign:
            choices = [assign[c]]
            fresh = False
        else:
            choices = [d for d in range(1, 10) if d not in used]
            fresh = True
        for d in choices:
            if fresh: assign[c] = d; used.add(d)
            vals = (d, 0) if c == M else (d,)
            for v in vals:
                if i == 0 and v == 0: continue  # no leading zero
                nv = val + v * p10[p]
                nk = okp(nv, p + 1, k)
                if nk >= 0: go(i - 1, nv, nk)
                if st['trunc'] or len(sols) >= max_sol: break
            if fresh: del assign[c]; used.discard(d)
            if st['trunc'] or len(sols) >= max_sol: return
    go(n - 1, 0, 0)
    return sols, st


def selftest():
    rnd = random.Random(4)
    for T in ('lastwordsbeforearchichoicethispassword', 'theprivatekeysbelongtohalfandbetterhalf'):
        D = text_to_digits(T)
        perm = list('abcdefghi'); rnd.shuffle(perm)
        mp = {str(d): perm[d - 1] for d in range(1, 10)}
        M = rnd.choice('abcdefghi')
        mp['0'] = M
        s = ''.join(mp[ch] for ch in D)
        t0 = time.time()
        sols, st = search(s, M, CHARSETS['lower'], max_nodes=20_000_000, max_sol=1000)
        hit = any(to_bytes(v) == T.encode() for v, a in sols)
        print(f'selftest {T!r} M={M} nsol={len(sols)} recovered={hit} nodes={st["nodes"]} trunc={st["trunc"]} {time.time() - t0:.1f}s', flush=True)
        assert hit


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        selftest(); sys.exit()
    name, M, csn, rev, maxn, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == '1', int(sys.argv[5]), sys.argv[6]
    s = {'FAED': FAED, 'DBBI': DBBI, 'R60': R60, 'R61': R61}[name]
    if rev: s = s[::-1]
    t0 = time.time()
    sols, st = search(s, M, CHARSETS[csn], max_nodes=maxn)
    row = dict(s=name, M=M, cs=csn, rev=rev, nodes=st['nodes'], trunc=st['trunc'], deepest=st['deepest'], nsol=len(sols),
               sols=[(to_bytes(v)[:80].decode('latin1'), a) for v, a in sols[:10]], secs=round(time.time() - t0, 1))
    print(json.dumps(row), flush=True)
    json.dump(row, open(out, 'w'))
