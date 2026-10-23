# c40 sumlist_pw: page-block matrix row/column sum lists as the literal answer -> AES password (raw + sha256hex)
import sys, re, json, glob, os
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from common import DBBI, FAED, MATRIX
from tools.gsmg import extract_grid, SOURCES
OUT = '/home/vin/bitcoin_puzzle/scratch/c40/sumlist_pw'
CAP_CANDS = 9500   # x2 forms (raw + sha256hex) -> <= 19,000 password strings (hard cap 20,000)

R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
assert len(R60) == 60
R61 = R60 + 'e'
RES56 = DBBI.replace('be', '').replace('b', '')
assert len(RES56) == 56, len(RES56)
C = extract_grid(SOURCES / 'gsmg-puzzle.png')['colors']
WBY = {'black': 1, 'white': 0, 'blue': 2, 'yellow': 25, 'near_white': 0}
IMG01 = [MATRIX[r][c] for r in range(14) for c in range(14)]
IMGBY = [WBY[C[r][c]] for r in range(14) for c in range(14)]
assert sum(IMG01) == 101 and sum(IMGBY) == 86 + 30 + 225

def val(s, a0): return [ord(ch) - (97 if a0 else 96) for ch in s]
blocks = []  # (name, values)
for nm, s in (('dbbi', DBBI), ('r60', R60), ('r61', R61), ('res56', RES56), ('faed', FAED)):
    blocks.append((nm + '_a1', val(s, False)))
    blocks.append((nm + '_a0', val(s, True)))
blocks.append(('img01', IMG01)); blocks.append(('imgB2Y25', IMGBY))

def widths(n):
    ws = set(range(2, 41)) | {d for d in range(2, n) if n % d == 0}
    return sorted(w for w in ws if w < n)

def sums(v, w):
    rows = [sum(v[i:i + w]) for i in range(0, len(v), w)]
    cols = [sum(v[j::w]) for j in range(w)]
    return rows, cols

def fmts(L):
    s = [str(x) for x in L]
    return {'cat': ''.join(s), 'comma': ','.join(s), 'space': ' '.join(s), 'py': str(L)}
def fmts2(A, B):  # row list followed by column list
    s = [str(x) for x in A + B]
    return {'cat': ''.join(s), 'comma': ','.join(s), 'space': ' '.join(s), 'pyflat': str(A + B),
            'pynest': str([A, B]), 'py2': str(A) + str(B), 'py2sp': str(A) + ' ' + str(B)}

# priority tiers: 0 = brief's explicit formats (rows, cols, rows+cols); 1 = compact JSON; 2 = cols+rows (column-major fill)
cands = []  # (tier, desc, string)
for nm, v in blocks:
    for w in widths(len(v)):
        rows, cols = sums(v, w)
        tag = f'{nm}|w{w}' + ('|exact' if len(v) % w == 0 else '')
        for k, s in fmts(rows).items(): cands.append((0, tag + '|rows|' + k, s))
        for k, s in fmts(cols).items(): cands.append((0, tag + '|cols|' + k, s))
        f2 = fmts2(rows, cols)
        for k in ('cat', 'comma', 'space', 'pyflat', 'pynest'): cands.append((0, tag + '|rows+cols|' + k, f2[k]))
        for k in ('py2', 'py2sp'): cands.append((1, tag + '|rows+cols|' + k, f2[k]))
        cands.append((1, tag + '|rows|json', json.dumps(rows, separators=(',', ':'))))
        cands.append((1, tag + '|cols|json', json.dumps(cols, separators=(',', ':'))))
        cands.append((1, tag + '|rows+cols|jsonflat', json.dumps(rows + cols, separators=(',', ':'))))
        cands.append((1, tag + '|rows+cols|jsonnest', json.dumps([rows, cols], separators=(',', ':'))))
        f3 = fmts2(cols, rows)
        for k in ('cat', 'comma', 'space', 'pyflat', 'pynest'): cands.append((2, tag + '|cols+rows|' + k, f3[k]))

# ---- dedupe: previously tested exact password-forms (fastcheck + oracle normalizations) of all ledger lines
R = '/home/vin/bitcoin_puzzle'
files = [R + '/research/candidates.jsonl'] + sorted(glob.glob(R + '/scratch/wf/cands_*'))
wide = [f for f in glob.glob(R + '/scratch/**/*.txt', recursive=True) if ('cands' in os.path.basename(f) or 'cand' in f) and '/c40/sumlist_pw/' not in f]
files = sorted(set(files + wide))
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
lines = set()
def strings_in(o):
    if isinstance(o, str): yield o
    elif isinstance(o, dict):
        for x in o.values(): yield from strings_in(x)
    elif isinstance(o, list):
        for x in o: yield from strings_in(x)
for f in files:
    try: data = open(f, errors='replace').read()
    except Exception: continue
    for l in data.split('\n'):
        l2 = l.strip()
        if not l2: continue
        lines.add(l2); lines.add(l.rstrip('\n'))
        if f.endswith('.jsonl') or f.endswith('.tsv'):
            try:
                for s in strings_in(json.loads(l2)): lines.add(s.strip())
            except Exception: pass
            for s in l2.split('\t'): lines.add(s.strip())
tested = set()
for l in lines:
    tested.update({l, l.lower(), l.upper(), re.sub(r'\s+', '', l.lower()), re.sub(r'\s+', '', l), norm(l), re.sub(r'[^A-Za-z0-9]', '', l), l.strip()})
nlines = {norm(l) for l in lines}
uniq = {}
for t, d, s in cands:
    if s not in uniq or t < uniq[s][0]: uniq[s] = (t, d)
n_dup_internal = len(cands) - len(uniq)
kept, already, seenpy_norm = [], [], 0
for s, (t, d) in uniq.items():
    if s in tested: already.append((t, d, s)); continue
    if norm(s) in nlines: seenpy_norm += 1
    kept.append((t, d, s))
kept.sort(key=lambda x: x[0])
by_tier = {}
for t, d, s in kept: by_tier[t] = by_tier.get(t, 0) + 1
sel = kept[:CAP_CANDS]
open(OUT + '/cands.txt', 'w').write('\n'.join(s for t, d, s in sel) + '\n')
open(OUT + '/cands_desc.tsv', 'w').write('\n'.join(f'{t}\t{d}\t{s}' for t, d, s in sel) + '\n')
open(OUT + '/already_tested.tsv', 'w').write('\n'.join(f'{t}\t{d}\t{s}' for t, d, s in already) + '\n')
stats = dict(ledger_files=len(files), ledger_lines=len(lines), generated=len(cands), unique=len(uniq), internal_dups=n_dup_internal,
             already_tested_exact=len(already), new=len(kept), new_by_tier=by_tier, seenpy_normalized_line_match_among_new=seenpy_norm,
             selected=len(sel), password_strings=2 * len(sel), blocks={nm: len(v) for nm, v in blocks})
print(json.dumps(stats, indent=1))
json.dump(stats, open(OUT + '/gen_stats.json', 'w'), indent=1)
