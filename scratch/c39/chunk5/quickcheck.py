import base64, hashlib, sys
from Crypto.Cipher import AES
A='/home/vin/bitcoin_puzzle/research/artifacts/'
dbbi=open(A+'cycle02/salphaseion-dbbi.txt').read().strip()
def load(p):
    r=base64.b64decode(''.join(open(p).read().split())); assert r[:8]==b'Salted__'; return r[8:16],r[16:]
def evp(pw,salt,h):
    d=b'';pr=b''
    while len(d)<48:
        pr=h(pr+pw+salt).digest(); d+=pr
    return d[:32],d[32:48]
def dec(pw,blob,h=hashlib.md5):
    s,ct=load(A+blob); k,iv=evp(pw,s,h); pt=AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
    p=pt[-1]; ok=1<=p<=16 and pt.endswith(bytes([p])*p); return ok,p,pt
# 1 Test User 422
m={c:str(i+1) for i,c in enumerate('abcdefghi')}; ds=''.join(m[c] for c in dbbi)
print('1) dbbi a=1..i=9 prefix',ds[:6],'digit sum',sum(map(int,ds)),'len',len(ds))
# 2 z positions in blobs
for f in ['salphaseion-small.b64','phase32-inner.b64']:
    b=''.join(open(A+f).read().split()); print('2)',f,'len',len(b),'z positions(1-based)',[i+1 for i,c in enumerate(b) if c=='z'])
# 3 URL LSB parity
u='gsmg.io/theseedisplanted'; bits=''.join(str(ord(c)&1) for c in u); print('3) url parity',bits,hex(int(bits,2)))
# 5 Boulayo indices on btcseed (from chat #75945)
bs='btcseeddeoemckeadhbschdkbdcsdkdvbxcpcochcrdicibqeebddbcndsbdcpdgcpdncncsescgddclenbmcuducqcacdeld'
idx=[51,49,43,45,32,50,36,12,44,14,40,34,41,43,20,30,56,52]
print('5) 1-based',''.join(bs[i-1] for i in idx),' 0-based',''.join(bs[i] for i in idx))
# 4 Marc chain
pw=b'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist'
ok,p,pt=dec(pw,'salphaseion-small.b64'); print('4) small blob literal tokens md5: padok',ok,'pad',p,'len',len(pt)-p if ok else None, pt[:32].hex() if ok else '')
if ok:
    B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    def b58c(b):
        b=b+hashlib.sha256(hashlib.sha256(b).digest()).digest()[:4]; n=int.from_bytes(b,'big'); s=''
        while n: n,r=divmod(n,58); s=B58[r]+s
        return '1'*(len(b)-len(b.lstrip(b'\0')))+s
    for lab,w in [('wif_u',b58c(b'\x80'+pt[:32])),('wif_c',b58c(b'\x80'+pt[:32]+b'\x01'))]:
        for hn,h in [('md5',hashlib.md5),('sha256',hashlib.sha256)]:
            ok2,p2,pt2=dec(w.encode(),'phase32-inner.b64',h); print('   inner via',lab,hn,'padok',ok2,'pad',p2,pt2[:14].hex() if ok2 else '')
# 6/7/8 explicitly claimed passwords
cl={'ZION':b'ZION','sha256hex(ZION)':hashlib.sha256(b'ZION').hexdigest().encode(),'Z1ON0101':b'Z1ON0101','zion0101':b'zion0101','test151':b'test151',
    'sha256hex(followthewhiterabbit)+adipfBrr':(hashlib.sha256(b'followthewhiterabbit').hexdigest()+'adipfBrr').encode()}
for k,v in cl.items():
    r=[]
    for f in ['salphaseion-small.b64','phase32-inner.b64','cosmic-duality.b64']:
        for hn,h in [('md5',hashlib.md5),('sha256',hashlib.sha256)]:
            o,pp,_=dec(v,f,h)
            if o: r.append(f'{f.split(".")[0]}/{hn}:pad{pp}')
    print('6)',k,'valid-padding hits:',r)
