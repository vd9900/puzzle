# Critic quick check (idea 2): is faed (g in {0,7}) a window of the decimal printout of any puzzle byte object?
import sys, re, glob, base64, hashlib, os
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI, BLOBS
sys.set_int_max_str_digits(0)
R='/home/vin/bitcoin_puzzle/'
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
objs={}
for f in glob.glob(R+'research/artifacts/*.txt')+glob.glob(R+'research/artifacts/*.b64')+[R+'research/sources/gsmg-puzzle.png',R+'research/sources/salphaseion.html']+glob.glob(R+'research/sources/community-*.png'):
    if not os.path.exists(f): continue
    b=open(f,'rb').read(); objs[os.path.basename(f)]=b
    txt=b.decode('latin1')
    for i,m in enumerate(re.finditer(r'((?:[A-Za-z0-9+/=]{40,}\s*){2,})',txt)):
        try:
            d=base64.b64decode(re.sub(r'\s','',m.group(1)))
            objs[f'{os.path.basename(f)}#b64{i}']=d; objs[f'{os.path.basename(f)}#b64{i}-nohdr']=d[16:]
        except Exception: pass
for k,(s,c) in BLOBS.items(): objs['blob_'+k]=b'Salted__'+s+c; objs['blob_'+k+'_ct']=c
for pw in ['causality','jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple','theseedisplanted','gsmg.io/theseedisplanted','thematrixhasyou','matrixsumlist','enter']:
    h=hashlib.sha256(pw.encode()).digest(); objs['sha_'+pw]=h; objs['shahex_'+pw]=h.hex().encode()
def pat(s): return ''.join('[07]' if c=='g' else str('abcdefghi'.index(c)+1) for c in s)
probes={}
for nm,s in (('faed',FAED),('faed_rev',FAED[::-1]),('R60',R60),('dbbi',DBBI)):
    for st in range(0,len(s)-14,7): probes[(nm,st)]=re.compile(pat(s[st:st+14]))
# planted: take blob_cosmic decimal digits 100..240, write as letters with 0/7->g; must be found
cos=str(int.from_bytes(objs['blob_cosmic'],'big'))
plant=''.join('g' if d in '07' else 'abcdefghi'[int(d)-1] for d in cos[100:240])
pp=re.compile(pat(plant[:14]))
print('planted found at',[m.start() for m in pp.finditer(cos)])
tot=0;hits=[]
for k,b in objs.items():
    if not b: continue
    reps={'be':str(int.from_bytes(b,'big')),'le':str(int.from_bytes(b,'little')),'dec3':''.join('%03d'%x for x in b),'decv':''.join(str(x) for x in b)}
    for rn,d in reps.items():
        tot+=len(d)
        for pk,p in probes.items():
            for m in p.finditer(d): hits.append((k,rn,pk,m.start()))
print('objects',len(objs),'total digits scanned',tot,'hits',hits[:20])
