"""'matrix sum list' as a literal matrix product: dbbi (91 = 7x13 or 13x7) x label bits (13 chars x 8 bits).
Every entry is a sum of products; check outputs as ASCII / letters. Also the 56-letter residual (7x8) variants."""
import sys, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, BIN1
import numpy as np
lab = np.array([[int(b) for b in BIN1[8*k:8*k+8].translate(str.maketrans('ab', '01'))] for k in range(13)])  # 13x8
def show(name, C):
    flat = C.flatten()
    asc = ''.join(chr(x) if 32 <= x < 127 else '.' for x in flat)
    pr = sum(32 <= x < 127 for x in flat) / len(flat)
    lo = sum(97 <= x <= 122 for x in flat) / len(flat)
    m26 = ''.join(chr(97 + (x % 26)) for x in flat)
    m26b = ''.join(chr(96 + (x % 26)) if x % 26 else '_' for x in flat)
    print(f'{name:44} min={flat.min():3} max={flat.max():3} printable={pr:.2f} lower={lo:.2f}\n   ascii: {asc}\n   mod26 a0: {m26}\n   mod26 a1: {m26b}')
for a0 in (False, True):
    d = np.array([ord(c) - 96 - (1 if a0 else 0) for c in DBBI])
    for shape in ('7x13 rowmajor', '13x7 rowmajor->T', '7x13 colmajor'):
        if shape == '7x13 rowmajor': A = d.reshape(7, 13)
        elif shape == '13x7 rowmajor->T': A = d.reshape(13, 7).T
        else: A = d.reshape(13, 7, order='C').T.copy() if False else d.reshape(7, 13, order='F')
        for lbits, L in (('label', lab), ('label-inverted', 1 - lab), ('label-bitreversed', lab[:, ::-1])):
            C = A @ L
            show(f'{"a0" if a0 else "a1"} dbbi[{shape}] x {lbits}', C)
