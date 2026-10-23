"""Shuffled-residual control for H1b: same marker skeleton (L83), residual letters shuffled; compare search depth."""
import sys, random, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from h1b_markers import tokens, build, opts_for, Search, CHARSETS
toks = tokens('L83'); res = [t for t, m, _ in toks if not m]
real = {}; ctrl = {}
rnd = random.Random(12)
cfgs = [(c, r, v) for c in ('one', 'tok', 'col') for r in ('id', 'a0', 'ed', 'gd', 'fd') for v in (False, True)]
def run(tk):
    out = {}
    for c, r, v in cfgs:
        slots, classes = build(tk, c, r, v, opts_for('L83', c))
        se = Search(slots, classes, CHARSETS['printnl'], max_nodes=30_000_000, max_solutions=5, min_bytes=8).run()
        out[(c, r, v)] = (se.deepest, len(se.solutions))
    return out
real = run(toks)
ctrls = []
for k in range(6):
    sh = res[:]; rnd.shuffle(sh); it = iter(sh)
    tk = [(t, m, i) if m else (next(it), m, i) for t, m, i in toks]
    ctrls.append(run(tk))
rd = [d for d, s in real.values()]; cd = [max(c[k][0] for c in ctrls) for k in cfgs]
print('real: mean deepest', sum(rd) / len(rd), 'max', max(rd), 'sols', sum(s for d, s in real.values()))
print('ctrl: mean of per-config max deepest over 6 shuffles', sum(cd) / len(cd), 'max', max(cd),
      'sols', sum(c[k][1] for c in ctrls for k in cfgs))
print('configs where real deepest > max of controls:', sum(1 for k in cfgs if real[k][0] > max(c[k][0] for c in ctrls)), 'of', len(cfgs))
