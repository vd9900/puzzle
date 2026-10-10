# Round 2: phrase-keyed + structurally varied boards on the short streams; checkerboard on other page digit sources; direct Beaufort/Vigenere on a..i letters.
import json, random, sys
from cb3lib import *
from common import Z1, Z2, Z3, MATRIX, letters_to_digits
ALPHA = 'abcdefghijklmnopqrstuvwxyz'
PHRASES = ['lastwordsbeforearchichoice', 'thispassword', 'matrixsumlist', 'theseedisplanted', 'whiterabbit', 'whiterabbitseverywhere', 'cosmicduality', 'causality', 'salphaseion',
           'halfandbetterhalf', 'thematrixhasyou', 'followthewhiterabbit', 'jacquefresco', 'heisenberg', 'gsmgio', 'lifeanddeath', 'theoryofeverything', 'archichoice', 'lastwords',
           'enter', 'anstoo', 'shabef', 'ourfirsthintisyourlastcommand', 'fubcdora', 'oracle', 'architect', 'merovingian', 'keymaker', 'neo', 'trinity', 'morpheus', 'zion', 'thesource',
           'rosesarewhite', 'primenumbers', 'btcseed', 'bitcoin', 'satoshi', 'giveit', 'megangima', 'meganigma', 'puzzle', 'choiceisanillusion', 'dbifhcega', 'faedgcbhi']
def key26(p): return ''.join(dict.fromkeys(p.replace('j', 'i') if False else p)) + ''.join(c for c in ALPHA if c not in p)
def phrase_boards(p):
    k = key26(p); out = {}
    out[f'P_{p}_fill_last'] = make_board(top=k[:8], rows=(k[8:18], k[18:26] + '/.'))
    out[f'P_{p}_fill_first'] = make_board(top=k[:8], rows=('/' + k[8:17], '.' + k[17:26]))
    out[f'P_{p}_slash_first'] = make_board(top=k[:8], rows=('/' + k[8:17], k[17:26] + '.'))
    out[f'P_{p}_top_fill'] = make_board(top=k[:8], rows=(k[8:18], k[18:26] + '/.'))
    out[f'P_{p}_esc_from_key'] = make_board(esc=('1', '4'), top=k[:8], rows=(k[8:18], k[18:26] + '/.'))
    return out
def struct_boards():
    out = {'rowswap': make_board(rows=(ROW2, ROW1)), 'top_rev': make_board(top=TOP[::-1]), 'row1_rev': make_board(rows=(ROW1[::-1], ROW2)), 'row2_rev': make_board(rows=(ROW1, ROW2[::-1])),
           'all_rev': make_board(top=TOP[::-1], rows=(ROW1[::-1], ROW2[::-1])), 'cols_rev': make_board(colperm='9876543210'), 'esc_41_rowswap': make_board(esc=('4', '1')),
           'esc01': make_board(esc=('0', '1')), 'esc89': make_board(esc=('8', '9')), 'esc25': make_board(esc=('2', '5')), 'esc_09': make_board(esc=('0', '9'))}
    # continuous alphabet 'fubcdoralethingkymvpszjqwx./' re-cut with different top-row widths (7/9) -> width-10 board with different splits
    seq = 'fubcdoralethingkymvpszjqwx./'
    out['seq_split_7'] = make_board(esc=('1', '4', '7'), top=seq[:7], rows=(seq[7:17], seq[17:27], seq[27:] + '?????????'))
    return out
rng = random.Random(5)
def beaufort(c, k): return ''.join(chr(97 + (ord(k[i % len(k)]) - 65 - (ord(ch) - 97)) % 26) for i, ch in enumerate(c))
def vig_dec(c, k): return ''.join(chr(97 + (ord(ch) - 97 - (ord(k[i % len(k)]) - 65)) % 26) for i, ch in enumerate(c))
def vig_enc(c, k): return ''.join(chr(97 + (ord(ch) - 97 + (ord(k[i % len(k)]) - 65)) % 26) for i, ch in enumerate(c))
def randkey(L): return ''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(L))
rows = []; cands = set()
def rec(tag, d, board, esc, z=None):
    txt = decode(d, board, esc)
    if z is None: z = zscore(d, lambda x: qscore(decode(x, board, esc)), trials=20)
    rows.append({'tag': tag, 'q': round(qscore(txt), 3), 'z': round(z, 2), 'len': len(txt), 'frags': frags(txt), 'text': txt}); cands.add(txt); cands.add(letters(txt)); cands.add(d)
# (a) structural + phrase boards on short streams (+faed for structural only)
boards = struct_boards()
for p in PHRASES: boards.update(phrase_boards(p))
srcs = {'dbbi': DBBI, 'res60': RES60, 'res61': RES61, 'faed': FAED}
for bn, board in boards.items():
    esc = tuple(sorted({k[0] for k in board if len(k) == 2}))
    for sn, s in srcs.items():
        if sn == 'faed' and bn.startswith('P_') and not bn.endswith('fill_last'): continue
        for mn, tr in (('a0', A0), ('a1', A1)):
            for pm in ('none', 'drop', 'zero'):
                if sn.startswith('res') and pm != 'none': continue
                d0 = prime_mode(s, pm, 'Z').translate(tr).replace('Z', '0')
                for rd in (0, 1):
                    d = d0[::-1] if rd else d0
                    rec(f'{bn}|{sn}|{mn}|{pm}|revdig={rd}', d, board, esc)
print('after boards: rows', len(rows), flush=True)
# (b) other digit sources with STD board
rs = [sum(r) for r in MATRIX]; cs = [sum(c) for c in zip(*MATRIX)]
diag = [sum(MATRIX[i][i] for i in range(14)), sum(MATRIX[i][13 - i] for i in range(14))]
other = {'Z1_o0': letters_to_digits(Z1), 'Z2_o0': letters_to_digits(Z2), 'Z1_a0': Z1.translate(A0).replace('o', '9'), 'Z2_a0': Z2.translate(A0).replace('o', '9'),
         'Z3_a1': Z3.translate(str.maketrans('abcdefghi', '123456789')), 'rowsums': ''.join(map(str, rs)), 'colsums': ''.join(map(str, cs)), 'rows+cols': ''.join(map(str, rs + cs)),
         'cols+rows': ''.join(map(str, cs + rs)), 'rowsums_pad': ''.join(f'{x:02d}' for x in rs), 'colsums_pad': ''.join(f'{x:02d}' for x in cs), 'rc_pad': ''.join(f'{x:02d}' for x in rs + cs),
         'spiral_bytes': ''.join(str(ord(c)) for c in 'gsmg.io/theseedisplanted'), 'matrix_rowbits_dec': ''.join(str(int(''.join(map(str, r)), 2)) for r in MATRIX),
         'matrix_colbits_dec': ''.join(str(int(''.join(map(str, c)), 2)) for c in zip(*MATRIX)), 'dbbi_markerbits+res61_a0': '00001000110000100110010' + RES61.translate(A0),
         'faed_a0_pairsum_mod10': ''.join(str((int(a) + int(b)) % 10) for a, b in zip(FAED.translate(A0)[0::2], FAED.translate(A0)[1::2])),
         'faed_a1_minus_dbbi_cycle': ''.join(str((int(a) - int(b)) % 10) for a, b in zip(FAED.translate(A1), (DBBI.translate(A1) * 7)[:570]))}
std = make_board()
for on, d in other.items():
    for rd in (0, 1):
        dd = d[::-1] if rd else d
        rec(f'OTHER_{on}|revdig={rd}', dd, std, ('1', '4'))
print('after other: rows', len(rows), flush=True)
# (c) direct Beaufort / Vigenere on a..i letters
KEYS = ['THEMATRIXHASYOU', 'LASTWORDSBEFOREARCHICHOICE', 'THISPASSWORD', 'MATRIXSUMLIST', 'CAUSALITY', 'COSMICDUALITY', 'WHITERABBIT', 'HALFANDBETTERHALF', 'GSMG', 'SALPHASEION',
        'THESEEDISPLANTED', 'ONEFORONEFOURFORONE', 'PRIME', 'NEO', 'ORACLE', 'ARCHITECT', 'SOURCE', 'ENTER', 'ANSTOO', 'SHABEF', 'DBIFHCEGA', 'FUBCDORA', 'INCASEYOUMANAGETOCRACKTHIS']
for sn, s in (('faed', FAED), ('dbbi', DBBI), ('res61', RES61)):
    for rd in (0, 1):
        c = s[::-1] if rd else s
        for K in KEYS:
            for fn_name, fn in (('beaufort', beaufort), ('vigdec', vig_dec), ('vigenc', vig_enc)):
                t = fn(c, K); q = qscore(t)
                ctrl = [qscore(fn(c, randkey(len(K)))) for _ in range(20)]
                m = sum(ctrl) / 20; sd = (sum((v - m) ** 2 for v in ctrl) / 20) ** .5 or 1e-9
                rows.append({'tag': f'DIRECT_{sn}|revdig={rd}|{fn_name}|{K}', 'q': round(q, 3), 'z': round((q - m) / sd, 2), 'len': len(t), 'frags': frags(t), 'text': t}); cands.add(t)
rows.sort(key=lambda r: -r['z'])
json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/wf/lens_cb3_round2_rows.json', 'w'), indent=0)
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto_r2.txt', 'w') as f:
    for c in sorted(cands):
        if c: f.write(c + '\n')
print('rows', len(rows), 'cands', len(cands))
for r in rows[:15]: print(r['z'], r['q'], r['tag'], r['frags'], r['text'][:60])
print('best q overall:'); 
for r in sorted(rows, key=lambda r: -r['q'])[:8]: print(r['q'], r['z'], r['tag'], r['frags'], r['text'][:60])
print('frags>=7:', [(r['tag'], r['frags']) for r in rows if any(len(w) >= 7 for w in r['frags'])][:12])
