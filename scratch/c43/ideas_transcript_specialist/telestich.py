# 'last WORDS' (plural) = sentence-final words of the Architect's door speech, read up to the sentence ending in 'choice'
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import test_candidates
seqs=[['end','doors','zion','species'],['end','doors','zion','species','choice'],['doors','zion','species'],
      ['doors','zion','species','choice'],['zion','species']]
c=[]
for s in seqs:
    for j in ('',' ','_'):
        c.append(('/'.join(s)+repr(j), j.join(s)))
test_candidates(c,'telestich')
