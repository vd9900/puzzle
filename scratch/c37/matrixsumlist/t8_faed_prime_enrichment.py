"""T8: does the dbbi prime-marker scheme continue through the 104-bit 'matrixsumlist' label into faed?
For every counting offset o in 0..400 (o=195 continues dbbi91+label104 physical count; o=187 continues the
83-token logical count), compare the letter distribution of faed at positions i where (i+1+o) is prime against the
rest (chi-square, 9 letters) and the share of the most enriched letter.  Max over offsets vs 300 shuffled-faed
controls (same max-over-offset statistic)."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
P = set(primes_upto(2000)); L = 'abcdefghi'
def chi(s, o):
    idx = [i for i in range(len(s)) if (i + 1 + o) in P]
    a = [s[i] for i in idx]; b = [s[i] for i in range(len(s)) if (i + 1 + o) not in P]
    st = 0.0
    for x in L:
        ca, cb = a.count(x), b.count(x); t = ca + cb
        if t == 0: continue
        ea = t * len(a) / len(s); eb = t * len(b) / len(s)
        st += (ca - ea) ** 2 / ea + (cb - eb) ** 2 / eb
    top = max(L, key=lambda x: a.count(x) / len(a) - b.count(x) / len(b))
    return st, top, a.count(top) / len(a), b.count(top) / len(b), len(a)
def scan(s, offs=range(0, 401)):
    return max((chi(s, o)[0], o) for o in offs)
if __name__ == '__main__':
    r = scan(FAED)
    print('REAL max chi2 %.2f at offset %d' % r, chi(FAED, r[1]))
    for o in (0, 187, 195, 196, 91, 104):
        print('  offset', o, 'chi2=%.2f top=%s prime-share=%.3f rest-share=%.3f nprime=%d' % chi(FAED, o))
    ctrl = sorted(scan(shuffled(FAED, 31337 + t))[0] for t in range(300))
    print('CONTROL max-over-offset chi2: median %.2f p95 %.2f max %.2f; real rank p=%.3f' % (
        ctrl[150], ctrl[285], ctrl[-1], sum(c >= r[0] for c in ctrl) / 300))
