"""Which nested openssl-enc cascades are length-consistent with the Cosmic blob (ct 1328 B -> outer plaintext 1312..1327 B)
and with the 80-B blobs (plaintext 64..79 B)?  Layer formats: bin (salted binary), a64 (salted, base64, 64-col lines,
trailing NL), aA (salted, base64 one line, no NL), nosalt-bin.  Payloads: natural key/password objects."""
import math, itertools
def enc(L, fmt):
    ct = 16 * (L // 16 + 1)
    if fmt == 'nsbin': return ct
    b = 16 + ct
    if fmt == 'bin': return b
    ch = 4 * math.ceil(b / 3)
    if fmt == 'a64': return ch + math.ceil(ch / 64)
    if fmt == 'aA': return ch
    if fmt == 'aAnl': return ch + 1
PAY = {'rawkey32': 32, 'hex64': 64, 'hex64nl': 65, 'wifU51': 51, 'wifU51nl': 52, 'wifC52': 52, 'wifC52nl': 53,
       'addr34nl': 35, 'hex128(2keys)': 128, 'hex128nl2': 130, 'raw64(2keys/seed)': 64, '2wifC+nl': 106}
def ok_outer(L): return 1312 <= L <= 1327
res = []
for fmt in ('bin', 'a64', 'aA', 'aAnl', 'nsbin'):
    for pn, P in PAY.items():
        L = P
        for k in range(1, 41):
            # k inner layers already applied produce L; outermost Cosmic layer needs plaintext L in range
            L = enc(L, fmt)
            if ok_outer(L): res.append((k + 1, fmt, pn, L))
for r in sorted(res): print('total layers incl. Cosmic=%2d  inner fmt=%-5s payload=%-18s outer-pt=%d' % r)
print('--- 80-byte blobs (pt 64..79): one inner layer?')
for fmt in ('bin', 'a64', 'aA', 'aAnl', 'nsbin'):
    for pn, P in PAY.items():
        L = enc(P, fmt)
        if 64 <= L <= 79: print('  80B blob could hold', fmt, 'layer of', pn, '->', L)
