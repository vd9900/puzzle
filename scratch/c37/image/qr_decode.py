"""Raw QR (version 4) decoder: format info, unmask, codeword extraction, block de-interleave,
segment parse, padding inspection, and Reed-Solomon syndrome check (GF(256), poly 0x11d)."""
import numpy as np
g = np.load('/home/vin/bitcoin_puzzle/scratch/c37/image/qr_grid.npy')
N = 33
FMT_MASK = 0b101010000010010
def bits_to_int(b): return int(''.join(map(str, b)), 2)
f1 = [g[8, c] for c in (0, 1, 2, 3, 4, 5, 7, 8)] + [g[r, 8] for r in (7, 5, 4, 3, 2, 1, 0)]
f2 = [g[r, 8] for r in range(N - 1, N - 8, -1)] + [g[8, c] for c in range(N - 8, N)]
fi1 = bits_to_int(f1) ^ FMT_MASK; fi2 = bits_to_int(f2) ^ FMT_MASK
print('format copies', format(fi1, '015b'), format(fi2, '015b'))
ecl = {1: 'L', 0: 'M', 3: 'Q', 2: 'H'}[fi1 >> 13]; mask = (fi1 >> 10) & 7
print('ECC', ecl, 'mask', mask)
# BCH check of format
def bch_ok(v):
    gpoly = 0b10100110111; r = v
    for i in range(14, 9, -1):
        if r >> i & 1: r ^= gpoly << (i - 10)
    return r == 0
print('format BCH ok:', bch_ok(fi1), bch_ok(fi2))
MASKS = [lambda i, j: (i + j) % 2 == 0, lambda i, j: i % 2 == 0, lambda i, j: j % 3 == 0, lambda i, j: (i + j) % 3 == 0,
         lambda i, j: (i // 2 + j // 3) % 2 == 0, lambda i, j: (i * j) % 2 + (i * j) % 3 == 0,
         lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0, lambda i, j: ((i + j) % 2 + (i * j) % 3) % 2 == 0]
func = np.zeros((N, N), bool)
func[0:9, 0:9] = True; func[0:9, N - 8:N] = True; func[N - 8:N, 0:9] = True
func[6, :] = True; func[:, 6] = True
func[24:29, 24:29] = True  # alignment center (26,26)
func[N - 8, 8] = True      # dark module
bits = []
col = N - 1; up = True
while col > 0:
    if col == 6: col -= 1
    rows = range(N - 1, -1, -1) if up else range(N)
    for r in rows:
        for c in (col, col - 1):
            if not func[r, c]:
                v = g[r, c] ^ (1 if MASKS[mask](r, c) else 0)
                bits.append(v)
    up = not up; col -= 2
print('data bits', len(bits), '=> codewords', len(bits) // 8, 'remainder', len(bits) % 8)
cw = [bits_to_int(bits[i:i + 8]) for i in range(0, len(bits) // 8 * 8, 8)]
BLOCKS = {'L': [(80, 20)], 'M': [(32, 18)] * 2, 'Q': [(24, 26)] * 2, 'H': [(9, 16)] * 4}[ecl]
nb = len(BLOCKS); dlen = BLOCKS[0][0]; elen = BLOCKS[0][1]
data_blocks = [[] for _ in range(nb)]; ec_blocks = [[] for _ in range(nb)]
k = 0
for i in range(dlen):
    for b in range(nb): data_blocks[b].append(cw[k]); k += 1
for i in range(elen):
    for b in range(nb): ec_blocks[b].append(cw[k]); k += 1
# GF(256)
EXP = [0] * 512; LOG = [0] * 256; x = 1
for i in range(255):
    EXP[i] = x; LOG[x] = i; x <<= 1
    if x & 0x100: x ^= 0x11d
for i in range(255, 512): EXP[i] = EXP[i - 255]
def gmul(a, b): return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]
def syndromes(msg, nsym):
    out = []
    for i in range(nsym):
        s = 0
        for c in msg: s = gmul(s, EXP[i]) ^ c
        out.append(s)
    return out
for b in range(nb):
    syn = syndromes(data_blocks[b] + ec_blocks[b], elen)
    print(f'block {b}: syndromes all zero = {all(s == 0 for s in syn)}; nonzero = {sum(1 for s in syn if s)}')
data = sum(data_blocks, [])
db = ''.join(format(c, '08b') for c in data)
print('data codewords hex:', bytes(data).hex())
# parse segments
p = 0; segs = []
while p + 4 <= len(db):
    mode = db[p:p + 4]; p += 4
    if mode == '0000': print('terminator at bit', p - 4); break
    if mode == '0100':
        n = int(db[p:p + 8], 2); p += 8
        s = bytes(int(db[p + 8 * i:p + 8 * i + 8], 2) for i in range(n)); p += 8 * n
        segs.append(('byte', s)); print('BYTE segment', n, s)
    elif mode == '0010':
        n = int(db[p:p + 9], 2); p += 9
        A = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'; out = ''
        for i in range(n // 2):
            v = int(db[p:p + 11], 2); p += 11; out += A[v // 45] + A[v % 45]
        if n % 2: out += A[int(db[p:p + 6], 2)]; p += 6
        segs.append(('alnum', out)); print('ALNUM segment', n, out)
    elif mode == '0001':
        n = int(db[p:p + 10], 2); p += 10; out = ''
        while n >= 3: out += '%03d' % int(db[p:p + 10], 2); p += 10; n -= 3
        if n == 2: out += '%02d' % int(db[p:p + 7], 2); p += 7
        if n == 1: out += str(int(db[p:p + 4], 2)); p += 4
        segs.append(('num', out)); print('NUM segment', out)
    else:
        print('unknown mode', mode, 'at', p - 4); break
tail_start = (p + 7) // 8
print('bits used', p, 'tail codewords from', tail_start, ':', bytes(data[tail_start:]).hex())
std = [0xEC, 0x11] * 50
print('standard padding?', data[tail_start:] == std[:len(data) - tail_start])
print('remainder bits', bits[len(bits) // 8 * 8:])
