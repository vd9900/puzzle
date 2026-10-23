import sys
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
from collections import defaultdict
# colour bits in spiral order: LSB of each of 24 bytes of 'gsmg.io/theseedisplanted' blue=1 yellow=0
col=[c&1 for c in b'gsmg.io/theseedisplanted']
print('colour bits',''.join(map(str,col)), sum(col))
def consistent(seg,bits):
    d=defaultdict(set)
    for ch,b in zip(seg,bits): d[ch].add(b)
    return sum(len(v)>1 for v in d.values()), dict((k,sorted(v)) for k,v in d.items())
for name,seg in [('faed[-24:]',FAED[-24:]),('faed[:24]',FAED[:24]),('faed[546:]',FAED[546:]),('faed[538:562]',FAED[538:562])]:
    for b in (col, col[::-1]):
        print(name, consistent(seg,b)[0], seg)
# I Ching: f,g,h,i subsequence -> yang(7,9)=1 yin(6,8)=0
sub=[c for c in FAED if c in 'fghi']
bits=''.join('1' if c in 'gi' else '0' for c in sub)
print(len(sub), bytes(int(bits[i:i+8],2) for i in range(0,len(bits)-7,8))[:40])
b64='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
print(''.join(b64[int(bits[i:i+6],2)] for i in range(0,len(bits)-5,6))[:60])
