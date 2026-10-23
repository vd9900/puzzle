import sys, base64, hashlib
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import evp
from Crypto.Cipher import AES
raw=open('/home/vin/Downloads/Telegram Desktop/ChatExport_2026-10-13/files/phase3.1_old.aes').read()
b=base64.b64decode(''.join(raw.split()))
print('old31 magic',b[:8],'salt',b[8:16].hex(),'ct',len(b)-16)
for pw in ['jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple','jacquefrescogivetitjustonesecondheisenbergsuncertaintyprinciple']:
    for dg in ('sha256','md5'):
        for p in (hashlib.sha256(pw.encode()).hexdigest(), pw):
            k,iv=evp(p.encode(),b[8:16],dg)
            pt=AES.new(k,AES.MODE_CBC,iv).decrypt(b[16:])
            pr=sum(32<=x<127 or x in (9,10,13) for x in pt)/len(pt)
            if pr>0.8 or pt[-1]<=16 and pt.endswith(bytes([pt[-1]])*pt[-1]):
                print(pw[:22],dg,'hashed' if len(p)==64 else 'raw','printable %.2f'%pr, pt[:120])
# PROGRESS.md 64/16 claim
d='dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe'
t=[];i=0
while i<len(d):
    if d[i] in 'bg' and i+1<len(d): t.append(d[i:i+2]); i+=2
    else: t.append(d[i]); i+=1
print('tokens',len(t),'distinct',len(set(t)))
