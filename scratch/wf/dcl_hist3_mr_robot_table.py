import json, time, urllib.request
P = ["-40,-17","-41,-18","-42,-18","-40,-18","-41,-17","42,4","25,15","82,25","28,0","-16,42","-42,16","23,2","4,24","51,52","82,28"]
out = {}
for p in P:
    url = "https://peer.decentraland.org/content/deployments?pointer=%s&onlyCurrentlyPointed=false&limit=60&entityType=scene&sortingField=entity_timestamp&sortingOrder=ASC" % p
    for attempt in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'curl/8'}), timeout=40)); deps = r.get('deployments', []); break
        except Exception as e:
            print(p, 'ERR', e); deps = None; time.sleep(15)
    if deps is None: out[p] = 'ERR'; continue
    uniq = {}
    for d in deps:
        md = d.get('metadata') or {}
        title = (md.get('display') or {}).get('title'); files = [c['key'] for c in d.get('content', [])]
        txt = json.dumps(md).lower() + ' '.join(files).lower()
        flag = [w for w in ('gsmg','zion','matrix','rabbit','puzzle','neo','morpheus','safenet','robot','btc','bitcoin','cosmic','duality','keymaker','architect','0x5d801b2b') if w in txt]
        uniq.setdefault((str(title)[:40], str(d.get('deployedBy'))[:12], tuple(flag)), []).append(time.strftime('%Y-%m-%d', time.gmtime(d['entityTimestamp']/1000)))
    out[p] = [(k, v[0], v[-1], len(v)) for k, v in uniq.items()]
    print('== %s: %d deployments, %d distinct' % (p, len(deps), len(uniq)))
    for k, v in uniq.items(): print('   ', k[0], '| by', k[1], '| flags', list(k[2]), '|', v[0], '..', v[-1], 'x%d' % len(v))
    time.sleep(6.0)
json.dump(out, open('/home/vin/bitcoin_puzzle/scratch/wf/dcl_hist3_mr_robot_table.json','w'), indent=1)
