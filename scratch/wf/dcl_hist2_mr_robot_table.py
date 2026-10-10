import json, time, urllib.request
P = ["-42,-16","-42,-17","-40,-16","-40,-17","-41,-15","-41,-18","-42,-15","-42,-18","-40,-15","-40,-18","-41,-16","-41,-17",
     "2,32","42,4","0,82","25,15","32,42","82,25","-16,-42","28,0","42,-16","-16,42","16,-42","-42,16","0,28","23,2","4,24","51,52","28,82","82,28"]
out = {}
for p in P:
    url = "https://peer.decentraland.org/content/deployments?pointer=%s&onlyCurrentlyPointed=false&limit=60&entityType=scene&sortingField=entity_timestamp&sortingOrder=ASC" % p
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'curl/8'}), timeout=40))
        deps = r.get('deployments', [])
    except Exception as e:
        print(p, 'ERR', e); deps = []; time.sleep(5)
    rows = []
    for d in deps:
        md = d.get('metadata') or {}
        title = (md.get('display') or {}).get('title'); owner = md.get('owner')
        files = [c['key'] for c in d.get('content', [])]
        txt = json.dumps(md).lower() + ' '.join(files).lower()
        flag = [w for w in ('gsmg','zion','matrix','rabbit','puzzle','neo','morpheus','safenet','robot','btc','bitcoin','cosmic','duality','keymaker','architect','0x5d801b2b') if w in txt]
        rows.append((d['entityTimestamp'], time.strftime('%Y-%m-%d', time.gmtime(d['entityTimestamp']/1000)), str(title)[:40], str(d.get('deployedBy'))[:12], len(d.get('pointers',[])), flag, d['entityId'][:20]))
    out[p] = rows
    uniq = {}
    for r in rows: uniq.setdefault((r[2], r[3], tuple(r[5])), []).append(r[1])
    print('== %s: %d deployments, %d distinct' % (p, len(rows), len(uniq)))
    for k, v in uniq.items(): print('   ', k[0], '| by', k[1], '| flags', list(k[2]), '|', v[0], '..', v[-1], 'x%d' % len(v))
    time.sleep(3.0)
json.dump(out, open('/home/vin/bitcoin_puzzle/scratch/wf/dcl_hist2_mr_robot_table.json','w'), indent=1)
