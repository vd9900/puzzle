"""T4b: re-run of T4(b) with a NON-degenerate detector.  T4(b)'s 'bytes+32' codec maps 0..99 to 32..131, which is
printable almost surely (control run = 285 = real), so it carried no information.  Here: exclude bytes+32 from the
printable statistics; add lowercase ratio of z100/bytes, and English quadgram score (textmodel) of the letters in
bytes+32.  Control: 200 shuffled-faed strings pushed through the same Bifid decrypt."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
import bifid
from t4_bifid_sumlist import decodes_b, SQ

def stats(res):
    inf = [(p, b) for p, b in res if p[3] != 'bytes+32' and len(b) > 20]
    run = max(longest_printable_run(b) for p, b in inf)
    bpr = max(pr(b) for p, b in inf)
    blo = max(lowr(b) for p, b in inf)
    be = max(eng(b) for p, b in res if p[3] == 'bytes+32')
    return run, bpr, blo, be

R = decodes_b(bifid.BIF)
real = stats(R)
print('REAL (run, best printable, best lowercase, best eng(bytes+32)):', [round(x, 3) for x in real])
cs = []
for t in range(200):
    d = bifid.bifid_decrypt(shuffled(FAED, 500 + t), SQ, 570)
    rr = decodes_b(d)
    if rr: cs.append(stats(rr))
for i, nm in enumerate(('run', 'printable', 'lowercase', 'eng')):
    c = sorted(x[i] for x in cs)
    ge = sum(1 for x in c if x >= real[i])
    print(f'{nm:10s} real={real[i]:.3f} ctrl median={c[len(c)//2]:.3f} max={c[-1]:.3f}  frac ctrl>=real={ge/len(c):.3f} (n={len(c)})')
