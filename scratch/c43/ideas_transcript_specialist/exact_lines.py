# Phase 3.2 follows the scene past the Beaufort block (funds to live ~ 'need human beings to survive', better half ~ love,
# chess line ~ 'nothing you can do'): the creator's own last words before the inner blob (= doors slot), exact bytes.
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import test_candidates
raw=open('/home/vin/bitcoin_puzzle/research/artifacts/phase32.txt','rb').read().decode('latin1')
parts=raw.split('\r\n\r\n')
chess=[p for p in parts if p.startswith('Raising')][0]; digits=[p for p in parts if p[:5].isdigit()][0]
pre=parts[1]
c=[]
for name,s in [('chess',chess),('digits',digits),('pre',pre)]:
    for suf in ('','\r\n','\n','\r\n\r\n'):
        c.append((name+repr(suf),s+suf))
        c.append((name+'.lower'+repr(suf),s.lower()+suf))
c.append(('digits+chess',digits+'\r\n\r\n'+chess)); c.append(('digits+chess+crlf',digits+'\r\n\r\n'+chess+'\r\n\r\n'))
c.append(('chess_nopunct',''.join(ch for ch in chess.lower() if ch.isalnum())))
c.append(('lastsentence','A fubcd-king & oracle-queen, thingky mvps, on a sad board but as wide as the first one seen.'))
test_candidates(c,'exact phase3.2 tail lines')
# VIC plaintext in creator-like formats (the scene-continuation 'last words' before the chess line / inner blob)
v='IN CASE YOU MANAGE TO CRACK THIS THE PRIVATE KEYS BELONG TO HALF AND BETTER HALF AND THEY ALSO NEED FUNDS TO LIVE'
c2=[]
for s in (v, v.replace(' ',''), v.lower(), v.lower().replace(' ',''), 'THEY ALSO NEED FUNDS TO LIVE','theyalsoneedfundstolive','they also need funds to live',
          'HALF AND BETTER HALF','halfandbetterhalf','NEED FUNDS TO LIVE','needfundstolive','fundstolive','FUNDSTOLIVE'):
    for suf in ('','\n','\r\n'): c2.append((repr(s[:20])+repr(suf), s+suf))
test_candidates(c2,'vic plaintext formats')
