"""Cycle 42 test0: replay the dbbi construction on faed.
Hypothesis: faed = unknown a1z26 message at PRIME logical positions (zeros dropped: j=10->'a', t=20->'b'),
single filler letters at non-prime positions (as dbbi carries B=2 / Y=25 tokens at primes).
Search: exact Viterbi over (string index, last 3 output letters) per prime step, capped at beam 20k,
scored with the clean Carroll quadgram model (quad_indep.py). Score = per-letter quadgram log10 prob.
Planted self-test (3 streams) + matched letter-shuffle controls. No AES unless a readable phrase appears.
"""
import sys, random, json, time, difflib
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
from common import FAED, primes_upto
from quad_indep import LOGP, FLOOR

PR = set(primes_upto(5000))
AL = 'abcdefghijklmnopqrstuvwxyz'
BEAM = 20000
OUT = '/home/vin/bitcoin_puzzle/scratch/c42/test0'


def options(s, j):
    c = s[j]
    if c == 'a':
        o = [('a', 1), ('j', 1)]                      # 1 or 10 (zero dropped)
        if j + 1 < len(s):
            o.append((AL[10 + ord(s[j + 1]) - 97], 2))  # 11..19 = k..s
        return o
    if c == 'b':
        o = [('b', 1), ('t', 1)]                      # 2 or 20 (zero dropped)
        if j + 1 < len(s) and s[j + 1] in 'abcdef':
            o.append((AL[20 + ord(s[j + 1]) - 97], 2))  # 21..26 = u..z
        return o
    return [(c, 1)]                                   # c..i = 3..9


def search(s, start, beam=BEAM):
    n = len(s)
    states = {(0, ''): (0.0, '', ())}   # (i,last3) -> (total, out, trace of (i_token, len))
    p = start
    fin = []
    maxstates = 0
    while states:
        q = p
        while q not in PR:
            q += 1
        gap = q - p
        new = {}
        for (i, l3), (sc, out, tr) in states.items():
            j = i + gap
            if j >= n:
                fin.append((sc, out, tr)); continue
            for ch, ln in options(s, j):
                if j + ln > n:
                    continue
                add = LOGP.get(out[-3:] + ch, FLOOR) if len(out) >= 3 else 0.0
                key = (j + ln, (l3 + ch)[-3:])
                v = sc + add
                if key not in new or new[key][0] < v:
                    new[key] = (v, out + ch, tr + ((j, ln),))
        if len(new) > beam:
            new = dict(sorted(new.items(), key=lambda kv: -kv[1][0])[:beam])
        maxstates = max(maxstates, len(new))
        states = new
        p = q + 1
    best = max(fin, key=lambda t: t[0] / max(1, len(t[1]) - 3))
    sc, out, tr = best
    return dict(per=sc / max(1, len(out) - 3), out=out, n=len(out), trace=tr, maxstates=maxstates)


def tok(ch):
    return ''.join(AL[int(d) - 1] for d in str(ord(ch) - 96) if d != '0')


UNI = Counter(FAED)
UL, UW = zip(*sorted(UNI.items()))


def make_plant(sentence, start, rng, length=570):
    s = ''; planted = ''; p = start; k = 0
    while len(s) < length:
        if p in PR:
            t = tok(sentence[k % len(sentence)])
            if len(s) + len(t) <= length and k < len(sentence):
                planted += sentence[k]
            s += t; k += 1
        else:
            s += rng.choices(UL, UW)[0]
        p += 1
    return s[:length], planted


# dictionary for "readable English" criterion
SHORT = set('a i an as at be by do go he if in is it me my no of on or so to up us we'.split())
WORDS = set()
for w in open('/usr/share/dict/american-english', encoding='utf-8', errors='ignore'):
    w = w.strip()
    if w.isalpha() and w.islower() and w.isascii() and len(w) >= 3:
        WORDS.add(w)
WORDS |= SHORT
MAXW = 20


def longest_dict_span(t):
    n = len(t); best = (0, 0, 0)
    for a in range(n):
        reach = [False] * (n + 1); reach[a] = True; far = a
        for i in range(a, n):
            if not reach[i]:
                continue
            for L in range(1, MAXW + 1):
                if i + L > n: break
                if t[i:i + L] in WORDS:
                    reach[i + L] = True; far = max(far, i + L)
        if far - a > best[0]:
            best = (far - a, a, far)
    return best


def recovery(dec, planted):
    m = difflib.SequenceMatcher(None, dec, planted, autojunk=False)
    return sum(b.size for b in m.get_matching_blocks()) / len(planted)


def job(args):
    tag, s, start = args
    t0 = time.time()
    r = search(s, start)
    r['tag'] = tag; r['start'] = start; r['secs'] = time.time() - t0
    r['span'] = longest_dict_span(r['out'])
    del r['trace']
    return r


SENTS = [
    'whenthenightfallsoverthequietcitytheoldwatchmanlightshislampandwalksslowlyalongtheemptystreetsuntildawn',
    'youwillfindthesecretkeyhiddenbehindtheseconddoorbutonlyafteryouhavelearnedtoreadthenumbersinthegridagain',
    'everygreatjourneybeginswithasinglestepandthecouragetokeepmovingforwardevenwhentheroadseemsendlesstoyou',
]

if __name__ == '__main__':
    rng = random.Random(42042)
    NCTRL = 30
    inputs = {'fwd': FAED, 'rev': FAED[::-1], 'nohdr': FAED[4:]}
    starts = [1, 188, 189]
    # ---- planted self-test (one plant per counter convention) ----
    plants = []
    for k, (sent, st) in enumerate(zip(SENTS, starts)):
        s, planted = make_plant(sent, st, rng)
        plants.append((f'plant{k}', s, st, planted))
    tasks = []
    for tag, s, st, planted in plants:
        tasks.append((tag, s, st))
        for c in range(NCTRL):
            l = list(s); rng.shuffle(l); tasks.append((f'{tag}_ctrl{c}', ''.join(l), st))
    for nm, s in inputs.items():
        for st in starts:
            tasks.append((f'real_{nm}_s{st}', s, st))
            for c in range(NCTRL):
                l = list(s); rng.shuffle(l); tasks.append((f'real_{nm}_s{st}_ctrl{c}', ''.join(l), st))
    print('tasks', len(tasks), flush=True)
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(job, tasks, chunksize=4)
    print('elapsed %.1fs' % (time.time() - t0), 'max beam states', max(r['maxstates'] for r in res))
    R = {r['tag']: r for r in res}
    json.dump(R, open(f'{OUT}/results.json', 'w'), indent=0)

    # ---- plant evaluation & margin calibration ----
    gaps = []
    print('\n== PLANTS ==')
    for tag, s, st, planted in plants:
        r = R[tag]
        cmax = max(R[f'{tag}_ctrl{c}']['per'] for c in range(NCTRL))
        rec = recovery(r['out'], planted)
        gaps.append(r['per'] - cmax)
        print(f'{tag} start={st} planted={len(planted)} dec_len={r["n"]} per={r["per"]:.3f} ctrl_max={cmax:.3f} '
              f'gap={r["per"]-cmax:.3f} recovery={rec:.3f} span={r["span"][0]}')
        print('   dec :', r['out'])
        print('   true:', planted)
    margin = 0.5 * min(gaps)
    plant_ok = all(g > 0 for g in gaps)
    print(f'plant gaps {[round(g,3) for g in gaps]}  -> decision margin (half the smallest plant gap) = {margin:.3f}')

    # ---- real runs ----
    print('\n== REAL ==')
    allctrl_span = 0
    verdicts = []
    for nm in inputs:
        for st in starts:
            tag = f'real_{nm}_s{st}'
            r = R[tag]
            cs = [R[f'{tag}_ctrl{c}'] for c in range(NCTRL)]
            cmax = max(c['per'] for c in cs); cmean = sum(c['per'] for c in cs) / NCTRL
            sd = (sum((c['per'] - cmean) ** 2 for c in cs) / NCTRL) ** .5
            cspan = max(c['span'][0] for c in cs); allctrl_span = max(allctrl_span, cspan)
            ok = (r['per'] - cmax >= margin) and r['span'][0] >= 40
            verdicts.append(ok)
            print(f'{tag}: n={r["n"]} per={r["per"]:.3f} ctrl mean={cmean:.3f} sd={sd:.3f} max={cmax:.3f} '
                  f'diff={r["per"]-cmax:+.3f} z={(r["per"]-cmean)/sd:+.2f} span={r["span"][0]} (ctrl max span {cspan}) PASS={ok}')
            print('   ', r['out'])
            sp = r['span']
            if sp[0] >= 12:
                print('    longest dict span:', r['out'][sp[1]:sp[2]])
    print('\nmax dictionary span among all real controls:', allctrl_span)
    print('plant self-test ok:', plant_ok, '| any real PASS:', any(verdicts))
