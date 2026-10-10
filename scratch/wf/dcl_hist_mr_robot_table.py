import json, time, urllib.request, re
out = {}
for p in ["4,15","15,4","32,82","82,32","42,25","2,0","25,42","0,2"]:
    url = "https://peer.decentraland.org/content/deployments?pointer=%s&onlyCurrentlyPointed=false&limit=50&entityType=scene&sortingField=entity_timestamp&sortingOrder=ASC" % p
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
        txt = json.dumps(md).lower()
        flag = [w for w in ('gsmg','zion','matrix','rabbit','puzzle','neo','morpheus','safenet','robot') if w in txt or any(w in f.lower() for f in files)]
        rows.append((d['entityTimestamp'], time.strftime('%Y-%m-%d', time.gmtime(d['entityTimestamp']/1000)), str(title)[:40], str(d.get('deployedBy'))[:12], len(d.get('pointers',[])), flag, d['entityId']))
    out[p] = rows
    print('== %s: %d deployments' % (p, len(rows)))
    for r in rows: print('  ', r[1], '|', r[2], '| by', r[3], '| n=%d' % r[4], '| flags=', r[5], '|', r[6][:20])
    time.sleep(3.0)
json.dump(out, open('/home/vin/bitcoin_puzzle/scratch/wf/dcl_hist_mr_robot_table.json','w'), indent=1)
