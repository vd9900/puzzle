from common import *
import itertools

def key_order(key):
    # standard: rank letters alphabetically, ties left-to-right
    idx = sorted(range(len(key)), key=lambda i:(key[i],i))
    order=[0]*len(key)
    for rank,i in enumerate(idx): order[i]=rank
    return order  # order[i] = rank of column i

def col_transpose_decrypt(ct, key):
    """ciphertext was written row-wise into grid, columns read out in key order -> undo"""
    n=len(key); rows=len(ct)//n; assert rows*n==len(ct)
    order=key_order(key)
    cols=[None]*n
    pos=0
    for rank in range(n):
        i=order.index(rank)
        cols[i]=ct[pos:pos+rows]; pos+=rows
    return ''.join(cols[i][r] for r in range(rows) for i in range(n))

def col_transpose_encrypt(pt, key):
    n=len(key); rows=len(pt)//n
    order=key_order(key)
    grid=[pt[r*n:(r+1)*n] for r in range(rows)]
    out=''
    for rank in range(n):
        i=order.index(rank)
        out+=''.join(grid[r][i] for r in range(rows))
    return out

def row_perm_decrypt(ct,key):
    """grid with n=len(key) ROWS; rows permuted by key order"""
    n=len(key); cols=len(ct)//n; assert n*cols==len(ct)
    order=key_order(key)
    rows=[ct[r*cols:(r+1)*cols] for r in range(n)]
    out=[None]*n
    for i in range(n): out[order[i]]=rows[i]
    return ''.join(out)
def row_perm_encrypt(ct,key):
    n=len(key); cols=len(ct)//n
    order=key_order(key)
    rows=[ct[r*cols:(r+1)*cols] for r in range(n)]
    return ''.join(rows[order.index(k)] for k in range(n))

def evaluate(tag, s):
    d=letters_to_digits(s)
    b=zmethod_digits(d)
    pr=printable_ratio(b)
    flag = '  <-- ' if pr>0.7 else ''
    print(f'{tag:60s} pr={pr:.2f} {b[:40]!r}{flag}')
    # also as password
    for desc,pw in ((tag+':letters',s),(tag+':digits',d)):
        for form,p in (('raw',pw),('sha256',sha256hex(pw))):
            for bn,dg,pt in try_pw(p):
                if printable_ratio(pt)>0.8: print('   !!! AES', desc, form, bn, dg, pt[:60])

KEYS_D = {'matrixsumlist':'matrixsumlist'}
KEYS_F = {'lw+tp':'lastwordsbeforearchichoicethispassword','tp+lw':'thispasswordlastwordsbeforearchichoice'}
for kn,key in KEYS_D.items():
    for fn,f in (('coldec',col_transpose_decrypt),('colenc',col_transpose_encrypt),('rowdec',row_perm_decrypt),('rowenc',row_perm_encrypt)):
        s=f(DBBI,key); evaluate(f'dbbi {kn} {fn}', s); evaluate(f'dbbi {kn} {fn} rev', s[::-1])
        # column-wise read of the grid too
for kn,key in KEYS_F.items():
    for fn,f in (('coldec',col_transpose_decrypt),('colenc',col_transpose_encrypt),('rowdec',row_perm_decrypt),('rowenc',row_perm_encrypt)):
        s=f(FAED,key); evaluate(f'faed {kn} {fn}', s); evaluate(f'faed {kn} {fn} rev', s[::-1])
# plain grid column reads (no key)
def colread(s,n):
    rows=len(s)//n
    return ''.join(s[r*n+c] for c in range(n) for r in range(rows))
for n in (7,13): evaluate(f'dbbi colread n={n}', colread(DBBI,n))
for n in (2,3,5,6,10,15,19,30,38,57,95): evaluate(f'faed colread n={n}', colread(FAED,n))
