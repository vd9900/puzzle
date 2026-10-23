import re,sys,glob,os
D='/home/vin/bitcoin_puzzle/data/user_supplied/cosmic_duality/pages'
pats=sys.argv[1:]
W=int(os.environ.get('W','60'))
for f in sorted(glob.glob(D+'/p*.txt')):
    t=re.sub(r'\s+',' ',open(f,errors='replace').read())
    t=re.sub(r'-\s(?=[a-z])','',t)  # dehyphenate roughly
    for p in pats:
        for m in re.finditer(p,t,re.I):
            s=max(0,m.start()-W); e=min(len(t),m.end()+W)
            print(os.path.basename(f)[1:4], '|', m.group(0), '|', t[s:e])
