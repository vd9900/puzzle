# Homophonic "sum code": each plaintext letter = k consecutive digits whose SUM is its a1z26 index (+offset).
# Reading: faed as a (570/k) x k matrix, row-sum list -> letters. Score: best English monogram chi2 over all
# 26 Caesar offsets; compare with shuffled-faed controls (same reading). Also count common English words.
import sys, random, math
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED
E=dict(zip('abcdefghijklmnopqrstuvwxyz',[8.2,1.5,2.8,4.3,12.7,2.2,2.0,6.1,7.0,.15,.77,4.0,2.4,6.7,7.5,1.9,.1,6.0,6.3,9.1,2.8,1.0,2.4,.15,2.0,.07]))
def readings(s,k):
    d=[ 'abcdefghi'.index(c)+1 for c in s]
    for ph in range(k):
        sums=[sum(d[i:i+k]) for i in range(ph,len(d)-k+1,k)]
        for off in range(26):
            yield ph,off,''.join(chr(97+(x+off)%26) for x in sums)
def chi(t):
    n=len(t); return sum((t.count(c)-n*E[c]/100)**2/(n*E[c]/100) for c in E)
WORDS=['the','and','that','with','this','key','private','password','is','you','your']
for k in (2,3,4):
    best=min(readings(FAED,k),key=lambda r:chi(r[2]))
    ctrl=[]
    for sd in range(20):
        sh=list(FAED); random.Random(sd).shuffle(sh)
        ctrl.append(min(chi(r[2]) for r in readings(''.join(sh),k)))
    print(k,'faed best chi2 %.0f'%chi(best[2]),best[:2],best[2][:60],'| ctrl min/med %.0f/%.0f'%(min(ctrl),sorted(ctrl)[10]))
