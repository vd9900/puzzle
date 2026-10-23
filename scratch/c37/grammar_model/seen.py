# usage: python3 seen.py "cand1" "cand2" ...   -> reports exact-line and normalized-substring presence
import sys, glob, re, os
R='/home/vin/bitcoin_puzzle'
files=[R+'/research/candidates.jsonl']+sorted(glob.glob(R+'/scratch/wf/cands_*'))
wide = '--wide' in sys.argv
if wide:
    files += [f for f in glob.glob(R+'/scratch/**/*.txt',recursive=True) if 'cands' in os.path.basename(f) or 'cand' in f]
cands=[a for a in sys.argv[1:] if a!='--wide']
norm=lambda s: re.sub(r'[^a-z0-9]','',s.lower())
nc=[(c,norm(c)) for c in cands]
exact={c:[] for c in cands}; sub={c:[] for c in cands}
for f in set(files):
    try: data=open(f,errors='replace').read()
    except Exception: continue
    lines=set(l.strip() for l in data.split('\n')); nlines=set(norm(l) for l in lines)
    nd=norm(data)
    for c,n in nc:
        if c in lines or n in nlines: exact[c].append(os.path.basename(f))
        elif n and n in nd: sub[c].append(os.path.basename(f))
for c,_ in nc:
    print(f'{c!r}: exact={len(exact[c])} {exact[c][:3]} | norm-substr={len(sub[c])} {sub[c][:3]}')
