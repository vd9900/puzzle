import json, time, urllib.request
V = [2,4,0,15,32,42,-42,82,28,25,-16,16,24,23,52,51,-32,-82,-28,-25,-15,-2,-4,-24,-23,61,-61,-41,-17]
prev = set(json.load(open('/home/vin/bitcoin_puzzle/scratch/wf/dcl_probe_mr_robot_table.json'))['pointers'])
pairs = sorted({(a,b) for a in V for b in V if -150<=a<=163 and -150<=b<=158})
ptrs = ['%d,%d'%p for p in pairs]
print('pointers', len(ptrs), 'new vs prev', len([p for p in ptrs if p not in prev]))
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
        txt = json.dumps(md).lower() + ' '.join(files).lower()
        flag = [w for w in ('gsmg','zion','matrix','rabbit','puzzle','neo','morpheus','safenet','robot','5 btc','5btc','bitcoin','cosmic','duality','keymaker','architect') if w in txt]
        found[ent['id']] = dict(ptrs=hit, title=title, owner=owner, base=base, ts=ent.get('timestamp'), n=len(ent['pointers']), files=files[:12], flag=flag, deployedBy=ent.get('deployedBy'))
    time.sleep(1.0)
for k,v in found.items():
    print('SCENE', k[:18], v['ptrs'], '|', v['title'], '| owner', v['owner'], '| base', v['base'], '| n', v['n'], '| flags', v['flag'])
print('total scenes', len(found))
json.dump({'pointers':ptrs,'found':found}, open('/home/vin/bitcoin_puzzle/scratch/wf/dcl_probe2_mr_robot_table.json','w'), indent=1)
