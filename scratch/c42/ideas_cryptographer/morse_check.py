# Feasibility check: Pollux (1 symbol -> . - x, homophonic) and Morbit (1 symbol -> pair of . - x)
# on faed / dbbi / R60. Structural oracle: every Morse group must be a valid code; 'xxx' forbidden.
import sys, itertools, re
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
import numpy as np
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
M={'.-':'a','-...':'b','-.-.':'c','-..':'d','.':'e','..-.':'f','--.':'g','....':'h','..':'i','.---':'j','-.-':'k','.-..':'l','--':'m','-.':'n','---':'o','.--.':'p','--.-':'q','.-.':'r','...':'s','-':'t','..-':'u','...-':'v','.--':'w','-..-':'x','-.--':'y','--..':'z',
 '-----':'0','.----':'1','..---':'2','...--':'3','....-':'4','.....':'5','-....':'6','--...':'7','---..':'8','----.':'9'}
def parse(tr):
    words=tr.split('xx'); out=[]; bad=0; n=0
    for w in words:
        for g in w.split('x'):
            if g=='' : bad+=1; continue
            n+=1
            if g in M: out.append(M[g])
            else: out.append('?'); bad+=1
        out.append(' ')
    return ''.join(out), bad, n
def pollux(s,name):
    L='abcdefghi'; best=[]
    for a in itertools.product('.-x',repeat=9):
        mp=dict(zip(L,a))
        tr=''.join(mp[c] for c in s)
        if 'xxx' in tr: continue
        txt,bad,n=parse(tr)
        best.append((bad/max(n,1),bad,n,''.join(a),txt[:80]))
    best.sort()
    print(name,'pollux assignments without xxx:',len(best))
    for b in best[:5]: print('  ',b)
def morbit(s,name):
    pairs=[a+b for a in '.-x' for b in '.-x']
    idx=np.array(['abcdefghi'.index(c) for c in s])
    best=[]
    for perm in itertools.permutations(range(9)):
        if pairs[perm[0]]=='xx': pass
        tr=''.join(pairs[perm[i]] for i in idx)
        if 'xxx' in tr: continue
        txt,bad,n=parse(tr)
        best.append((bad/max(n,1),bad,n,perm,txt[:80]))
    best.sort()
    print(name,'morbit perms without xxx:',len(best))
    for b in best[:5]: print('  ',b)
if __name__=='__main__':
    for s,name in ((FAED,'faed'),(DBBI,'dbbi'),(R60,'R60')):
        pollux(s,name)
    for s,name in ((DBBI,'dbbi'),(R60,'R60'),(FAED,'faed')):
        morbit(s,name)
