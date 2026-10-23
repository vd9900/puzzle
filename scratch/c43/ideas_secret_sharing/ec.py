"""Minimal secp256k1 affine arithmetic + prize target (pure python, verified against prize address)."""
import hashlib
P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
LAM = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
PUB_UNC = ('04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559')
TGT = (int(PUB_UNC[2:66], 16), int(PUB_UNC[66:], 16))
def add(a, b):
    if a is None: return b
    if b is None: return a
    if a[0] == b[0]:
        if (a[1] + b[1]) % P == 0: return None
        l = 3 * a[0] * a[0] * pow(2 * a[1], -1, P) % P
    else:
        l = (b[1] - a[1]) * pow(b[0] - a[0], -1, P) % P
    x = (l * l - a[0] - b[0]) % P
    return (x, (l * (a[0] - x) - a[1]) % P)
def neg(a): return None if a is None else (a[0], (-a[1]) % P)
def mul(k, pt=G):
    k %= N; r = None
    while k:
        if k & 1: r = add(r, pt)
        pt = add(pt, pt); k >>= 1
    return r
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def addr(pt, comp):
    x, y = pt
    enc = (bytes([2 + (y & 1)]) + x.to_bytes(32, 'big')) if comp else (b'\4' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big'))
    pl = b'\0' + hashlib.new('ripemd160', hashlib.sha256(enc).digest()).digest()
    d = pl + hashlib.sha256(hashlib.sha256(pl).digest()).digest()[:4]
    n = int.from_bytes(d, 'big'); s = ''
    while n: n, r = divmod(n, 58); s = B58[r] + s
    return '1' * (len(d) - len(d.lstrip(b'\0'))) + s
assert (TGT[1]**2 - TGT[0]**3 - 7) % P == 0
assert addr(TGT, False) == '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
assert addr(mul(1), True) == '1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH'
