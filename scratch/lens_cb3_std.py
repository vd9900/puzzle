# Round-3 verification: known board (fubcdora / lethingky / mvpszjqwx., esc 1,4) on dbbi / res60 / res61 / faed
# under a0/a1, prime none/zero/drop (+ logical zeroing for dbbi), revdig/revtxt, plus escape rows re-keyed from dbbi/faed order.
import json, sys
from cb3lib import *
from exp05_prime_seg import segmentations
OUT = '/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto.txt'
ROWS = '/home/vin/bitcoin_puzzle/scratch/wf/lens_cb3_std_rows.json'
def inv(perm):
    out = [''] * 10
    for j, d in enumerate(perm): out[int(d)] = str(j)
    return ''.join(out)
def boards_for(mapping):
    tr = A0 if mapping == 'a0' else A1
    res = {'STD': (make_board(), ('1', '4'))}
    for nm, order in (('dbbi', DBBI_ORDER), ('faed', FAED_ORDER)):
        od = order.translate(tr); perm = od + ''.join(d for d in '0123456789' if d not in od)
        res[f'RKall_{nm}'] = (make_board(colperm=perm), ('1', '4'))
        res[f'RKall_{nm}_inv'] = (make_board(colperm=inv(perm)), ('1', '4'))
        # escape rows only re-keyed
        b = make_board(); be = make_board(colperm=perm); bi = make_board(colperm=inv(perm))
        res[f'RKesc_{nm}'] = ({**b, **{k: v for k, v in be.items() if len(k) == 2}}, ('1', '4'))
        res[f'RKesc_{nm}_inv'] = ({**b, **{k: v for k, v in bi.items() if len(k) == 2}}, ('1', '4'))
        e = (od[0], od[1]); res[f'ESCorder_{nm}'] = (make_board(esc=e), e)
    be = ('b'.translate(tr), 'e'.translate(tr)); res['ESC_be'] = (make_board(esc=be), be)
    return res
sources = {'dbbi': DBBI, 'res60': RES60, 'res61': RES61, 'faed': FAED}
segs = segmentations(DBBI)
rows = []; cands = []
for mapping in ('a0', 'a1'):
    tr = A0 if mapping == 'a0' else A1
    bds = boards_for(mapping)
    variants = []
    for sn, s in sources.items():
        for pm in ('none', 'zero', 'drop'):
            variants.append((f'{sn}|{pm}', prime_mode(s, pm, zero='Z').translate(tr).replace('Z', '0')))
    for t in segs:
        variants.append((f'dbbi|zerolog{len(t)}', ''.join('0' if (i + 1) in P else tok.translate(tr) for i, tok in enumerate(t))))
        variants.append((f'dbbi|zerolog{len(t)}_keeplen', ''.join('0' * len(tok) if (i + 1) in P else tok.translate(tr) for i, tok in enumerate(t))))
    for vn, dig in variants:
        for bn, (board, esc) in bds.items():
            for revdig in (0, 1):
                d = dig[::-1] if revdig else dig
                fn = lambda x: qscore(decode(x, board, esc))
                txt = decode(d, board, esc); z = zscore(d, fn)
                for revtxt in (0, 1):
                    t = txt[::-1] if revtxt else txt
                    fr = frags(t)
                    rows.append({'tag': f'{bn}|{vn}|{mapping}|revdig={revdig}|revtxt={revtxt}', 'q': round(qscore(t), 3), 'z': round(z, 2), 'len': len(t), 'qm': t.count('?'), 'frags': fr, 'text': t})
                    cands += [t, letters(t), d]
rows.sort(key=lambda r: -r['z'])
json.dump(rows, open(ROWS, 'w'), indent=0)
seen = set(); n = 0
with open(OUT, 'w') as f:
    for c in cands:
        if c and c not in seen: seen.add(c); f.write(c + '\n'); n += 1
print('rows', len(rows), 'unique candidates', n)
print('top by z:')
for r in rows[:15]: print(r['z'], r['q'], r['tag'], r['frags'], r['text'][:70])
print('rows with any fragment >=6 letters:')
for r in rows:
    if any(len(w) >= 6 for w in r['frags']): print(r['z'], r['tag'], r['frags'], r['text'][:70])
