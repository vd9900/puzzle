import hashlib, base64, sys
R = '/home/vin/bitcoin_puzzle/research/artifacts/'
dbbi = open(R+'cycle02/salphaseion-dbbi.txt').read().strip()
m91 = open(R+'phase32-checkerboard.txt').read().split()[0].strip()
sh = lambda s: hashlib.sha256(s.encode()).hexdigest()
print('len dbbi', len(dbbi), 'sha', sh(dbbi)[:16], '(claim 71fe4625)')
print('len m91', len(m91), 'sha', sh(m91)[:16], '(claim 2fbfbef7)')
A = ''.join(chr((ord(a)-ord(b))%26+65) for a,b in zip(dbbi,m91))
borrow = ''.join('1' if a<b else '0' for a,b in zip(dbbi,m91))
print('A =', A, 'YOUWON at', A.find('YOUWON'), 'sha(A)', hashlib.sha256(A.encode()).hexdigest()[:16], '(claim f1785730)')
print('borrow', borrow, 'first 1111111 at', borrow.find('1111111'), 'runs>=7:', [i for i in range(len(borrow)-6) if borrow[i:i+7]=='1111111'])
print('DBBI 1-based [1,4,21]:', dbbi[0]+dbbi[3]+dbbi[20])
print('d positions 1-based:', [i+1 for i,c in enumerate(dbbi) if c=='d'])
print('BULLSHIT a1z26 sum:', sum(ord(c)-64 for c in 'BULLSHIT'))
s='matrixsumlistlastwordsbeforearchichoiceshabefourfirsthintisyourlastcommandentershabefanstoo'
print('Diego string len', len(s), 'a1z26 sum', sum(ord(c)-96 for c in s))
n = int(''.join(str(ord(c)-96) for c in dbbi)); print('dbbi digits /5 exact?', n%5==0, str(n//5)[:30], len(str(n//5)))
print('sha GSMGIO5BTC...:', sh('GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe')[:16])
def isp(k): return k>1 and all(k%p for p in range(2,int(k**.5)+1))
print('prime 423427,11927,72911,661:', [isp(x) for x in (423427,11927,72911,661)], 'pi(661)=', sum(isp(i) for i in range(662)))
# MrNobody checkerboard parse with prefixes {b,g}
toks=[];i=0
while i<len(dbbi):
    if dbbi[i] in 'bg' and i+1<len(dbbi): toks.append(dbbi[i:i+2]); i+=2
    else: toks.append(dbbi[i]); i+=1
print('{b,g} parse: ntok', len(toks), 'distinct slots', len(set(toks)), 'ends cleanly', i==len(dbbi))
x=bytes(32)
for t in ['matrixsumlist','enter','lastwordsbeforearchichoice','thispassword','matrixsumlist','yourlastcommand','secondanswer']:
    x=bytes(a^b for a,b in zip(x,hashlib.sha256(t.encode()).digest()))
print('cosmic 7-token xor', x.hex()[:16], '(claim a795de11)')
for f in ['phase2.txt','phase3.txt','phase32.txt','phase32-inner.b64','salphaseion-small.b64','cosmic-duality.b64']:
    try:
        raw=open(R+f).read(); b=base64.b64decode(''.join(raw.split()))
        print(f, b[:8], b[8:16].hex(), len(b))
    except Exception as e: print(f, 'err', e)
