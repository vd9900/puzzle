import json,glob,re,sys,os
D='/home/vin/bitcoin_puzzle/scratch/dl/gh_issues_oct10'
items=[]
for p in (1,2):
    items+=json.load(open(f'{D}/issues_p{p}.json'))
byn={it['number']:it for it in items}
want=[int(x) for x in sys.argv[1:]] if len(sys.argv)>1 else sorted(byn)
for n in want:
    it=byn.get(n)
    if not it: continue
    print('='*100); print(f"#{n} {it['created_at'][:10]} by {it['user']['login']} :: {it['title']}")
    body=(it['body'] or '')
    print(body[:6000])
    cf=f'{D}/comments_{n}.json'
    if os.path.exists(cf):
        try: cs=json.load(open(cf))
        except Exception: cs=[]
        for c in cs:
            print('-'*60, f"comment {c['created_at'][:10]} by {c['user']['login']}")
            print((c['body'] or '')[:4000])
