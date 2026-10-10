from common import *
d=[int(x) for x in letters_to_digits(DBBI)]
f=[int(x) for x in letters_to_digits(FAED)]
def grid(v,ncol):
    return [v[i:i+ncol] for i in range(0,len(v),ncol)]
def sums(v,ncol):
    g=grid(v,ncol)
    rows=[sum(r) for r in g]; cols=[sum(g[r][c] for r in range(len(g))) for c in range(ncol)]
    return rows,cols
A='abcdefghijklmnopqrstuvwxyz'
for name,v,shapes in (('dbbi',d,(7,13)),('faed',f,(15,38,2,3,5,6,10,19,30,57,95,114,190,285))):
    for ncol in shapes:
        rows,cols=sums(v,ncol)
        print(f'{name} {len(v)//ncol}x{ncol}: rowsums={rows}')
        print(f'      colsums={cols}')
        for lab,s in (('rows',rows),('cols',cols)):
            print('      ',lab,'mod26->',''.join(A[x%26] for x in s),' mod9->',''.join(str(x%9) for x in s), ' primes:',[x for x in s if x>1 and all(x%p for p in range(2,int(x**.5)+1))])
# image matrix sums
M=MATRIX
rows=[sum(r) for r in M]; cols=[sum(M[r][c] for r in range(14)) for c in range(14)]
print('image rows',rows,'cols',cols, 'total',sum(rows))
print('image rows mod26',''.join(A[x%26] for x in rows), 'cols', ''.join(A[x%26] for x in cols))
