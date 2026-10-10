from common import *
import sys
sys.path.insert(0,'/home/vin/bitcoin_puzzle')
from tools.gsmg import extract_grid, SOURCES, spiral_coordinates
g=extract_grid(SOURCES/'gsmg-puzzle.png'); colors=g['colors']; M=MATRIX
P=primes_upto(100); pr23=P[:23]
sets={'L84':('00001000110000100110010'),'L83':('00001000110000100110011')}
sp=spiral_coordinates(14)
orders={'spiral':sp,'rowmajor':[(r,c) for r in range(14) for c in range(14)],'colmajor':[(r,c) for c in range(14) for r in range(14)]}
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
cands=[]
for sname,bits in sets.items():
    y=[p for p,b in zip(pr23,bits) if b=='1']; b=[p for p,bb in zip(pr23,bits) if bb=='0']
    for oname,order in orders.items():
        for base in (0,1):
            def cell(i): r,c=order[i-base]; return M[r][c], colors[r][c]
            yb=''.join(str(cell(i)[0]) for i in y); bb=''.join(str(cell(i)[0]) for i in b); allb=''.join(str(cell(i)[0]) for i in pr23)
            yc=[cell(i)[1][0] for i in y]; bc=[cell(i)[1][0] for i in b]
            yn=int(yb,2); bn=int(bb,2)
            print(f'{sname} {oname} base{base}: yellowbits={yb} ({yn}, chr {chr(yn) if 32<=yn<127 else "-"}) bluebits={bb} ({bn}) colors y={"".join(yc)} b={"".join(bc)} all23={allb} ({int(allb,2)})')
            for s in (yb,bb,yb+bb,bb+yb,str(yn),str(bn),f'{yn}{bn}',f'{bn}{yn}',f'{yn} {bn}',allb,str(int(allb,2)),f'yellow{yn}blue{bn}'):
                cands.append((f'{sname} {oname} b{base}',s))
    # digit sums of dbbi / residual / faed at prime positions
    for tn,txt in (('dbbi',letters_to_digits(DBBI)),('res60',letters_to_digits(RES60)),('faed',letters_to_digits(FAED))):
        for base in (0,1):
            sy=sum(int(txt[i-base]) for i in y if i-base<len(txt)); sb=sum(int(txt[i-base]) for i in b if i-base<len(txt))
            print(f'   {sname} {tn} b{base} digit sums yellow={sy} blue={sb}')
            for s in (f'{sy}{sb}',f'{sb}{sy}',str(sy),str(sb),f'{sy} {sb}'): cands.append((f'{sname} {tn} sums b{base}',s))
seen=set(); uniq=[]
for d,s in cands:
    if s and s not in seen: seen.add(s); uniq.append((d,s))
test_candidates(uniq,'prime-position matrix cells')
