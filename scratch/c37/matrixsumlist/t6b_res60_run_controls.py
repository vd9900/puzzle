"""T6b: T6 gave res60/res61 longest exact run 8 (width 276 column sums mod 10) vs control max 7 with only 12 controls.
Extend the control for the res60 longest-run statistic only: 60 further multiset shuffles of faed (seeds disjoint)."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
from t6_faed_sums_vs_dbbi import scan
real = scan(FAED, {'res60': RES60})['res60_run']
print('REAL res60_run', real[1], real[2], flush=True)
c = []
for t in range(60):
    c.append(scan(shuffled(FAED, 9100 + t), {'res60': RES60})['res60_run'][1])
    if t % 10 == 9: print(t + 1, sorted(c), flush=True)
c.sort(); ge = sum(x >= real[1] for x in c)
print(f'res60_run real={real[1]} ctrl median={c[len(c)//2]} max={c[-1]} frac>=real={ge}/{len(c)} -> p~{(ge+1)/(len(c)+1):.3f}')
