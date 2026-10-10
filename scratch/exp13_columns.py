from common import *
from serial import hcond_z
import sys
f=letters_to_digits(FAED)
def colread(s,n):  # written in rows of n, read down columns (irregular ok)
    rows=[s[i:i+n] for i in range(0,len(s),n)]
    return ''.join(r[c] for c in range(n) for r in rows if c<len(r))
def colwrite(s,n): # inverse of colread
    L=len(s); full=L//n; extra=L%n
    lens=[full+(1 if c<extra else 0) for c in range(n)]
    cols=[];p=0
    for c in range(n): cols.append(s[p:p+lens[c]]); p+=lens[c]
    return ''.join(cols[c][r] for r in range(full+1) for c in range(n) if r<lens[c])
res=[]
for n in range(2,286):
    for lab,fn in (('colread',colread),('colwrite',colwrite)):
        s=fn(f,n); res.append((hcond_z(s,trials=40),f'n={n} {lab}'))
        s=fn(f[::-1],n); res.append((hcond_z(s,trials=40),f'n={n} {lab} rev'))
res.sort(); print('N',len(res))
for z,t in res[:12]: print(round(z,2),t)
print('tail',[(round(z,2),t) for z,t in res[-3:]])
