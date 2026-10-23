#!/usr/bin/env python3
"""Sweep row/col sum candidates from the 11x11 grid of 121 prime-position characters
from DBBI + FAED (len 661, pi(661)=121=11x11).
Tests both 1-based (a=1..i=9) and 0-based (a=0..i=8), in raw, comma, space, hex,
and ASCII char representations against small, inner, cosmic blobs and target addresses.
"""
import sys, os, time, re, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
from systematic_solver import run_sweep

def is_prime(n):
    if n < 2: return False
    for d in range(2, int(n**0.5)+1):
        if n % d == 0: return False
    return True

combined = DBBI + FAED
primes_661 = [p for p in range(1, 662) if is_prime(p)]

# 1-based characters and 0-based characters
p_1to9 = [ord(combined[p-1]) - ord('a') + 1 for p in primes_661]
p_0to8 = [x - 1 for x in p_1to9]

cands = []

for name, p_vals in [('1based', p_1to9), ('0based', p_0to8)]:
    grid = [p_vals[i*11 : (i+1)*11] for i in range(11)]
    row_sums = [sum(row) for row in grid]
    col_sums = [sum(grid[r][c] for r in range(11)) for c in range(11)]
    
    # 1. Plain concatenations
    cands.append(''.join(map(str, row_sums)))
    cands.append(''.join(map(str, col_sums)))
    cands.append(''.join(map(str, row_sums)) + ''.join(map(str, col_sums)))
    cands.append(''.join(map(str, col_sums)) + ''.join(map(str, row_sums)))
    
    # 2. Spaces and commas
    cands.append(' '.join(map(str, row_sums)))
    cands.append(' '.join(map(str, col_sums)))
    cands.append(','.join(map(str, row_sums)))
    cands.append(','.join(map(str, col_sums)))
    cands.append(' '.join(map(str, row_sums)) + ' ' + ' '.join(map(str, col_sums)))
    cands.append(','.join(map(str, row_sums)) + ',' + ','.join(map(str, col_sums)))
    
    # 3. As ASCII bytes if in printable range
    try:
        cands.append(bytes(row_sums).decode('latin1'))
    except: pass
    try:
        cands.append(bytes(col_sums).decode('latin1'))
    except: pass
    try:
        cands.append(bytes(row_sums + col_sums).decode('latin1'))
    except: pass
    try:
        cands.append(bytes(col_sums + row_sums).decode('latin1'))
    except: pass
    
    # 4. Modulo 26 as letters A..Z
    mod26_r = ''.join(chr(ord('a') + (x % 26)) for x in row_sums)
    mod26_c = ''.join(chr(ord('a') + (x % 26)) for x in col_sums)
    cands.append(mod26_r)
    cands.append(mod26_c)
    cands.append(mod26_r + mod26_c)
    cands.append(mod26_c + mod26_r)
    
    # 5. Combined with 'matrixsumlist'
    cands.append('matrixsumlist' + ''.join(map(str, row_sums)))
    cands.append('matrixsumlist' + ''.join(map(str, col_sums)))
    cands.append(''.join(map(str, row_sums)) + 'matrixsumlist')
    cands.append(''.join(map(str, col_sums)) + 'matrixsumlist')

# Also the 121 prime characters string itself
p_chars_str = ''.join(combined[p-1] for p in primes_661)
cands.append(p_chars_str)
cands.append(p_chars_str[::-1])

# Transpose of 11x11 grid read out
grid_chars = [p_chars_str[i*11 : (i+1)*11] for i in range(11)]
trans_chars = ''.join(''.join(grid_chars[r][c] for r in range(11)) for c in range(11))
cands.append(trans_chars)
cands.append(trans_chars[::-1])

uniq = list(dict.fromkeys(cands))
print(f'Total 11x11 grid sum candidates: {len(uniq)}')

out_hits = run_sweep(uniq, label='11x11_grid_sums')
print(f'Sweep completed. Structured hits: {len(out_hits)}')
if out_hits:
    for h in out_hits:
        print(f'HIT: {h}')
