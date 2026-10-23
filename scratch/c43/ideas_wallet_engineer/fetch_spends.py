#!/usr/bin/env python3
"""Fetch all txs of the prize address from blockstream, keep those spending from it; save raw json."""
import json, urllib.request, time
A='1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
def get(u):
    for i in range(3):
        try:
            return json.load(urllib.request.urlopen(u, timeout=30))
        except Exception as e:
            time.sleep(2)
    raise SystemExit('fail '+u)
txs=[]; last=None
while True:
    u=f'https://blockstream.info/api/address/{A}/txs/chain' + (f'/{last}' if last else '')
    page=get(u)
    if not page: break
    txs+=page; last=page[-1]['txid']
    if len(page)<25: break
spends=[t for t in txs if any(v.get('prevout') and v['prevout'].get('scriptpubkey_address')==A for v in t['vin'])]
print(len(txs),'txs;',len(spends),'spending txs')
json.dump(spends,open('prize_spends.json','w'),indent=1)
for t in spends:
    n=sum(1 for v in t['vin'] if v['prevout'].get('scriptpubkey_address')==A)
    print(t['txid'], t['status'].get('block_height'), 'inputs from prize:',n, 'total vin',len(t['vin']))
