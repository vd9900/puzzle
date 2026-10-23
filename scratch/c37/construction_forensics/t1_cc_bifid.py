"""T1: run VERBATIM CyberChef Bifid Encode/Decode (node, cc_bifid.js) on faed/dbbi/res60 with every page-string keyword;
compare with scratch/bifid.py; score outputs with English quadgrams + BIP39 4-letter-prefix coverage vs shuffled controls."""
import sys, json, subprocess, random, statistics, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import *
import bifid, textmodel, pickle
# NOTE: scratch/quadgrams.pkl is CONTAMINATED (chat transcript contains the btcseed decode 19x); use the clean model
sys.path.insert(0, "/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics"); import quad_indep
# quadgrams_clean.pkl is ALSO contaminated -> independent Carroll-only model
textmodel.LOGP, textmodel.FLOOR = quad_indep.LOGP, quad_indep.FLOOR
HERE = '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics'
RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
W = open('/home/vin/predict_Future/dream11/venv/lib/python3.12/site-packages/bip_utils/bip/bip39/wordlist/english.txt').read().split()
PFX = {w[:4] for w in W}
def bip_cov(t):  # greedy max fraction of text covered by BIP39 words (full word or 4-letter prefix), DP
    t = t.lower(); n = len(t); best = [0]*(n+1)
    for i in range(n-1, -1, -1):
        b = best[i+1]
        for w in W:
            if t.startswith(w, i): b = max(b, len(w)+best[i+len(w)])
        best[i] = b
    return best[0]/n
INPUTS = {'faed': FAED, 'dbbi': DBBI, 'res60': RES60}
KEYS = {'(none)': '', 'dbbi': DBBI, 'res60': RES60, 'faed': FAED, 'matrixsumlist': 'matrixsumlist',
        'lastwordsbeforearchichoice': 'lastwordsbeforearchichoice', 'thispassword': 'thispassword',
        'shabefourfirsthintisyourlastcommand': Z3, 'enter': 'enter', 'shabefanstoo': 'shabefanstoo',
        'Z1letters': re.sub('[^a-z]', '', Z1), 'Z2letters': re.sub('[^a-z]', '', Z2), 'causality': 'causality',
        'yellowbluepr...': 'yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang'}
def run(jobs):
    p = HERE + '/_jobs.json'; json.dump(jobs, open(p, 'w'))
    r = subprocess.run(['node', HERE + '/cc_bifid.js', HERE + '/cc_src', p], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)
jobs = [dict(op=op, inp=i, kname=k, input=INPUTS[i], key=KEYS[k]) for op in ('dec', 'enc') for i in INPUTS for k in KEYS]
res = run(jobs)
# (a) equivalence with bifid.py on faed/dbbi key
r0 = [r for r in res if r['op'] == 'dec' and r['inp'] == 'faed' and r['kname'] == 'dbbi'][0]
print('CyberChef square (key=dbbi):', r0['square'], '| bifid.py CANON:', bifid.CANON.upper())
print('CyberChef Decode(faed,key=dbbi) == bifid.py BIF:', r0['out'] == bifid.BIF, '| head:', r0['out'][:40])
# (b) python reimpl equivalence for every job
mism = 0
for r in res:
    sq = r['square'].lower(); per = len(r['input'])
    ref = (bifid.bifid_decrypt if r['op'] == 'dec' else bifid.bifid_encrypt)(r['input'], sq, per)
    if ref != r['out']: mism += 1; print('MISMATCH', r['op'], r['inp'], r['kname'])
print('python-vs-CyberChef mismatches over', len(res), 'jobs:', mism)
# (c) controls: 200 shuffled inputs per (op, input) decoded with key dbbi -> score distribution
rng = random.Random(37)
ctrl_jobs = []
for op in ('dec', 'enc'):
    for i, s in INPUTS.items():
        for kn, kv in KEYS.items():
            for t in range(100):
                l = list(s); rng.shuffle(l); ctrl_jobs.append(dict(op=op, inp=i, kname=kn, input=''.join(l), key=kv))
cres = run(ctrl_jobs)
dist = {}
for r in cres: dist.setdefault((r['op'], r['inp'], r['kname']), []).append(textmodel.score(r['out']))
lines = []
for r in res:
    sc = textmodel.score(r['out']); d = dist[(r['op'], r['inp'], r['kname'])]
    z = (sc - statistics.mean(d)) / statistics.pstdev(d)
    bc = bip_cov(r['out'][:120])
    lines.append((z, r['op'], r['inp'], r['kname'], round(sc, 3), round(bc, 2), r['out'][:48]))
lines.sort(reverse=True)
print('top by quadgram z (vs 100 shuffled-input controls with the SAME key/op/input):')
for l in lines[:12]: print(' z=%+.2f %s %s key=%s q=%s bip39cov=%s %s' % l)
print('max z overall: %.2f over %d keyed decodes' % (lines[0][0], len(lines)))
# planted control: encode an English seed-like plaintext with key dbbi via CyberChef, decode back
pt = 'btcseedabandonabilityableaboutaboveabsentabsorbabstractabsurdabuse'
e = run([dict(op='enc', inp='pt', kname='dbbi', input=pt, key=DBBI)])[0]['out']
d = run([dict(op='dec', inp='ct', kname='dbbi', input=e, key=DBBI)])[0]['out']
print('planted roundtrip ok:', d == pt, '| score planted', round(textmodel.score(pt), 3), 'bip39cov', round(bip_cov(pt), 2))
json.dump(res, open(HERE + '/t1_results.json', 'w'), indent=0)
