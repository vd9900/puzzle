"""Runs the turning-grille readings on speech / faed / page stream; planted self-tests; random-grille controls."""
import sys, json, random, time
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c40/grille')
from grille import *
from multiprocessing import Pool

SPEECH = ''.join(ch for ch in open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read() if ch.isalpha()).lower()
assert len(SPEECH) == 1539
STREAM = DBBI + BIN1 + FAED; assert len(STREAM) == 765
SP_OFFS = sorted(set(range(0, 1344, 196)) | set(range(0, 196, 4)))
FA_OFFS = list(range(0, 375)) + [392]
ST_OFFS = list(range(0, 570)) + [588]
NAT = [('FAED', FAED, 0), ('FAED', FAED, 196), ('FAED', FAED, 392),
       ('STREAM', STREAM, 0), ('STREAM', STREAM, 196), ('STREAM', STREAM, 392), ('STREAM', STREAM, 588)]


def apply(text, off, idx):
    return ''.join(text[off + i] for i in idx if off + i < len(text))


def run_grille(args):
    """returns per-grille-subset best metrics (speech English score; faed/stream leading-lowercase bytes; full hits)"""
    grilles, tag, do_dfs = args
    R = make_readers(grilles)
    res = {g: dict(sp_best=-99, sp_arg=None, fa_lead=0, fa_arg=None, st_lead=0, st_arg=None, zhits=[], dfs_deep=0,
                   dfs_sols=0, dfs_trunc=False) for g in grilles}
    for key, idx in R:
        g = key[0]; r = res[g]
        for off in SP_OFFS:
            t = apply(SPEECH, off, idx); sc = qscore(t)
            if sc > r['sp_best']: r['sp_best'] = sc; r['sp_arg'] = (key, off, t)
        for name, text, offs, fld in (('FAED', FAED, FA_OFFS, 'fa'), ('STREAM', STREAM, ST_OFFS, 'st')):
            for off in offs:
                t = apply(text, off, idx)
                b, lowfrac, allprint = zdirect(t)
                ll = lead_lower(t)
                if ll > r[fld + '_lead']: r[fld + '_lead'] = ll; r[fld + '_arg'] = (key, off, b[:12].hex())
                if lowfrac == 1.0 or allprint: r['zhits'].append((name, key, off, b.decode('latin1')))
        if do_dfs:
            for name, text, off in NAT:
                t = apply(text, off, idx)
                n, deep, trunc, sols = zero_dfs(t)
                r['dfs_deep'] = max(r['dfs_deep'], deep); r['dfs_trunc'] |= trunc; r['dfs_sols'] += n
                if n: r['zhits'].append(('DFS', name, key, off, [repr(s) for s in sols]))
    return tag, res


def selftests():
    rnd = random.Random(7)
    R = dict(make_readers(GRILLES))
    # (a) planted English through the real grille (all24, cw, s=0, row, row fill) into a speech-like window
    key = ('all24', 'cw', 0, 'row', 'row'); idx = R[key]
    msg = ('theseedisplantedandthepasswordisthenameoftherabbitwhoranoutoftimeinthesquaresoftheboard' * 2)[:96]
    win = list(SPEECH[196:392]); rnd.shuffle(win)
    for i, ch in zip(idx, msg): win[i] = ch
    win = ''.join(win)
    best = max((qscore(apply(win, 0, ix)), k) for k, ix in R.items())
    bt = apply(win, 0, R[best[1]]); L = len(idx) // 4
    print('selftest English plant: best', best, ' msg score', round(qscore(msg), 3), flush=True)
    assert any(bt == msg[k * L:] + msg[:k * L] for k in range(4))   # block-cyclic shifts are equivalent readings
    # (b) planted z-method text with zeros deleted (96 remaining digits) into an a..i window
    base = 'raisingthestakeswithoutextrachancesofwinningthehalfandbetterhalf'
    found = None
    for j in range(0, 20):
        for L in range(38, 48):
            txt = base[j:j + L]; d = str(int.from_bytes(txt.encode(), 'big')); dz = d.replace('0', '')
            if len(dz) == 96 and found is None: found = (txt, d, dz)
    txt, d, dz = found
    assert len(dz) == 96, 'no planted length 96'
    s = ''.join('abcdefghi'[int(c) - 1] for c in dz)
    win = [rnd.choice('abcdefghi') for _ in range(196)]
    key2 = ('all24', 'ccw', 2, 'spiral', 'spiral'); idx2 = R[key2]
    for i, ch in zip(idx2, s): win[i] = ch
    t = apply(''.join(win), 0, idx2); assert t == s
    n, deep, trunc, sols = zero_dfs(t, Zmax=max(12, d.count('0')))
    ok = any(x[2] == txt.encode() for x in sols) if n else False
    print(f'selftest z-plant: Z={d.count("0")} nsol={n} deep={deep} recovered={ok} sols={sols[:2]}', flush=True)
    assert ok
    # (c) direct decode path: planted text whose digits have no zeros under 'o' allowance
    so = ''.join('abcdefghio'[int(c) - 1] for c in d)
    assert zdirect(so)[0] == txt.encode()
    print('selftests passed', flush=True)


if __name__ == '__main__':
    t0 = time.time()
    selftests()
    NCTRL = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    NDFS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    jobs = [(GRILLES, 'REAL', True)]
    for i in range(NCTRL):
        jobs.append((random_grille(random.Random(1000 + i)), f'CTRL{i}', i < NDFS))
    with Pool(4) as P:
        out = P.map(run_grille, jobs, chunksize=1)
    json.dump(out, open(OUT + 'results.json', 'w'), indent=0, default=str)
    real = dict(out)['REAL']; ctrls = [r for t, r in out if t != 'REAL']
    summ = {}
    for g in GRILLES:
        row = {}
        for m in ('sp_best', 'fa_lead', 'st_lead'):
            cv = sorted(c[g][m] for c in ctrls)
            row[m] = dict(real=real[g][m], ctrl_max=cv[-1], ctrl_mean=round(sum(cv) / len(cv), 4),
                          n_ctrl_ge_real=sum(v >= real[g][m] for v in cv), n_ctrl=len(cv))
        dv = [c[g]['dfs_deep'] for c in ctrls[:NDFS]]
        row['dfs'] = dict(real_deep=real[g]['dfs_deep'], real_sols=real[g]['dfs_sols'], real_trunc=real[g]['dfs_trunc'],
                          ctrl_deep=dv, ctrl_sols=[c[g]['dfs_sols'] for c in ctrls[:NDFS]])
        row['real_zhits'] = real[g]['zhits'][:5]; row['ctrl_zhits'] = sum(len(c[g]['zhits']) for c in ctrls)
        row['sp_arg'] = real[g]['sp_arg']; row['fa_arg'] = real[g]['fa_arg']; row['st_arg'] = real[g]['st_arg']
        summ[g] = row
        print(g, json.dumps(row, default=str)[:900], flush=True)
    json.dump(summ, open(OUT + 'summary.json', 'w'), indent=1, default=str)
    print('secs', round(time.time() - t0, 1))
