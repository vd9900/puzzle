from common import *
import itertools, re
P=primes_upto(100)
bits84='00001000110000100110010'; bits83='00001000110000100110011'
pr23=P[:23]
sets={}
for name,bits in (('L84',bits84),('L83',bits83)):
    y=[p for p,b in zip(pr23,bits) if b=='1']; b=[p for p,bb in zip(pr23,bits) if bb=='0']
    sets[name]=(y,b)
    print(name,'yellow',y,sum(y),'blue',b,sum(b))
speech=open('speech32_words.txt').read().split()
speech_l=re.sub('[^a-z]','',open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().lower())
cb='incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive'
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
import pathlib
p2=pathlib.Path('/home/vin/bitcoin_puzzle/research/artifacts/phase2.txt').read_text(errors='ignore'); p3=pathlib.Path('/home/vin/bitcoin_puzzle/research/artifacts/phase3.txt').read_text(errors='ignore')
p2w=re.findall(r"[A-Za-z']+",p2); p3w=re.findall(r"[A-Za-z']+",p3)
arch=open('arch_scene_chat.txt').read(); archw=re.findall(r"[A-Za-z']+",arch)
cands=[]
def add(d,s): 
    if s: cands.append((d,s))
for name,(y,b) in sets.items():
    for lab,L in (('y',y),('b',b),('yb',y+b),('by',b+y)):
        add(f'{name}{lab} concat',''.join(map(str,L))); add(f'{name}{lab} comma',','.join(map(str,L))); add(f'{name}{lab} space',' '.join(map(str,L)))
    sy,sb=sum(y),sum(b)
    for s in (f'{sy}{sb}',f'{sb}{sy}',f'{sy} {sb}',f'{sy},{sb}',f'yellow{sy}blue{sb}',f'blue{sb}yellow{sy}',str(sy),str(sb),str(sy+sb),str(sy*sb),f'{sy}-{sb}',f'Y{sy}B{sb}',f'yellow {sy} blue {sb}'):
        add(f'{name} sums',s)
    # word selection
    for tn,words in (('speech',speech),('p2',p2w),('p3',p3w),('arch',archw),('cb',cb.split('z'))):
        for base in (0,1):
            for lab,L in (('y',y),('b',b),('yb',y+b),('p23',pr23)):
                ws=[words[(i-base)] for i in L if 0<=i-base<len(words)]
                add(f'{name} {tn} words {lab} b{base}',''.join(ws).lower()); add(f'{name} {tn} WORDS {lab} b{base}',''.join(ws)); add(f'{name} {tn} words {lab} b{base} sp',' '.join(ws).lower())
    # letter selection
    for tn,txt in (('speech',speech_l),('cb',cb),('dbbi',DBBI),('faed',FAED),('res60',RES60),('matbits',''.join(str(x) for row in MATRIX for x in row))):
        for base in (0,1):
            for lab,L in (('y',y),('b',b),('yb',y+b),('p23',pr23)):
                add(f'{name} {tn} letters {lab} b{base}',''.join(txt[i-base] for i in L if 0<=i-base<len(txt)))
# Architect numbers
for s in ['23167','231607','2316and7','twentythreesixteenseven','23 16 7','23-16-7','16+7','167','716','16723']: add('archnums',s)
seen=set(); uniq=[]
for d,s in cands:
    if s not in seen: seen.add(s); uniq.append((d,s))
test_candidates(uniq,'yellow/blue prime sets & selections')
