"""'seven intertwined passwords': braid (round-robin interleave) / concatenate the 7 solved-stage inputs and their sha256
hex digests, forward and reverse order; try as AES password (raw + sha256hex) and as brainwallet vs prize address."""
import sys, hashlib, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from common import test_candidates, sha256hex
from bw_oracle import addrs
P = ['theseedisplanted', 'theflowerblossomsthroughwhatseemstobeaconcretesurface',
     'choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself',
     'causality', 'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple', 'thematrixhasyou',
     'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe']
def braid(ss):
    return ''.join(c for grp in itertools.zip_longest(*ss, fillvalue='') for c in grp)
cands = []
for nm, base in (('plain', P), ('hex', [sha256hex(p) for p in P])):
    for o, seq in (('fwd', base), ('rev', base[::-1])):
        for k in (6, 7):  # 6 = without the SalPhaseIon entry text (stage passwords before the page)
            s = seq[:k] if o == 'fwd' else seq[-k:]
            cands += [(f'braid {nm} {o} k{k}', braid(s)), (f'concat {nm} {o} k{k}', ''.join(s))]
test_candidates(cands, 'braid7')
PRIZE = '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
for d, c in cands:
    for k in (int(sha256hex(c), 16), int(hashlib.sha256(hashlib.sha256(c.encode()).digest()).hexdigest(), 16)):
        if PRIZE in addrs(k).values(): print('!!! ADDRESS', d)
print('addr checks done', len(cands))
