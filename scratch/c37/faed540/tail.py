import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common import FAED
from h4_topdown import td_insert, CHARSETS, to_bytes
from run import famA  # reuses td_choices (runs the selftest on import)
hits = 0
for start in range(520, 545):
    for end in (570,):
        s = FAED[start:end]; digs = ''.join(str(ord(c) - 96) for c in s)
        for csn in ('lower', 'lowsp', 'printnl', 'textish', 'hex'):
            cs = CHARSETS[csn] if csn in CHARSETS else set(b'0123456789abcdef')
            for Z in range(0, 5):
                T = td_insert(digs, Z, cs, max_nodes=2_000_000)
                if T.sols or T.trunc:
                    hits += 1; print(start, csn, Z, 'trunc' if T.trunc else '', [to_bytes(a) for a in T.sols[:3]])
            for M in 'abcdefghi':
                T = famA(s, M, cs)
                if T.sols or T.trunc:
                    hits += 1; print(start, csn, 'M=' + M, [to_bytes(a) for a in T.sols[:3]])
print('tail windows done; hits/truncations:', hits)
