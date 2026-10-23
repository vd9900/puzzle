"""Read the 33x33 QR module grid from the puzzle PNG and compare it with canonical encodings
of the same URL (python-qrcode) under every ECC level and mask. Any module difference beyond
the mask choice would be hidden data (non-standard padding etc.)."""
from PIL import Image
import numpy as np, qrcode
im = np.array(Image.open('/home/vin/bitcoin_puzzle/research/sources/gsmg-puzzle.png').convert('L')).astype(int)
q = im[1285:1525, 0:240]
blk = q < 128
ys, xs = np.nonzero(blk)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
N = 33
ps = (x1 - x0 + 1) / N
grid = np.zeros((N, N), int)
for r in range(N):
    for c in range(N):
        cy = int(y0 + (r + 0.5) * ps); cx = int(x0 + (c + 0.5) * ps)
        grid[r, c] = 1 if q[cy, cx] < 128 else 0
print('pixel size', ps, 'bbox', x0, x1, y0, y1)
# purity check: each module uniform?
bad = 0
for r in range(N):
    for c in range(N):
        cell = blk[int(y0 + r * ps) + 1:int(y0 + (r + 1) * ps) - 1, int(x0 + c * ps) + 1:int(x0 + (c + 1) * ps) - 1]
        m = cell.mean()
        if 0.05 < m < 0.95: bad += 1
print('impure modules', bad)
url = 'https://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
best = None
for name, ec in (('L', qrcode.constants.ERROR_CORRECT_L), ('M', qrcode.constants.ERROR_CORRECT_M), ('Q', qrcode.constants.ERROR_CORRECT_Q), ('H', qrcode.constants.ERROR_CORRECT_H)):
    for mask in range(8):
        for data in (url, url.upper(), 'http://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'):
            try:
                qr = qrcode.QRCode(version=4, error_correction=ec, border=0, mask_pattern=mask)
                qr.add_data(data); qr.make(fit=False)
            except Exception as e:
                continue
            m = np.array(qr.get_matrix(), int)
            if m.shape != grid.shape: continue
            d = int((m != grid).sum())
            if best is None or d < best[0]: best = (d, name, mask, data)
print('best canonical match: diff modules =', best)
np.save('/home/vin/bitcoin_puzzle/scratch/c37/image/qr_grid.npy', grid)
for r in grid: print(''.join('#' if v else '.' for v in r))
