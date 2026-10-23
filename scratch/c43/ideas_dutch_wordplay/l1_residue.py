# Dutch-L1 audit residue: creator-authored anomalies NOT explained by Dutch L1 interference -> literal passwords (tiny closed set)
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
res=['yourselfself','selfself','theentirenessofyourselfself','entirenessofyourselfself','yourself',
     'giveyourselfyourselfandyourselfwillbegivenyourself','Give yourself yourself and yourself will be given yourself.',
     'archi','archichoice','anstoo','ourfirsthint','shabef','sha256ourfirsthintisyourlastcommand','sha256anstoo']
test_candidates([(s,s) for s in res],'L1-residue literals')
