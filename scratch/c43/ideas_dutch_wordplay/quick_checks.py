# Dutch-lens quick feasibility checks (cycle 43). Run: cd scratch && python3 c43/ideas_dutch_wordplay/quick_checks.py
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
g=lambda w: sum(ord(c)-96 for c in w)
# 1) Dutch gematria of colour words
for w in ['geel','blauw','wit','rood','zwart']: print('gematria',w,g(w))
# 2) could faed carry Dutch-gematria markers 'bi'(29)/'ei'(59) at primes like dbbi's b/be?  count available bigrams
cnt=sum(FAED[i:i+2] in ('bi','ei') for i in range(len(FAED)-1))
print('faed bi/ei bigrams:',cnt,' primes needed ~',len(primes_upto(570)))
# 3) ring ('lijst' = frame) sums of the 14x14 Phase-0 matrix
N=14
rings=[]
for r in range(7):
    cells=[(i,j) for i in range(r,N-r) for j in range(r,N-r) if i in (r,N-1-r) or j in (r,N-1-r)]
    rings.append((sum(MATRIX[i][j] for i,j in cells), len(cells)))
ones=[a for a,_ in rings]; zeros=[n-a for a,n in rings]
print('ring ones',ones,'ring zeros',zeros)
cands=[]
for nm,L in (('ones',ones),('zeros',zeros)):
    for o,LL in (('out-in',L),('in-out',L[::-1])):
        for sep in ('',',',' ','-',', '):
            cands.append((f'ring {nm} {o} sep={sep!r}', sep.join(map(str,LL))))
        cands.append((f'ring {nm} {o} sum', str(sum(LL))))
        cands.append((f'matrixsumlist+ring {nm} {o}', 'matrixsumlist'+''.join(map(str,LL))))
test_candidates(cands,'ring (lijst=frame) sums')
# 4) 'voor' (before = in front of) + first-ever creator hint 'giveit = givetit': prefix construction
SALPH='GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
answers=['lastwordsbeforearchichoice','thispassword','lastwordsbeforearchichoicethispassword','matrixsumlist','enter','yinyang',
         'cosmicduality','anstoo','theseedisplanted','causality','thematrixhasyou',SALPH,
         'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple','ourfirsthintisyourlastcommand']
pre=['giveit','givetit','giveit=givetit','giveitgivetit']
c2=[(f'{p}+{a[:20]}',p+a) for p in pre for a in answers]
test_candidates(c2,'voor-prefix giveit/givetit')
