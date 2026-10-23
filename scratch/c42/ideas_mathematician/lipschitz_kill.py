# Any overlapping-window sum field (3x3 box sums, Minesweeper counts) read row-major with row length W must satisfy
# |s[i]-s[i+1]| <= 3 within rows and |s[i]-s[i+W]| <= 3 between rows (adjacent windows share 6 of 9 cells).
# If faed were such a field, some lag (1 or W) would show ~100% small differences. Check all lags.
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED
v=[ord(c)-96 for c in FAED]
best=[]
for lag in range(1,300):
    pairs=[(v[i],v[i+lag]) for i in range(len(v)-lag)]
    best.append((sum(abs(a-b)<=3 for a,b in pairs)/len(pairs),lag))
best.sort(reverse=True); print('top lags',best[:5],' i.i.d. expectation ~0.63')
