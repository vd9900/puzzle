# Derivation: speech line "your life is the sum of a remainder of an unbalanced equation inherent to the programming of
# [the matrix -> 'this puzzle']" + checkerboard "private keys belong to half and better half" + roadmap "matrix sumlist".
# Reading: remainder = X mod n (secp256k1 order, the curve y^2=x^3+7 is the 'unbalanced equation'), key = sum of remainders.
# Tiny principled set (<40 keys), oracle = exact P2PKH address match. No loop over windows/offsets.
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0,'/home/vin/bitcoin_puzzle')
from common import DBBI, FAED
from bw_oracle import addrs
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P=2**256-2**32-977
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
T={'1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe','17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'}
v=lambda s:int(''.join(str(ord(c)-96) for c in s))
objs={'dbbi':v(DBBI),'R60':v(R60),'faed':v(FAED),'faedA':v(FAED[:285]),'faedB':v(FAED[285:]),
      'dbbi_rev':v(DBBI[::-1]),'faed_rev':v(FAED[::-1])}
cands={}
for k,x in objs.items():
    cands[k+'%n']=x%N; cands[k+'%p']=x%P
for a,b in [('dbbi','faed'),('R60','faed'),('faedA','faedB'),('dbbi','R60'),('dbbi_rev','faed_rev')]:
    cands[f'({a}%n+{b}%n)%n']=(objs[a]%N+objs[b]%N)%N
    cands[f'({a}%n-{b}%n)%n']=(objs[a]%N-objs[b]%N)%N
    cands[f'({a}*{b})%n']=(objs[a]*objs[b])%N
# self-test: planted key reachable
import hashlib
assert addrs(1)['compressed']=='1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH'
hits=0
for name,k in cands.items():
    a=addrs(k)
    if set(a.values())&T: print('HIT',name,hex(k)); hits+=1
print(len(cands),'keys tested, hits',hits)
