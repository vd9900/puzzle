import sys, re, hashlib
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
A='/home/vin/bitcoin_puzzle/research/artifacts/'
# 1) dot-template 1-2-3-4-5 scan (creator dot = one elided letter convention)
texts={}
texts['speech32']=re.findall(r"[a-z']+",open('/home/vin/bitcoin_puzzle/scratch/speech32_words.txt').read().lower())
raw=open(A+'phase32.txt','rb').read().decode('latin1')
pre=raw.split('\r\n\r\n')[0]+' '+raw.split('\r\n\r\n')[1]
texts['p32pre']=re.findall(r"[a-z']+",pre.lower())
for f in ('phase2.txt','phase3.txt'):
    t=open(A+f,'rb').read().decode('latin1'); t=t.split('U2FsdGVk')[0]
    texts[f]=re.findall(r"[a-z']+",t.lower())
def L(w): return len(w.replace("'",''))
hits=[]
for name,ws in texts.items():
    for i in range(len(ws)-4):
        if [L(w) for w in ws[i:i+5]]==[1,2,3,4,5]: hits.append((name,' '.join(ws[i:i+5])))
        if [L(w) for w in ws[i:i+5]]==[5,4,3,2,1]: hits.append((name+'-rev',' '.join(ws[i:i+5])))
print('dot-template hits:',hits)
# 2) faed tail after change point (no e/g) = 'last words before' Z1 marker
tail=FAED[538:]
cands=[('tail',tail),('tailrev',tail[::-1]),('taildig',letters_to_digits(tail)),('faed+tail?',FAED[-32:])]
test_candidates(cands,'faed tail')
