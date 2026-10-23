import sys
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def expand(s,start):
    bits=[];b=start
    for c in s:
        bits+= [b]*(ord(c)-96); b^=1
    return bits
def tobytes(bits):
    return bytes(int(''.join(map(str,bits[i:i+8])),2) for i in range(0,len(bits)-7,8))
for name,s in [('R60',R60),('dbbi',DBBI),('faed',FAED),('Z-free faed[4:]',FAED[4:])]:
    for rev in (0,1):
        t=s[::-1] if rev else s
        for st in (0,1):
            bt=tobytes(expand(t,st))
            print(name,rev,st,len(bt),bt[:60])
# planted self-test: text -> bits -> RLE -> letters -> back
txt=b'thisisatest'
bits=[int(b) for ch in txt for b in format(ch,'08b')]
runs=[];cur=bits[0];n=0
for b in bits:
    if b==cur:n+=1
    else: runs.append(n);cur=b;n=1
runs.append(n)
print('planted runs max',max(runs), ''.join(chr(96+r) for r in runs))
