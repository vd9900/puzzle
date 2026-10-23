import sys, re, html, base64, hashlib
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import evp, sha256hex, BLOBS
from Crypto.Cipher import AES
R='/home/vin/bitcoin_puzzle/research/'
d=open(R+'sources/phase2.html').read()
tas=[''.join(html.unescape(c).split()) for c in re.findall(r"<textarea\b[^>]*>(.*?)</textarea>", d, re.S|re.I)]
p3=open(R+'artifacts/phase3.txt').read()
m=re.search(r'U2FsdGVkX1[A-Za-z0-9+/=\s]+', p3); b32=''.join(m.group(0).split())
pw7='causalitySafenetLunaHSM111100x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1'
cands={'p2a':(tas[0],['causality']),'p2b':(tas[1],['causality',pw7]),'p32':(b32,['jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple',pw7])}
out={}
for name,(b64,pws) in cands.items():
    raw=base64.b64decode(b64); salt=raw[8:16]; ct=raw[16:]
    for pw in pws:
        h=sha256hex(pw)
        k,iv=evp(h.encode(),salt)
        pt=AES.new(k,AES.MODE_CBC,iv).decrypt(ct)
        if pt[-1]<=16 and pt.endswith(bytes([pt[-1]])*pt[-1]):
            pt=pt[:-pt[-1]]
            print(name,'b64len',len(b64),'salt',salt.hex(),'ctlen',len(ct),'ptlen',len(pt),'endswith_nl',pt.endswith(b'\n'),'crlf',b'\r\n' in pt,'pw',pw[:20])
            print('   head',pt[:60]); print('   tail',pt[-80:])
            out[name]=(salt,pw,h,pt)
            # salt derivation checks
            for lab,v in [('sha256(pw)',hashlib.sha256(pw.encode()).digest()),('sha256(hex)',hashlib.sha256(h.encode()).digest()),('md5(pw)',hashlib.md5(pw.encode()).digest()),('md5(hex)',hashlib.md5(h.encode()).digest())]:
                if salt in v or salt[:4] in v: print('   SALT RELATION',lab)
            lines=b64.__len__()
            break
for n,(s,c) in BLOBS.items(): print('unsolved',n,s.hex(),len(c))
