"""H5 (top-down, cont.):
T3  'any character may be zeroed out': identity map a=1..i=9, EVERY occurrence of EVERY letter may independently be
    replaced by 0 (at most K zeros). Exhaustive top-down DFS. Unbounded K for lower/lowsp (expected false solutions
    << 1); bounded K for textish/printnl (K <= Kmax chosen so the expected number of false solutions is < 0.05).
EB  EBCDIC charsets (the creator used cp273/EBCDIC in Phase 3.2): re-run the identity-map families
    T1 (free zero reinsertion), T3 (any zeroing), T2 (any permutation + zero merged into g, faed) with
    ebc_lower (a-z in cp273), ebc_lowsp (+space 0x40), ebc_text (letters, digits, space, LF 0x25, common punctuation).
Self-tests: planted texts encoded under each family (ASCII and EBCDIC) are recovered."""
import sys, time, json, math, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import to_bytes, text_to_digits
from h4_topdown import TD, td_insert, td_perm, STRS, CHARSETS
import string

def cs_from_codec(cp, chars):
    out = set()
    for b in range(256):
        try:
            if bytes([b]).decode(cp) in chars: out.add(b)
        except Exception:
            pass
    return out
CHARSETS['ebc_lower'] = cs_from_codec('cp273', string.ascii_lowercase)
CHARSETS['ebc_lowsp'] = cs_from_codec('cp273', string.ascii_lowercase + ' ')
CHARSETS['ebc_text'] = cs_from_codec('cp273', string.ascii_letters + string.digits + " \n.,;:!?'\"-()/")
assert len(CHARSETS['ebc_lower']) == 26 and 0x25 in CHARSETS['ebc_text']


def td_zero_any(digs, cs, Kmax, max_nodes=50_000_000, max_sol=20):
    n = len(digs); T = TD(n, cs, max_nodes); dv = [int(c) for c in digs]
    sys.setrecursionlimit(10000)
    def go(t, A, kd, K):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        if t == n:
            if all(c in cs for c in to_bytes(A)): T.sols.append((A, K))
            return
        r = n - t - 1
        nA = A + dv[t] * T.p10[r]; nk = T.check(nA, r, kd)
        if nk >= 0: go(t + 1, nA, nk, K)
        if t > 0 and K < Kmax:
            nk = T.check(A, r, kd)
            if nk >= 0: go(t + 1, A, nk, K + 1)
        if T.trunc or len(T.sols) >= max_sol: return
    go(0, 0, 0, 0)
    return T


def expected_false_T3(n, K, cs):
    nbytes = math.ceil(n * math.log2(10) / 8)
    return sum(math.comb(n - 1, k) for k in range(K + 1)) * (len(cs) / 256) ** nbytes


def kmax_for(n, cs, target=0.05):
    K = 0
    while K < n - 1 and expected_false_T3(n, K + 1, cs) < target: K += 1
    return K


def ebc(text):
    return text.encode('cp273')


def selftest():
    rnd = random.Random(6)
    for enc in ('ascii', 'ebc'):
        for Tt in ('lastwordsbeforearchichoice', 'theseedisplanted'):
            raw = Tt.encode() if enc == 'ascii' else ebc(Tt)
            D = str(int.from_bytes(raw, 'big'))
            # T3 plant: zeros disguised as random nonzero letters
            disg = ''.join(str(rnd.randint(1, 9)) if ch == '0' else ch for ch in D)
            cs = CHARSETS['lower' if enc == 'ascii' else 'ebc_lower']
            T = td_zero_any(disg, cs, Kmax=len(D))
            hit = any(to_bytes(v) == raw for v, k in T.sols)
            print(f'T3 selftest {enc} {Tt!r} zeros={D.count("0")} nsol={len(T.sols)} recovered={hit} nodes={T.nodes}', flush=True)
            assert hit
            # T1 plant (EBCDIC only; ASCII covered in h4)
            if enc == 'ebc':
                T = td_insert(D.replace('0', ''), D.count('0'), cs, max_sol=100)
                hit = any(to_bytes(v) == raw for v in T.sols)
                print(f'T1 selftest ebc {Tt!r} nsol={len(T.sols)} recovered={hit} nodes={T.nodes}', flush=True)
                assert hit
    # T2 EBCDIC plant
    raw = ebc('Raising the stakes, without extra chances of winning.')
    D = str(int.from_bytes(raw, 'big')); perm = list('abcdefghi'); rnd.shuffle(perm)
    mp = {str(d): perm[d - 1] for d in range(1, 10)}; mp['0'] = 'g' if 'g' != mp['7'] else 'c'
    M = mp['0']; s = ''.join(mp[ch] for ch in D)
    T = td_perm(s, M, CHARSETS['ebc_text'], max_nodes=50_000_000, max_sol=500)
    hit = any(to_bytes(v) == raw for v, a in T.sols)
    print(f'T2 selftest ebc nsol={len(T.sols)} recovered={hit} nodes={T.nodes}', flush=True)
    assert hit


def run(out):
    rows = []
    def emit(row):
        rows.append(row); print(('!!! ' if row.get('nsol') else '    ') + json.dumps(row)[:380], flush=True)
    for name, s in STRS.items():
        digs = ''.join(str(ord(c) - 96) for c in s); n = len(digs)
        # T3
        for csn in ('lower', 'lowsp', 'textish', 'printnl', 'ebc_lower', 'ebc_lowsp', 'ebc_text'):
            cs = CHARSETS[csn]
            K = n if csn in ('lower', 'lowsp', 'ebc_lower', 'ebc_lowsp') else kmax_for(n, cs)
            t0 = time.time(); T = td_zero_any(digs, cs, K)
            emit(dict(test='T3', s=name, cs=csn, Kmax=K, expected_false=expected_false_T3(n, K, cs), nodes=T.nodes, trunc=T.trunc,
                      deepest_top_bytes=T.deepest, nsol=len(T.sols), sols=[(to_bytes(v)[:60].decode('latin1'), k) for v, k in T.sols[:3]],
                      secs=round(time.time() - t0, 1)))
        # T1 with EBCDIC + textish/printnl (Z bounded by expected-false)
        for csn in ('ebc_lower', 'ebc_lowsp', 'ebc_text', 'textish', 'printnl'):
            cs = CHARSETS[csn]; tot = 0; sols = []; trunc = False; deep = 0; expect = 0.0; Zs = []
            for Z in range(0, 131 if 'FAED' in name else 31):
                nbytes = math.ceil((n + Z) * math.log2(10) / 8)
                e = math.comb(n + Z - 1, Z) * (len(cs) / 256) ** nbytes
                if csn in ('ebc_text', 'textish', 'printnl') and e > 0.01: continue
                T = td_insert(digs, Z, cs, max_nodes=20_000_000)
                tot += T.nodes; trunc |= T.trunc; deep = max(deep, T.deepest); expect += e; Zs.append(Z)
                sols += [(Z, to_bytes(v)[:60].decode('latin1')) for v in T.sols[:3]]
            emit(dict(test='T1', s=name, cs=csn, Zs=f'{min(Zs) if Zs else None}..{max(Zs) if Zs else None} ({len(Zs)})', expected_false=expect,
                      nodes=tot, trunc=trunc, deepest_top_bytes=deep, nsol=len(sols), sols=sols[:3]))
    for name in ('FAED', 'FAED_rev'):
        for csn in ('ebc_lower', 'ebc_text'):
            t0 = time.time(); T = td_perm(STRS[name], 'g', CHARSETS[csn], max_nodes=300_000_000)
            emit(dict(test='T2', s=name, M='g', cs=csn, nodes=T.nodes, trunc=T.trunc, deepest_top_bytes=T.deepest, nsol=len(T.sols),
                      sols=[to_bytes(v)[:60].decode('latin1') for v, a in T.sols[:3]], secs=round(time.time() - t0, 1)))
    json.dump(rows, open(out, 'w'), indent=0)


if __name__ == '__main__':
    if sys.argv[1] == 'selftest': selftest()
    else: run(sys.argv[2])
