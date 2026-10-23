"""Language-independent kill test: a1z26 coding of natural text (English OR Dutch) yields a high share of digit '1'
(letters a and j..s). Compare with the share of 'a' (=1) in the dbbi residual and faed. Zero-deleted variant: j=10->'1', t=20->'2'."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED
from math import comb
R61 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeeae'
EN = dict(a=8.2,b=1.5,c=2.8,d=4.3,e=12.7,f=2.2,g=2.0,h=6.1,i=7.0,j=.15,k=.77,l=4.0,m=2.4,n=6.7,o=7.5,p=1.9,q=.1,r=6.0,s=6.3,t=9.1,u=2.8,v=1.0,w=2.4,x=.15,y=2.0,z=.07)
NL = dict(a=7.49,b=1.58,c=1.24,d=5.93,e=18.91,f=.81,g=3.40,h=2.38,i=6.50,j=1.46,k=2.25,l=3.57,m=2.21,n=10.03,o=6.06,p=1.57,q=.01,r=6.41,s=3.73,t=6.79,u=1.99,v=2.85,w=1.52,x=.04,y=.04,z=1.39)
def share1(freq):
    ones = digs = 0.0
    for ch, f in freq.items():
        code = str(ord(ch) - 96).replace('0', '')   # zero-deleted (most favourable to the hypothesis: no zeros needed)
        ones += f * code.count('1'); digs += f * len(code)
    return ones / digs
for nm, fr in (('English', EN), ('Dutch', NL)):
    p = share1(fr)
    for sn, s in (('R61', R61), ('faed', FAED)):
        n = len(s); k = s.count('a')
        tail = sum(comb(n, i) * p**i * (1-p)**(n-i) for i in range(k+1))
        print(f'{nm:7s} a1z26 digit-1 share={p:.3f} | {sn}: {k}/{n}={k/n:.3f}  P(X<={k})={tail:.2e}')
