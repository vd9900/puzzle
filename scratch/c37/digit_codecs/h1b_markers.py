"""H1b: z-method with dbbi marker tokens REINSERTED as class-consistent digit strings (+ optional zero disguise).

Tokenizations: L83/L84 = prime-logical segmentations (23 markers at prime positions);
               G = global (every 'be' digraph and every other lone 'b' is a marker; 25 markers = 15 b + 10 be).
Classing:  one (all markers same string), tok ('b' vs 'be'), col (image colour of the k-th prime marker: B/Y/W).
Residual:  id (a=1..i=9), a0 (a=0..i=8), Ld (letter L may independently be 0 at each occurrence; L in a..i).
Direction: forward / reversed digit string.
Oracle:    byte-local DFS (engine.Search): every byte of the big-endian integer in printnl; solutions then
           classified (lower/hex/b58/b64...). Exhaustive unless trunc=1.
Extra (W): for id/a0 residuals, every class assignment's integer is tested as a raw WIF payload
           (37/38 bytes, 0x80 prefix, double-SHA256 checksum) and for the 'Salted__' prefix (top-down oracle).
Self-tests: engine class-recovery test + full-pipeline plant (synthetic dbbi-like string)."""
import sys, time, json, random, hashlib, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import Search, CHARSETS, to_bytes, text_to_digits, DIG
from common_dc import DBBI, P, segmentations, COLOURS

OPTS_FULL = tuple(dict.fromkeys([''] + [str(d) for d in range(10)] + ['%02d' % d for d in range(100)] +
                                ['1812', '182', '218', '125', '40', '92', '65', '27']))
OPTS_SMALL = tuple(dict.fromkeys([''] + [str(d) for d in range(10)] + ['00', '25', '23', '52', '32', '20', '50']))


def tokens(tokname, s=DBBI):
    """returns list of (tok, is_marker, marker_index)"""
    if tokname in ('L83', 'L84', 'S'):
        segs = segmentations(s)
        if tokname == 'S':
            t = segs[0]
        else:
            t = [x for x in segs if len(x) == int(tokname[1:])][0]
        out = []; m = 0
        for i, tok in enumerate(t):
            if (i + 1) in P: out.append((tok, True, m)); m += 1
            else: out.append((tok, False, None))
        return out
    if tokname == 'G':
        out = []; i = 0; m = 0
        while i < len(s):
            if s[i] == 'b':
                if i + 1 < len(s) and s[i + 1] == 'e': out.append(('be', True, m)); i += 2
                else: out.append(('b', True, m)); i += 1
                m += 1
            else:
                out.append((s[i], False, None)); i += 1
        return out
    raise ValueError(tokname)


def build(toks, classing, resid, rev, opts):
    slots = []
    for tok, mk, m in toks:
        if mk:
            if classing == 'tok': name = 'tok_' + tok
            elif classing == 'col': name = 'col_' + COLOURS[m]
            else: name = 'one'
            slots.append(('cls', name))
        else:
            for ch in tok:
                if resid == 'id': slots.append(('fix', DIG[ch]))
                elif resid == 'a0': slots.append(('fix', str(int(DIG[ch]) - 1)))
                elif resid.endswith('d'):
                    slots.append(('ind', (DIG[ch], '0')) if ch == resid[0] else ('fix', DIG[ch]))
    if rev:
        slots = [(k, a[::-1] if k == 'fix' else (tuple(x[::-1] for x in a) if k == 'ind' else a)) for k, a in slots[::-1]]
    classes = {n: opts for k, n in slots if k == 'cls'}
    return slots, classes


def classify(bs):
    return [n for n, cs in CHARSETS.items() if all(c in cs for c in bs)]


def pipeline_selftest():
    """Synthetic dbbi-like string: planted text -> digits; zeros written as 'g'; markers at prime logical
    positions: 'be' stands for digit '5' (emitted when the next planted digit is 5), 'b' stands for nothing.
    The full pipeline (segmentation -> slots -> search) must recover the text."""
    ok = 0
    for T in ('reinsertingtheprimebasicsrequired', 'someofthecharactersarezeroedout'):
        D = text_to_digits(T)
        letters = []; i = 0; lp = 1
        while i < len(D):
            if lp in P:
                if D[i] == '5': letters.append('be'); i += 1
                else: letters.append('b')
            else:
                letters.append('g' if D[i] == '0' else 'abcdefghi'[int(D[i]) - 1]); i += 1
            lp += 1
        S = ''.join(letters)
        segs = segmentations(S)
        found = False
        for t in segs:
            toks = [(tok, (j + 1) in P, None) for j, tok in enumerate(t)]
            slots, classes = build(toks, 'tok', 'gd', False, OPTS_FULL)
            se = Search(slots, classes, CHARSETS['printnl'], max_nodes=20_000_000, max_solutions=500, min_bytes=8).run()
            sols = [(to_bytes(v), a) for v, a, c in se.solutions]
            if any(b == T.encode() for b, a in sols): found = True
            print(f'pipeline selftest {T!r}: segs={len(segs)} nsol={len(sols)} recovered={found} nodes={se.nodes}', flush=True)
        ok += found
    assert ok == 2


def wif_check(n):
    nb = (n.bit_length() + 7) // 8
    if nb not in (37, 38): return False
    b = n.to_bytes(nb, 'big')
    if b[0] != 0x80: return False
    return hashlib.sha256(hashlib.sha256(b[:-4]).digest()).digest()[:4] == b[-4:]


def wif_family(tokname, classing, resid, rev, opts):
    """enumerate all class assignments (no 'ind' slots) and test WIF / Salted__ top-down."""
    slots, classes = build(tokens(tokname), classing, resid, rev, opts)
    names = sorted(classes)
    cnt = 0; hits = []
    for combo in itertools.product(opts, repeat=len(names)):
        a = dict(zip(names, combo))
        dg = ''.join(arg if k == 'fix' else a[arg] for k, arg in slots)
        if not dg or dg.lstrip('0') == '': continue
        n = int(dg); cnt += 1
        if wif_check(n): hits.append(('WIF', a))
        b = to_bytes(n)
        if b.startswith(b'Salted__'): hits.append(('Salted', a))
    return cnt, hits


def configs():
    out = []
    for tokname in ('L83', 'L84', 'G'):
        for classing in (('one', 'tok', 'col') if tokname != 'G' else ('one', 'tok')):
            for resid in ['id', 'a0'] + [L + 'd' for L in 'abcdefghi']:
                for rev in (False, True):
                    out.append((tokname, classing, resid, rev))
    return out


def opts_for(tokname, classing):
    if classing == 'col' or (tokname == 'G' and classing == 'tok'): return OPTS_SMALL
    return OPTS_FULL


def run_shard(shard, nshards, max_nodes, outpath):
    rows = []
    t0 = time.time()
    for ci, (tokname, classing, resid, rev) in enumerate(configs()):
        if ci % nshards != shard: continue
        opts = opts_for(tokname, classing)
        slots, classes = build(tokens(tokname), classing, resid, rev, opts)
        se = Search(slots, classes, CHARSETS['printnl'], max_nodes=max_nodes, max_solutions=200, min_bytes=8).run()
        sols = [{'assign': a, 'n_ind_zero': sum(1 for _, o in c if o == '0'), 'bytes': to_bytes(v).decode('latin1'),
                 'cs': classify(to_bytes(v))} for v, a, c in se.solutions]
        nder = len(opts) ** len(classes)
        row = dict(tok=tokname, classing=classing, resid=resid, rev=rev, n_class_assign=nder, nodes=se.nodes,
                   trunc=se.truncated, deepest=se.deepest, nsol=len(sols), sols=sols[:20])
        if resid in ('id', 'a0'):
            cnt, hits = wif_family(tokname, classing, resid, rev, opts)
            row['wif_tested'] = cnt; row['wif_hits'] = hits
        rows.append(row)
        print(('!!! ' if sols or row.get('wif_hits') else '    ') +
              f'{tokname} {classing:3s} {resid:3s} rev={int(rev)} assigns={nder} nodes={se.nodes} trunc={int(se.truncated)} '
              f'deepest={se.deepest} nsol={len(sols)} wif={row.get("wif_tested", "-")}/{len(row.get("wif_hits", []))} t={time.time() - t0:.0f}s', flush=True)
        for so in sols[:3]: print('      ', so['assign'], so['cs'], repr(so['bytes'][:80]))
    json.dump(rows, open(outpath, 'w'), indent=0)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'selftest':
        import h1_marker_classes
        h1_marker_classes.selftest()
        pipeline_selftest()
    elif cmd == 'count':
        print(len(configs()), sum(len(opts_for(t, c)) ** len(build(tokens(t), c, r, v, opts_for(t, c))[1]) for t, c, r, v in configs()))
    else:
        run_shard(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
