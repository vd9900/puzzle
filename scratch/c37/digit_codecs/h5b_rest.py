"""Remainder of h5_topdown_more for faed: T3 on FAED_rev; T1 with text charsets restricted to the plausible zero count
Z in 39..90 (decimal text has ~10% zeros: Z ~ 63 +- 8, +-3 sigma) with 5M-node cap per Z; T2 (perm+g-merge) in EBCDIC."""
import sys, json, math, time
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from h5_topdown_more import CHARSETS, STRS, td_zero_any, expected_false_T3, kmax_for
from h4_topdown import td_insert, td_perm
from engine import to_bytes
rows = []
def emit(row):
    rows.append(row); print(('!!! ' if row.get('nsol') else '    ') + json.dumps(row)[:380], flush=True)
for name in ('FAED_rev',):
    digs = ''.join(str(ord(c) - 96) for c in STRS[name]); n = len(digs)
    for csn in ('lower', 'lowsp', 'textish', 'printnl', 'ebc_lower', 'ebc_lowsp', 'ebc_text'):
        cs = CHARSETS[csn]; K = n if csn in ('lower', 'lowsp', 'ebc_lower', 'ebc_lowsp') else kmax_for(n, cs)
        T = td_zero_any(digs, cs, K)
        emit(dict(test='T3', s=name, cs=csn, Kmax=K, expected_false=expected_false_T3(n, K, cs), nodes=T.nodes, trunc=T.trunc,
                  deepest_top_bytes=T.deepest, nsol=len(T.sols)))
for name in ('FAED', 'FAED_rev'):
    digs = ''.join(str(ord(c) - 96) for c in STRS[name]); n = len(digs)
    css = ('ebc_text', 'textish', 'printnl') if name == 'FAED' else ('ebc_lower', 'ebc_lowsp', 'ebc_text', 'textish', 'printnl')
    for csn in css:
        cs = CHARSETS[csn]; tot = 0; sols = []; ntr = 0; deep = 0; expect = 0.0; Zs = []
        zr = range(39, 91) if csn in ('ebc_text', 'textish', 'printnl') else range(0, 131)
        t0 = time.time()
        for Z in zr:
            nbytes = math.ceil((n + Z) * math.log2(10) / 8)
            e = math.comb(n + Z - 1, Z) * (len(cs) / 256) ** nbytes
            T = td_insert(digs, Z, cs, max_nodes=5_000_000)
            tot += T.nodes; ntr += T.trunc; deep = max(deep, T.deepest); expect += e; Zs.append(Z)
            sols += [(Z, to_bytes(v)[:60].decode('latin1')) for v in T.sols[:3]]
        emit(dict(test='T1', s=name, cs=csn, Zs=f'{min(Zs)}..{max(Zs)}', expected_false=expect, nodes=tot, n_trunc_Z=ntr,
                  deepest_top_bytes=deep, nsol=len(sols), sols=sols[:3], secs=round(time.time() - t0)))
for name in ('FAED', 'FAED_rev'):
    for csn in ('ebc_lower', 'ebc_text'):
        T = td_perm(STRS[name], 'g', CHARSETS[csn], max_nodes=300_000_000)
        emit(dict(test='T2', s=name, M='g', cs=csn, nodes=T.nodes, trunc=T.trunc, deepest_top_bytes=T.deepest, nsol=len(T.sols)))
json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h5b_rest.json', 'w'), indent=0)
