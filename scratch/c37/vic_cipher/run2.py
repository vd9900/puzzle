# Main structural sweep: every principled VIC derivation (phrase x date x personal number x keygroup reading x map x
# transposition variant) applied to faed, 3 shuffled-faed controls and 2 planted VIC ciphertexts.
# Detector = serial-structure z of H(next|prev) on the un-transposed 565-letter body (validated in t_basic.py), plus
# adjacent-equal z (number-mode triples). No AES oracle involved.
import sys, json, time, random, argparse
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/vic_cipher')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
sys.path.insert(0, '.')
import numpy as np
import vic, vicfast as V, cands
from multiprocessing import Pool

FAED = open('faed.txt').read().strip() if __import__('os').path.exists('faed.txt') else None
if FAED is None:
    from common import FAED

TXT = None
def corpus():
    global TXT
    if TXT is None:
        import re
        p = 'carroll.txt' if __import__('os').path.exists('carroll.txt') else '/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt'
        TXT = re.sub('[^A-Z]', '', open(p).read().upper())
    return TXT

RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
SET = 'main'
MODESET = None
DATESET = None
MAPSET = None

def make_targets_set(which):
    import vicfast as V2
    T = {}
    if which == 'rev':
        T['faed_rev'] = FAED[::-1]
        for i in range(2):
            l = list(FAED); random.Random(200 + i).shuffle(l); T['ctrlrev%d' % i] = ''.join(l)
        p, st, k = V2.plant(corpus()[80000:], 'WAKEUPNEOTHEMATRIXHA', '9112001', 11, '24680', mode='disrupted', zero_letter='g')
        T['plant_rev'] = p   # processed string (the observed reversed text would be p[::-1])
    elif which == 'gap0':
        T['faed'] = FAED
        for i in range(2):
            l = list(FAED); random.Random(400 + i).shuffle(l); T['ctrlg%d' % i] = ''.join(l)
        p, st, k = V2.plant(corpus()[60000:], 'THESEEDISPLANTEDWHEN', '110901', 9, '13579', mode='disrupted0', zero_letter='g')
        T['plant_gap0'] = p
    elif which == 'res60':
        T['res60'] = RES60
        for i in range(3):
            l = list(RES60); random.Random(300 + i).shuffle(l); T['ctrl60_%d' % i] = ''.join(l)
        p, st, k = V2.plant(corpus()[40000:], 'FOLLOWTHEWHITERABBIT', '1192001', 6, '47205', total=60, zero_letter='g')
        T['plant60'] = p
    return T

def make_targets():
    if SET != 'main':
        return make_targets_set(SET)
    return make_targets_main()

def make_targets_main():
    T = {'faed': FAED}
    for i in range(3):
        l = list(FAED); random.Random(100 + i).shuffle(l); T['ctrl%d' % i] = ''.join(l)
    txt = corpus()
    p1, st1, k1 = V.plant(txt[20000:], 'IVEBEENWAITINGFORYOU', '9112001', 13, '50731', mode='disrupted', zero_letter='g')
    T['plant1'] = p1
    # plant2: English with an embedded 77-digit number in VIC number mode (tripled digits), plain double columnar,
    # zero hidden in letter b; keygroup contains a zero.
    rnd = random.Random(9)
    k2 = vic.derive('THEFLOWERBLOSSOMSTHR', '110901', 4, '27094')
    enc, dec, esc = vic.vic_board(k2['S'])
    num = ''.join(rnd.choice('0123456789') for _ in range(77))
    st = enc['/'] + ''.join(d * 3 for d in num) + enc['/']
    i = 31000
    while len(st) < 565:
        st += enc[txt[i]]; i += 1
    st = st[:565]
    t1 = ''.join(st[j] for j in V._cp(565, tuple(k2['Q'])))
    t2 = ''.join(t1[j] for j in V._cp(565, tuple(k2['R'])))
    groups = [t2[j:j + 5] for j in range(0, 565, 5)]
    groups.insert(114 - 1, '27094')
    ct = ''.join(groups)
    m = {str(i + 1): c for i, c in enumerate(V.LET)}; m['0'] = 'b'
    T['plant2'] = ''.join(m[d] for d in ct)
    return T

PH = cands.usable_phrases()
MODES = ['disrupted', 'plain']
MAPS = ['a1', 'a0']
P32TAB = V.board_tables(kind='p32')

def prep(T):
    """per target, per possible keygroup group index: body array + null stats."""
    info = {}
    for name, s in T.items():
        info[name] = {}
        allpos = set()
        for dtag, date in DATES_USED():
            for ptag, gi in V.kg_positions(date, len(s) // 5): allpos.add(gi)
        for gi in sorted(allpos):
            body = s[:5 * gi] + s[5 * gi + 5:]
            kg = s[5 * gi:5 * gi + 5]
            a = V.to_idx(body)
            mu, sd = V.null_stats(a, 9, trials=300, seed=gi)
            # adjacent-equal null
            r = np.random.default_rng(gi + 7); b = a.copy(); eq = []
            for _ in range(300):
                r.shuffle(b); eq.append(int((b[1:] == b[:-1]).sum()))
            info[name][gi] = (a, kg, mu, sd, float(np.mean(eq)), float(np.std(eq)))
    return info

def DATES_USED():
    return [d for d in cands.DATES if DATESET is None or d[0] in DATESET]

G = {}
def init(T, setname='main', dateset=None, mapset=None, modeset=None):
    global SET, DATESET, MAPSET, MODESET
    SET, DATESET, MAPSET, MODESET = setname, dateset, mapset, modeset
    G['T'] = T
    G['info'] = prep(T)

def work(pi):
    ptag, phrase = PH[pi]
    T = G['T']; info = G['info']
    recs = []
    n = 0
    for name in T:
        nb = len(T[name]) - 5
        for dtag, date in DATES_USED():
            for postag, gi in V.kg_positions(date, len(T[name]) // 5):
                a, kgl, mu, sd, emu, esd = info[name][gi]
                seen = set()
                for mp in (MAPSET or MAPS):
                    for rdesc, kgd in V.kg_readings(kgl, mp):
                        if kgd in seen: continue   # identical digits -> identical keys
                        seen.add(kgd)
                        for pnum in cands.PNUMS:
                            k = vic.derive(phrase, date, pnum, kgd)
                            Q, R = tuple(k['Q']), tuple(k['R'])
                            if len(Q) != k['wa'] or len(R) != k['wb'] or len(Q) < 2 or len(R) < 2:
                                continue   # widths exceed the 50-digit block: not a valid VIC key
                            for mode in (MODESET or MODES):
                                idx = V.untranspose_index(nb, Q, R, mode)
                                u = a[idx]
                                z = (V.hcond_arr(u, 9) - mu) / sd
                                ez = (int((u[1:] == u[:-1]).sum()) - emu) / esd
                                ds = V.letters_to_digit_list(u, mp)
                                S = k['S']
                                lm1 = V.qscore(V.cb_decode_digits(ds, V.board_tables(S, 'atonesir')))
                                lm2 = V.qscore(V.cb_decode_digits(ds, P32TAB))
                                lm3 = V.qscore(V.cb_decode_digits(ds, V.board_tables(S, 'p32S')))
                                n += 1
                                recs.append((round(float(z), 3), round(float(ez), 3), name, ptag, dtag, postag, gi, mp, rdesc, kgd, pnum, mode,
                                             round(lm1, 3), round(lm2, 3), round(lm3, 3)))
    # compact: per target keep z/ez arrays and top records only
    comp = {}
    for name in T:
        rs = [r for r in recs if r[2] == name]
        arr = np.array([[r[0], r[1], r[12], r[13], r[14]] for r in rs], dtype=np.float32).reshape(-1, 5)
        tops = {'z': sorted(rs, key=lambda r: r[0])[:40], 'ez': sorted(rs, key=lambda r: -r[1])[:20],
                'lm_at': sorted(rs, key=lambda r: -r[12])[:20], 'lm_p32': sorted(rs, key=lambda r: -r[13])[:20],
                'lm_p32S': sorted(rs, key=lambda r: -r[14])[:20]}
        comp[name] = (arr, tops)
    return comp, n

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--procs', type=int, default=2); ap.add_argument('--out', default='main_results.json')
    ap.add_argument('--set', default='main'); ap.add_argument('--dates', default=''); ap.add_argument('--maps', default='')
    ap.add_argument('--modes', default='')
    a = ap.parse_args()
    SET = a.set
    DATESET = set(a.dates.split(',')) if a.dates else None
    MAPSET = a.maps.split(',') if a.maps else None
    MODESET = a.modes.split(',') if a.modes else None
    T = make_targets()
    t0 = time.time()
    total = 0; A = {n: [] for n in T}; TOPS = {n: {} for n in T}; done = 0
    with Pool(a.procs, initializer=init, initargs=(T, SET, DATESET, MAPSET, MODESET)) as pool:
        for comp, n in pool.imap_unordered(work, range(len(PH))):
            total += n; done += 1
            for name, (arr, tops) in comp.items():
                A[name].append(arr)
                for kk, v in tops.items(): TOPS[name].setdefault(kk, []).extend(v)
            print('phrases done', done, 'derivs', total, 'elapsed %.0f' % (time.time() - t0), flush=True)
    out = {'n_phrases': len(PH), 'total_derivations': total, 'targets': {}}
    keyidx = {'z': 0, 'ez': 1, 'lm_at': 12, 'lm_p32': 13, 'lm_p32S': 14}
    for name in T:
        arr = np.concatenate(A[name])
        d = dict(n=int(len(arr)))
        for j, st in enumerate(['z', 'ez', 'lm_at', 'lm_p32', 'lm_p32S']):
            col = arr[:, j]
            d[st] = dict(min=float(col.min()), max=float(col.max()), mean=float(col.mean()), sd=float(col.std()),
                         q0001=float(np.quantile(col, 0.0001)), q9999=float(np.quantile(col, 0.9999)))
            sgn = 1 if st == 'z' else -1
            d['top_' + st] = sorted(TOPS[name][st], key=lambda r: sgn * r[keyidx[st]])[:30]
        out['targets'][name] = d
        print(name, 'n', len(arr), ' '.join('%s[min %.2f max %.2f]' % (st, d[st]['min'], d[st]['max']) for st in ['z', 'ez', 'lm_at', 'lm_p32', 'lm_p32S']))
        print('   best z:', d['top_z'][:2])
        print('   best lm_at:', d['top_lm_at'][:1])
    json.dump(out, open(a.out, 'w'), indent=1)
