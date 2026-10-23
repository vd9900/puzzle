# Deterministic decode implied by the best non-stationary model (untransposed Phase-3.2 board, escapes 1,4):
# fitted map letters->digits from models.py (P32_numblock*: 0..9 -> i g h f e d c a i b); i is ambiguous 0/8.
import sys; sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED
top = dict(zip('02356789', 'FUBCDORA')); r1 = '/LETHINGKY'; r4 = 'MVPSZJQWX.'
def dec(ds):
    out = []; i = 0
    while i < len(ds):
        d = ds[i]
        if d in '14' and i + 1 < len(ds): out.append((r1 if d == '1' else r4)[int(ds[i + 1])]); i += 2
        elif d in top: out.append(top[d]); i += 1
        else: i += 1
    return ''.join(out)
for iv in '08':
    m = dict(g='1', h='2', f='3', e='4', d='5', c='6', a='7', b='9', i=iv)
    ds = ''.join(m[c] for c in FAED); print('i=%s' % iv, dec(ds)[:90], '| tail:', dec(ds[538:]))
