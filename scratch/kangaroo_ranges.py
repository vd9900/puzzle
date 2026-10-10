"""Generate candidate private-key intervals for a kangaroo finish from SalPhaseIon numeric material.
Hypothesis: key = PREFIX * B^t + r with r unknown (r < B^t). Output JSON list of {name,start,end,bits}."""
import json, sys
sys.path.insert(0,'/home/vin/bitcoin_puzzle'); sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from tools.gsmg import CURVE_ORDER as N
from common import DBBI, primes_upto
from exp05_prime_seg import segmentations
P=set(primes_upto(700))
RES={'res60':'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea','res61':'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeeae'}
# residual after removing ALL b/be tokens (56 symbols)
r=[]; i=0
while i<len(DBBI):
    if DBBI[i]=='b': i+=2 if (i+1<len(DBBI) and DBBI[i+1]=='e') else 1
    else: r.append(DBBI[i]); i+=1
RES['res56']=''.join(r)
nums={}
for name,s in RES.items():
    for rev in (False,True):
        ss=s[::-1] if rev else s; tag=name+('<' if rev else '')
        d0=''.join(str(ord(c)-97) for c in ss); d1=''.join(str(ord(c)-96) for c in ss)
        nums[tag+' base9(a=0)']=(int(d0,9),9,len(d0)); nums[tag+' dec(a=1)']=(int(d1),10,len(d1)); nums[tag+' dec(a=0)']=(int(d0),10,len(d0))
        nums[tag+' base9(a=1 as 1..9 in base10 digits)']=(int(d1),10,len(d1))
# dbbi with markers zeroed (logical) base 9
for t in segmentations(DBBI):
    L=len(t)
    z=''.join('0' if (i+1) in P else ''.join(str(ord(c)-97) for c in tok) for i,tok in enumerate(t))
    nums[f'dbbi L{L} markers->0 base9']=(int(z,9),9,len(z)); nums[f'dbbi L{L} markers->0 dec']=(int(z),10,len(z))
ranges=[]
MAXBITS=72   # cost 2^(bits/2+1) group ops; 72 -> 2^37
for name,(v,base,ndig) in nums.items():
    if v<=0: continue
    bl=v.bit_length()
    # (a) binary alignment: key = v << m, m from (256-bl-2) .. (256-bl)  (prefix occupies top bits)
    for m in range(max(0,256-bl-2),256-bl+1):
        if m<=MAXBITS and m>=0:
            start=v<<m; end=((v+1)<<m)-1
            if start<N: ranges.append({'name':f'{name} <<{m}','start':hex(start),'end':hex(min(end,N-1)),'bits':m})
    # (b) radix alignment: key = v * base^t + r, total digits = 77/78 (dec) or 81 (base 9)
    totals=(77,78) if base==10 else (81,)
    for tot in totals:
        t=tot-ndig
        if t<=0: continue
        start=v*base**t; end=(v+1)*base**t-1; bits=(end-start).bit_length()
        if start<N and bits<=MAXBITS: ranges.append({'name':f'{name} *{base}^{t}','start':hex(start),'end':hex(min(end,N-1)),'bits':bits})
# dedupe by (start,end)
seen=set(); out=[]
for r_ in ranges:
    k=(r_['start'],r_['end'])
    if k in seen: continue
    seen.add(k); out.append(r_)
out.sort(key=lambda x:x['bits'])
json.dump(out,open('kangaroo/ranges.json','w'),indent=1)
print(len(nums),'numbers ->',len(out),'ranges')
for r_ in out: print(f"{r_['bits']:3d} bits  {r_['name']}")
