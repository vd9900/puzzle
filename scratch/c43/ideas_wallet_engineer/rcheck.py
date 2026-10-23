#!/usr/bin/env python3
"""ECDSA signature hygiene of the 6 on-chain prize-key signatures: r reuse, s reuse, low-r grinding, small/structured nonces.
Oracle: any shared r (same key) -> k and d recoverable -> d*G must equal the revealed prize pubkey."""
import json
A='1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P=2**256-2**32-977
G=(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
def add(a,b):
    if a is None: return b
    if b is None: return a
    if a[0]==b[0] and (a[1]+b[1])%P==0: return None
    if a==b: l=3*a[0]*a[0]*pow(2*a[1],-1,P)%P
    else: l=(b[1]-a[1])*pow(b[0]-a[0],-1,P)%P
    x=(l*l-a[0]-b[0])%P; return (x,(l*(a[0]-x)-a[1])%P)
def der(sig):
    assert sig[0]==0x30; i=2
    assert sig[i]==2; lr=sig[i+1]; r=int.from_bytes(sig[i+2:i+2+lr],'big'); i+=2+lr
    assert sig[i]==2; ls=sig[i+1]; s=int.from_bytes(sig[i+2:i+2+ls],'big')
    return r,s,sig[-1]
sigs=[]
for t in json.load(open('prize_spends.json')):
    for j,v in enumerate(t['vin']):
        if v['prevout'].get('scriptpubkey_address')!=A: continue
        asm=v['scriptsig_asm'].split()
        sig=bytes.fromhex(asm[1]); pub=asm[3]
        r,s,ht=der(sig); sigs.append((t['txid'][:8],j,r,s,ht,pub[:10],len(asm[1])//2))
for x in sigs: print(x[0],x[1],'r=%064x'%x[2],'s=%064x'%x[3],'sighash',hex(x[4]),'pub',x[5],'siglen',x[6],'lowS',x[3]<=N//2)
rs=[x[2] for x in sigs]; ss=[x[3] for x in sigs]
print('distinct r:',len(set(rs)),'of',len(rs),' distinct s:',len(set(ss)))
print('r bit lengths:',[r.bit_length() for r in rs])
# small-nonce scan: k in 1..2^20 and k^-1 variants via x of k*G (x mod n == r)
rset=set(rs); Q=None; hit=[]
LIM=1<<20
for k in range(1,LIM+1):
    Q=add(Q,G)
    if Q[0]%N in rset: hit.append(k)
print('small nonce k<=2^20 hits:',hit)
