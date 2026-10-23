"""T2: lay a page digit string (faed / dbbi / residual60 / Bifid-btcseed body as digits) row-major in a matrix of
width w; take the row-sum list or column-sum list; read the LIST with three numeric codecs that were NOT in the
exhausted 'mod 26/27/9 -> letters' families:
  (a) direct byte values chr(sum)            [w=19 gives faed row sums mean 102.6 = inside lowercase ASCII]
  (b) the page z-method on the decimal concatenation of the sums (decimal -> int -> bytes), also zero-padded
      to fixed width 2/3, and reversed list
  (c) z-method on the sums mod 10 (one digit per sum)
Detector: printable ratio / lowercase ratio / longest printable run.  Control: 200 multiset shuffles of each
source; report real max vs control max distribution.  Planted test: build a faed-like string whose width-19 row
sums are the ASCII codes of a phrase and check (a) recovers it."""
import random, sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *

def codecs(sums):
    out = []
    if all(0 <= s < 256 for s in sums):
        out.append(('chr', bytes(sums)))
    cat = ''.join(map(str, sums))
    out.append(('zcat', zdec([int(c) for c in cat])))
    out.append(('zcat_rev', zdec([int(c) for c in ''.join(map(str, sums[::-1]))])))
    for k in (2, 3):
        if all(s < 10 ** k for s in sums):
            out.append((f'zpad{k}', zdec([int(c) for s in sums for c in f'{s:0{k}d}'])))
    out.append(('zmod10', zdec([s % 10 for s in sums])))
    return out

def all_decodes(s, a0, minlen=6):
    v = dig(s, a0)
    res = []
    for w in range(2, len(v)):
        for axis in ('rows', 'cols'):
            sums = grid_sums(v, w, axis)
            if len(sums) < 4:
                continue
            for cname, b in codecs(sums):
                if len(b) >= minlen:
                    res.append(((w, axis, cname), b))
    return res

def score_set(res):
    """max over decodes of: full-printable-with-len, printable ratio (len>=10), longest run"""
    best_run = 0; best_pr = 0; full_lower = []
    for p, b in res:
        r = longest_printable_run(b)
        best_run = max(best_run, r)
        if len(b) >= 10:
            best_pr = max(best_pr, pr(b))
        if len(b) >= 8 and lowr(b) >= 0.9:
            full_lower.append((p, b))
    return best_run, best_pr, full_lower

if __name__ == '__main__':
    # planted self-test: digits whose width-19 row sums equal the ASCII of a 30-char phrase
    rnd = random.Random(1)
    phrase = 'thisisaplantedthirtycharphrase'
    planted = []
    for ch in phrase:
        target = ord(ch)
        while True:
            row = [rnd.randint(1, 9) for _ in range(19)]
            diff = target - sum(row)
            # adjust greedily
            i = 0
            while diff != 0 and i < 1000:
                j = rnd.randrange(19)
                if diff > 0 and row[j] < 9: row[j] += 1; diff -= 1
                elif diff < 0 and row[j] > 1: row[j] -= 1; diff += 1
                i += 1
            if diff == 0: break
        planted += row
    ps = ''.join(chr(96 + d) for d in planted)
    hits = [p for p, b in all_decodes(ps, False) if b == phrase.encode()]
    assert ((19, 'rows', 'chr') in hits), hits
    print('planted self-test OK:', hits)

    import bifid
    sources = [('faed', FAED), ('dbbi', DBBI), ('res60', RES60), ('faed_rev', FAED[::-1]), ('dbbi_rev', DBBI[::-1])]
    summary = {}
    for name, s in sources:
        for a0 in (False, True):
            res = all_decodes(s, a0)
            run, bpr, fl = score_set(res)
            # control
            cr = []; cp = []; cf = 0
            for t in range(200 if len(s) < 200 else 60):
                r2, p2, f2 = score_set(all_decodes(shuffled(s, 1000 + t), a0))
                cr.append(r2); cp.append(p2); cf += len(f2)
            cr.sort(); cp.sort()
            n = len(res)
            print(f'{name:9s} a0={a0!s:5s} decodes={n:6d} REAL longest_run={run:3d} best_pr={bpr:.3f} lower>=0.9:{len(fl)} | '
                  f'CTRL run med={cr[len(cr)//2]} max={cr[-1]} pr med={cp[len(cp)//2]:.3f} max={cp[-1]:.3f} lower-hits total={cf}')
            for p, b in fl[:5]:
                print('    LOWER', p, b)
            summary[(name, a0)] = (n, run, bpr, len(fl))
    # direct ASCII special case print for faed w=18..22 rows
    for w in range(17, 24):
        sums = grid_sums(dig(FAED), w, 'rows')
        print('faed rows w=%d chr:' % w, bytes(min(255, x) for x in sums))
