# Exhaustive: every injective assignment of the 9 symbols a..i to digits 0..9 (3,628,800), decode with the KNOWN board
# (fubcdora / lethingky / mvpszjqwx., escapes 1 and 4), quadgram-score vectorised with numpy. Controls = shuffled sources.
import sys, json, itertools, random, time
import numpy as np
from cb3lib import *
QT = np.full(28 ** 4, FLOOR, dtype=np.float32)
for k, v in LOGP.items():
    QT[((ord(k[0]) - 97) * 28 + ord(k[1]) - 97) * 28 * 28 + (ord(k[2]) - 97) * 28 + ord(k[3]) - 97] = v
AL = 'abcdefghijklmnopqrstuvwxyz/.'
BOARD = make_board()
TOPI = {d: AL.index(BOARD[d]) for d in '02356789'}
ROWI = {e: [AL.index(BOARD[e + str(j)]) for j in range(10)] for e in '14'}
QM = 27  # '?' scored like '.'
def run(name, sym, zero_fixed=False, topk=8):
    """sym: string over a..i plus optional 'Z' (fixed digit 0)."""
    syms = sorted(set(sym) - {'Z'}); n = len(sym)
    digits_free = [d for d in '0123456789' if not (zero_fixed and d == '0')]
    best = []  # (score, esc_desc, mapping)
    t0 = time.time(); total = 0
    esc_choices = []
    for L1 in syms + [None]:
        for L4 in syms + [None]:
            if L1 is not None and L1 == L4: continue
            if zero_fixed and (L1 is None or L4 is None): continue
            if L1 is None and L4 is None: continue
            esc_choices.append((L1, L4))
    for L1, L4 in esc_choices:
        esc = {s for s in (L1, L4) if s}
        # tokenize
        types = {}; seq = []
        i = 0
        while i < n:
            c = sym[i]; i += 1
            if c in esc:
                if i < n: tok = (c, sym[i]); i += 1
                else: tok = (c, None)
            else: tok = (c,)
            seq.append(types.setdefault(tok, len(types)))
        seq = np.array(seq, dtype=np.int64); T = len(types)
        R = [s for s in syms if s not in esc]
        D = [d for d in digits_free if d not in ('1', '4')]
        fixed = {}
        if L1: fixed[L1] = '1'
        if L4: fixed[L4] = '4'
        if zero_fixed: fixed['Z'] = '0'
        perms = np.array(list(itertools.permutations(range(len(D)), len(R))), dtype=np.int8)  # B x |R| -> index into D
        Dd = np.array([int(d) for d in D], dtype=np.int8)
        B = len(perms); total += B
        # letter-index matrix LT: B x T
        LT = np.empty((B, T), dtype=np.int8)
        topi_arr = np.array([TOPI.get(str(d), QM) for d in range(10)], dtype=np.int8)
        for tok, ti in types.items():
            if len(tok) == 1:
                s = tok[0]
                if s in fixed: LT[:, ti] = topi_arr[int(fixed[s])]
                else: LT[:, ti] = topi_arr[Dd[perms[:, R.index(s)]]]
            else:
                e, s2 = tok; row = np.array(ROWI[fixed[e]], dtype=np.int8)
                if s2 is None: LT[:, ti] = QM
                elif s2 in fixed: LT[:, ti] = row[int(fixed[s2])]
                else: LT[:, ti] = row[Dd[perms[:, R.index(s2)]]]
        for b0 in range(0, B, 4032):
            sub = LT[b0:b0 + 4032].astype(np.int32)
            txt = sub[:, seq]  # b x n
            idx = ((txt[:, :-3] * 28 + txt[:, 1:-2]) * 28 + txt[:, 2:-1]) * 28 + txt[:, 3:]
            sc = QT[idx].sum(axis=1) / (n - 3)
            top = np.argsort(-sc)[:topk]
            for j in top:
                best.append((float(sc[j]), f'1={L1} 4={L4}', {s: fixed.get(s) or D[perms[b0 + j, R.index(s)]] for s in syms}))
            best.sort(key=lambda x: -x[0]); best = best[:topk]
    out = []
    for sc, e, m in best:
        mp = str.maketrans(''.join(m), ''.join(m.values()))
        d = sym.replace('Z', '0').translate(mp)
        t = decode(d, BOARD, ('1', '4'))
        out.append({'src': name, 'q': round(sc, 3), 'qexact': round(qscore(t), 3), 'esc': e, 'map': ''.join(m[s] for s in syms), 'frags': frags(t), 'text': t})
    print(json.dumps({'src': name, 'perms': total, 'secs': round(time.time() - t0, 1), 'best_q': out[0]['q'], 'best_text': out[0]['text'][:80], 'frags': out[0]['frags']}), flush=True)
    return out
if __name__ == '__main__':
    from exp05_prime_seg import segmentations
    rng = random.Random(7)
    def shuf(s): l = list(s); rng.shuffle(l); return ''.join(l)
    srcs = [('faed', FAED), ('faed_rev', FAED[::-1]), ('dbbi', DBBI), ('dbbi_rev', DBBI[::-1]), ('res61', RES61), ('res61_rev', RES61[::-1]), ('res60', RES60),
            ('faed_zeroP', prime_mode(FAED, 'zero', 'Z')), ('dbbi_zeroP', prime_mode(DBBI, 'zero', 'Z')), ('faed_dropP', prime_mode(FAED, 'drop')), ('dbbi_dropP', prime_mode(DBBI, 'drop'))]
    for t in segmentations(DBBI):
        srcs.append((f'dbbi_zerolog{len(t)}', ''.join('Z' if (i + 1) in P else tok for i, tok in enumerate(t))))
    srcs += [('CTRL_faed_shuf1', shuf(FAED)), ('CTRL_faed_shuf2', shuf(FAED)), ('CTRL_dbbi_shuf1', shuf(DBBI)), ('CTRL_dbbi_shuf2', shuf(DBBI)), ('CTRL_res61_shuf', shuf(RES61)),
             ('CTRL_vic_as_letters', VIC.translate(str.maketrans('0123456789', 'abcdefghij')).replace('j', 'Z'))]  # positive control: vic digit 9 -> Z? no: use j as 10th sym
    allrows = []
    with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto_perm.txt', 'w') as f:
        for name, s in srcs:
            if name == 'CTRL_vic_as_letters':
                # positive control: VIC stream relabelled to letters a..j (10 symbols) -> drop 'Z' trick; use digit 9->'i' collision-free? use symbols a..i for 0..8 and treat 9 as fixed by zeroing: skip exactness, use zero_fixed trick on digit 9 instead
                s = VIC.translate(str.maketrans('0123456789', 'bcdeafghiZ'))  # 9->Z fixed; wrong fixed digit (0) on purpose -> partial control
            rows = run(name, s, zero_fixed=('Z' in s))
            allrows += rows
            for r in rows:
                if not name.startswith('CTRL'): f.write(r['text'] + '\n'); f.write(letters(r['text']) + '\n')
    json.dump(allrows, open('/home/vin/bitcoin_puzzle/scratch/wf/lens_cb3_perm_rows.json', 'w'), indent=0)
