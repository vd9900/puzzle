import json,re,sys
d=json.load(open('/home/vin/bitcoin_puzzle/data/user_supplied/telegram/ocr_index.json'))
rows=[json.loads(l) for l in open('/home/vin/bitcoin_puzzle/data/user_supplied/telegram/text_export.jsonl')]
creator=json.load(open('/home/vin/bitcoin_puzzle/data/user_supplied/telegram/creator_all.json'))
def norm(t): return re.findall(r'[a-z0-9]+',t.lower())
def sh(ws,n=3): return {' '.join(ws[i:i+n]) for i in range(len(ws)-n+1)}
allsh=set(); crsh=set()
for r in rows:
    t=r.get('text'); t=t if isinstance(t,str) else json.dumps(t)
    allsh|=sh(norm(t))
for m in creator:
    t=m['text'] if isinstance(m['text'],str) else json.dumps(m['text'])
    crsh|=sh(norm(t))
r=re.compile(r'(jrk|bgrt|irk ?bert|jrkbgrt)',re.I)
out=[]
for i,x in enumerate(d):
    t=x['ocr']
    if not r.search(t): continue
    # split into paragraphs/lines
    lines=[l.strip() for l in re.split(r'\n',t) if len(norm(l))>=6]
    unm=[]
    for l in lines:
        s=sh(norm(l))
        if not s: continue
        cov_all=len(s&allsh)/len(s); cov_cr=len(s&crsh)/len(s)
        if cov_all<0.35: unm.append((round(cov_all,2),round(cov_cr,2),l[:160]))
    out.append((i,x['date'][:10],x['msg_id'],len(lines),unm))
for i,dt,mid,nl,unm in out:
    if unm:
        print(f'## {i} {dt} msg{mid} lines={nl} unmatched={len(unm)}')
        for u in unm[:8]: print('    ',u)
