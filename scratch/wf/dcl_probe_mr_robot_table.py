import json, time, urllib.request, itertools, sys
X = [2, 32, 42, -42, 4, -32, -4, -2]
Y = [0, 82, 25, -16, 16, 15, -82, -25, -15]
pairs = set()
for x in X:
    for y in Y:
        pairs.add((x,y)); pairs.add((y,x))
# positional + GPS-derived + sums
for p in [(2,0),(32,82),(42,25),(-42,-16),(4,15),(51,52),(28,0),(4,24),(23,2),(80,122),(122,80),(-41,-17),(-41,-16)]:
    pairs.add(p); pairs.add((p[1],p[0]))
pairs = sorted(p for p in pairs if -150<=p[0]<=163 and -150<=p[1]<=158)
print('pointers', len(pairs))
ptrs = ['%d,%d'%p for p in pairs]
found = {}
for i in range(0, len(ptrs), 30):
    chunk = ptrs[i:i+30]
    req = urllib.request.Request('https://peer.decentraland.org/content/entities/active', data=json.dumps({'pointers':chunk}).encode(), headers={'Content-Type':'application/json','User-Agent':'curl/8'})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        print('ERR', e); r = []
    for ent in r:
        md = ent.get('metadata',{})
        title = md.get('display',{}).get('title'); owner = md.get('owner'); base = md.get('scene',{}).get('base')
        files = [c['file'] for c in ent.get('content',[])]
        hit = [p for p in ent['pointers'] if p in chunk]
        found[ent['id']] = (hit, title, owner, base, ent.get('timestamp'), len(ent['pointers']), files[:12])
    time.sleep(1.0)
for k,v in found.items():
    print('SCENE', k, 'queried_ptrs=', v[0], 'title=', v[1], 'owner=', v[2], 'base=', v[3], 'ts=', v[4], 'nparcels=', v[5], 'files=', v[6])
print('total scenes', len(found))
json.dump({'pointers':ptrs,'found':found}, open('/home/vin/bitcoin_puzzle/scratch/wf/dcl_probe_mr_robot_table.json','w'), indent=1)
