"""Cycle 43 test2: is faed / dbbi / R60 the decimal expansion of a low-height algebraic number (degree <= 4,
|coeff| < 1e6) or a small integer combination (|coeff| < 100) of standard constants?

Derivation: the critic closed pure roots n^(1/r) and rationals p/q (q <= 1e18). The remaining low-complexity
"famous number" families are general algebraic numbers of low height and Z-linear combinations of constants;
PSLQ finds both from ~39 digits. Letters a..i = 1..9, g = 0 or 7 (both resolutions enumerated exactly).

Per target: first 39 letters, every exact 0/7 resolution of the g's, integer-part length L in {0,1,2},
basis (i) [1,x,x^2,x^3,x^4] maxcoeff 1e6, basis (ii) [x,1,pi,e,sqrt2,sqrt3,sqrt5,ln2,ln3,gamma,zeta3,pi^2] maxcoeff 100.
Oracle (self-verifying): any relation is solved/evaluated at len(target)+40 digits and EVERY letter of the full target
must match (non-g letter exact, g in {0,7}).

Run with the project venv (mpmath):  ../../../.venv/bin/python pslq_test.py {controls|negctl|targets}
"""
import sys, os, json, itertools, random, time
from collections import Counter
from multiprocessing import Pool
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
M = 39            # prefix letters fed to PSLQ
WORK_DPS = 50     # PSLQ working precision (input is exact 39-digit decimal)
TOL = {'poly': mp.mpf(10) ** -30, 'const': mp.mpf(10) ** -33}
MAXC = {'poly': 10 ** 6, 'const': 100}
MAXSTEPS = 4000
CONST_NAMES = ['1', 'pi', 'e', 'sqrt2', 'sqrt3', 'sqrt5', 'ln2', 'ln3', 'gamma', 'zeta3', 'pi^2']


def consts(dps):
    with mp.workdps(dps):
        return [mp.mpf(1), +mp.pi, +mp.e, mp.sqrt(2), mp.sqrt(3), mp.sqrt(5), mp.log(2), mp.log(3),
                +mp.euler, mp.zeta(3), mp.pi ** 2]


def enc(digs):
    return ''.join('g' if d in '07' else chr(96 + int(d)) for d in digs)


def first_mismatch(letters, digs):
    for i, (c, d) in enumerate(zip(letters, digs)):
        if c == 'g':
            if d not in '07':
                return i
        elif d != str(ord(c) - 96):
            return i
    return min(len(letters), len(digs))


def resolutions(prefix):
    gi = [i for i, c in enumerate(prefix) if c == 'g']
    base = [None if c == 'g' else str(ord(c) - 96) for c in prefix]
    for bits in itertools.product('07', repeat=len(gi)):
        d = base[:]
        for i, b in zip(gi, bits):
            d[i] = b
        yield ''.join(d)


def digits_of(val, L, N):
    """N-digit string of val with L integer digits (None if out of range / negative)."""
    if val < 0:
        return None
    D = int(mp.floor(val * mp.mpf(10) ** (N - L)))
    if D >= 10 ** N:
        return None
    return str(D).zfill(N)


def _trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def _divmod(a, b):
    from fractions import Fraction as F
    a = [F(v) for v in a]; q = [F(0)] * max(1, len(a) - len(b) + 1)
    while len(_trim(a)) >= len(b):
        a = _trim(a); s = len(a) - len(b); f = a[-1] / F(b[-1])
        q[s] = f
        for i, bv in enumerate(b):
            a[s + i] -= f * bv
    return q, _trim(a)


def squarefree(rel):
    """p / gcd(p, p') over Q (ascending coefficients) so Newton converges quadratically at every root."""
    p = _trim(rel)
    dp = [k * p[k] for k in range(1, len(p))]
    a, b = p, _trim(dp)
    while b:
        _, r = _divmod(a, b)
        a, b = b, r
    if len(a) <= 1:
        return p
    q, r = _divmod(p, a)
    assert not r
    from math import lcm
    m = lcm(*[v.denominator for v in q])
    return [int(v * m) for v in q]


def oracle(kind, rel, x0, L, full):
    """Extend relation to the full target length; return number of letters matched (== len(full) means pass)."""
    N = len(full)
    with mp.workdps(N + 40):
        if kind == 'poly':
            if all(v == 0 for v in rel[1:]):
                return 0, 'no-x'
            c = [mp.mpf(v) for v in squarefree(rel)]   # c[k] * x^k, repeated roots removed
            p = lambda t: sum(ck * t ** k for k, ck in enumerate(c))
            dp = lambda t: sum(k * ck * t ** (k - 1) for k, ck in enumerate(c) if k)
            r = mp.mpf(x0)
            for _ in range(30):
                d = dp(r)
                if d == 0:
                    break
                r = r - p(r) / d
            if abs(r - mp.mpf(x0)) > mp.mpf(10) ** -(M - L - 6):
                return 0, 'root-far'
            val = r
        else:
            if rel[0] == 0:
                return 0, 'no-x'
            cs = consts(N + 40)
            val = -sum(mp.mpf(v) * k for v, k in zip(rel[1:], cs)) / rel[0]
        digs = digits_of(val, L, N)
    if digs is None:
        return 0, 'range'
    k = first_mismatch(full, digs)
    return k, digs[:60]


def job(args):
    name, full, digs, L, kind = args
    mp.mp.dps = WORK_DPS
    x = mp.mpf(digs[:L] + '.' + digs[L:]) if L else mp.mpf('0.' + digs)
    if x == 0:
        return (name, digs, L, kind, None, 0, 'zero')
    if kind == 'poly':
        vec = [x ** k for k in range(5)]
    else:
        vec = [x] + consts(WORK_DPS)
    rel = mp.pslq(vec, tol=TOL[kind], maxcoeff=MAXC[kind], maxsteps=MAXSTEPS)
    if rel is None:
        return (name, digs, L, kind, None, 0, '')
    k, info = oracle(kind, rel, x, L, full)
    return (name, digs, L, kind, rel, k, info)


def make_jobs(name, full):
    out = []
    for digs in resolutions(full[:M]):
        for L in (0, 1, 2):
            for kind in ('poly', 'const'):
                out.append((name, full, digs, L, kind))
    return out


def control_strings(N=570):
    with mp.workdps(N + 60):
        plastic = mp.findroot(lambda t: t ** 3 - t - 1, 1.3)
        quartic = mp.findroot(lambda t: t ** 4 - 37 * t ** 3 + 101 * t - 999, 36.5)
        vals = {
            'C1_(3+2sqrt7)/5_L1': ((3 + 2 * mp.sqrt(7)) / 5, 1, 'poly'),
            'C2_plastic_L1': (plastic, 1, 'poly'),
            'C3_3pi-2e+sqrt5_L1': (3 * mp.pi - 2 * mp.e + mp.sqrt(5), 1, 'const'),
            'C4_quartic_x4-37x3+101x-999_L2': (quartic, 2, 'poly'),
            'C5_(zeta3-gamma)/7_L0': ((mp.zeta(3) - mp.euler) / 7, 0, 'const'),
        }
        out = {}
        for k, (v, L, kind) in vals.items():
            out[k] = (enc(digits_of(v, L, N)), L, kind)
    return out


def run(jobs, label):
    t = time.time()
    with Pool(os.cpu_count()) as pool:
        res = pool.map(job, jobs, chunksize=4)
    print(f'[{label}] {len(jobs)} PSLQ calls in {time.time() - t:.0f}s', flush=True)
    return res


if __name__ == '__main__':
    mode = sys.argv[1]
    log = open(HERE + f'results_{mode}.log', 'w')
    def P(*a):
        s = ' '.join(str(v) for v in a)
        print(s, flush=True); log.write(s + '\n'); log.flush()

    if mode == 'controls':
        for name, (full, Ltrue, kind_true) in control_strings().items():
            res = run(make_jobs(name, full), name)
            raw = [r for r in res if r[4] is not None]
            passes = [r for r in res if r[4] is not None and r[5] == len(full)]
            P(f'{name}: g-in-prefix={full[:M].count("g")} calls={len(res)} raw_relations={len(raw)} full_passes={len(passes)}')
            for r in passes[:4]:
                P('   PASS', 'L=', r[2], r[3], r[4], 'matched', r[5], '/', len(full))
            agg = Counter((r[2], r[3], tuple(r[4]), r[6] if r[6] in ('root-far', 'range', 'no-x') else 'mismatch@%d' % r[5])
                          for r in raw if r[5] != len(full))
            P(f'   discarded by oracle: {sum(agg.values())} raw relations ({len(agg)} distinct); most common:')
            for (L, kind, rel, why), n in agg.most_common(6):
                P('      x%d' % n, 'L=', L, kind, list(rel), why)
            ok = any(r[2] == Ltrue and r[3] == kind_true for r in passes)
            P('   CONTROL', 'RECOVERED' if ok else 'FAILED')
    elif mode == 'negctl':
        rng = random.Random(4343)
        while True:
            d = ''.join(rng.choice('0123456789') for _ in range(570))
            s = enc(d)
            if s[:M].count('g') == 8 and s[0] != 'g':
                break
        res = run(make_jobs('negctl', s), 'negctl')
        raw = [r for r in res if r[4] is not None]
        passes = [r for r in raw if r[5] == len(s)]
        P(f'negctl (random 570 digits, 8 g in prefix): calls={len(res)} raw_relations={len(raw)} full_passes={len(passes)}')
        for r in raw:
            P('   raw', 'L=', r[2], r[3], r[4], 'matched', r[5], '/', len(s), r[6] if r[6] in ('root-far', 'range', 'no-x') else '')
    elif mode == 'targets':
        T = json.load(open(HERE + 'targets.json'))
        names = sys.argv[2:] or ['faed', 'faed_rev', 'dbbi', 'R60']
        total = 0
        for name in names:
            full = T[name]
            jobs = make_jobs(name, full)
            total += len(jobs)
            res = run(jobs, name)
            raw = [r for r in res if r[4] is not None]
            passes = [r for r in raw if r[5] == len(full)]
            P(f'{name}: len={len(full)} g-in-prefix={full[:M].count("g")} calls={len(res)} raw_relations={len(raw)} full_passes={len(passes)}')
            for r in raw:
                P('   raw', 'L=', r[2], r[3], r[4], 'matched', r[5], '/', len(full), r[6] if r[6] in ('root-far', 'range', 'no-x') else '', 'digits', r[1])
            for r in passes:
                P('   *** FULL PASS ***', r)
        P('total target PSLQ calls', total)
