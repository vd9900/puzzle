from common import *
import itertools, re
phr = """we wont
wewont
we won't
hope
if i were you i would hope that we dont meet again
she is going to die and there is nothing you can do to stop it
she is going to die and there is nothing that you can do to stop it
there is nothing you can do to stop it
there is nothing that you can do to stop it
the problem is choice
the problem is
as you adequately put the problem is choice
as you adequately put the problem is
but we already know what youre going to do dont we
the door to your left leads back to the matrix to her and to the end of your species
the door to your right leads to the source and the salvation of zion
to the end of your species
the salvation of zion
salvation
salvationofzion
humph hope it is the quintessential human delusion simultaneously the source of your greatest strength and your greatest weakness
hope it is the quintessential human delusion
the quintessential human delusion
we wont give away the password
wewontgiveawaythepassword
its in front of your eyes but youre not seeing it
very last step is a true give away promised
yellow blue primes
yellowblueprimes
matrixsumlist
lastwordsbeforearchichoice
thispassword
yinyang
ying yang
yingyang
yin yang
cosmic duality
cosmicduality
salphaseion
our first hint is your last command
ourfirsthintisyourlastcommand
sha256 ans too
anstoo
enter
follow the white rabbit
followthewhiterabbit
hashthetext
theseedisplanted
the seed is planted
one for one four for one
ciao bella
ciaobella
ciaobellao
bella ciao
looking forward
lookingforward
jacque fresco
the venus project
thevenusproject
globally supporting my generation
globallysupportingmygeneration
gsmg
GSMG
theory of everything
theoryofeverything
the matrix has you
thematrixhasyou
wake up neo
knock knock neo
there is no spoon
free your mind
half and better half
halfandbetterhalf
better half
betterhalf
half
hundred fourty
hundredfourty
140
1812
21
1812bit
rabbit
RAB
infrared
purple pill
purplepill
the purple pill
first or zero
firstorzero
reinserting the prime basics
the prime basics
primebasics
prime
primes
11 SEP 2001
11SEP2001
11092001
09112001
2001-09-11
september 11 2001
""".strip().splitlines()
def norms(p):
    p=p.strip()
    out={p, p.lower(), p.upper(), re.sub(r'[^a-z0-9]','',p.lower()), re.sub(r'[^A-Za-z0-9]','',p), re.sub(r"[^a-z0-9 ]","",p.lower())}
    return out
cands=[]
for p in phr:
    for v in norms(p):
        cands.append((p,v))
hits=test_candidates(cands,'phrases')
# also sha256 of sha256 (double) and raw digest bytes
n=0
for p,v in cands:
    h=sha256hex(v)
    for pw in (sha256hex(h), bytes.fromhex(h), sha256hex(v).upper()):
        n+=1
        for bn,dg,pt in try_pw(pw):
            if printable_ratio(pt)>0.85: print('!!!',p,bn,dg,pt)
print('extra forms tried',n)
