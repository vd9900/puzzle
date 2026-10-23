"""EBCDIC (cp273) re-run of the bottom-up families: single-letter zero disguise (H5) and dbbi marker reinsertion (H1b).
Self-test: planted cp273 text with markers/zero disguise recovered by the same pipeline."""
import sys, json, time, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import Search, to_bytes, DIG
from h5_topdown_more import CHARSETS
from h5_zero_disguise import slots_for
from h1b_markers import configs, opts_for, build, tokens, segmentations, P
from common_dc import DBBI, R60, R61, FAED


def selftest():
    T = 'reinsertingtheprimebasics'
    raw = T.encode('cp273'); D = str(int.from_bytes(raw, 'big'))
    letters = []; i = 0; lp = 1
    while i < len(D):
        if lp in P:
            if D[i] == '5': letters.append('be'); i += 1
            else: letters.append('b')
        else:
            letters.append('g' if D[i] == '0' else 'abcdefghi'[int(D[i]) - 1]); i += 1
        lp += 1
    S = ''.join(letters); found = False
    for t in segmentations(S):
        toks = [(tok, (j + 1) in P, None) for j, tok in enumerate(t)]
        slots, classes = build(toks, 'tok', 'gd', False, opts_for('L83', 'tok'))
        se = Search(slots, classes, CHARSETS['ebc_text'], max_nodes=20_000_000, max_solutions=500, min_bytes=8).run()
        found |= any(to_bytes(v) == raw for v, a, c in se.solutions)
    print('ebcdic pipeline selftest recovered', found, flush=True); assert found


def main(out):
    rows = []
    strs = {'DBBI': DBBI, 'R60': R60, 'R61': R61, 'FAED': FAED}
    for name, s0 in strs.items():
        for rev in (False, True):
            s = s0[::-1] if rev else s0
            for L in 'abcdefghi':
                for csn in ('ebc_lower', 'ebc_text'):
                    se = Search(slots_for(s, L), {}, CHARSETS[csn], max_nodes=20_000_000, max_solutions=20, min_bytes=4).run()
                    rows.append(dict(test='H5ebc', s=name, rev=rev, L=L, cs=csn, nodes=se.nodes, trunc=se.truncated,
                                     deepest=se.deepest, nsol=len(se.solutions),
                                     sols=[to_bytes(v)[:60].decode('cp273', 'replace') for v, a, c in se.solutions[:3]]))
    print('H5ebc', len(rows), 'sols', sum(r['nsol'] for r in rows), 'trunc', sum(r['trunc'] for r in rows), flush=True)
    t0 = time.time()
    for (tokname, classing, resid, rev) in configs():
        opts = opts_for(tokname, classing)
        slots, classes = build(tokens(tokname), classing, resid, rev, opts)
        se = Search(slots, classes, CHARSETS['ebc_text'], max_nodes=30_000_000, max_solutions=50, min_bytes=8).run()
        rows.append(dict(test='H1b_ebc', tok=tokname, classing=classing, resid=resid, rev=rev, nodes=se.nodes, trunc=se.truncated,
                         deepest=se.deepest, nsol=len(se.solutions),
                         sols=[(a, to_bytes(v)[:60].decode('cp273', 'replace')) for v, a, c in se.solutions[:3]]))
    h = [r for r in rows if r['test'] == 'H1b_ebc']
    print('H1b_ebc', len(h), 'sols', sum(r['nsol'] for r in h), 'trunc', sum(r['trunc'] for r in h), 'maxdeep', max(r['deepest'] for r in h),
          f'{time.time() - t0:.0f}s', flush=True)
    for r in rows:
        if r['nsol']: print('!!!', json.dumps(r)[:300])
    json.dump(rows, open(out, 'w'), indent=0)


if __name__ == '__main__':
    selftest()
    main(sys.argv[1])
