"""Deterministic checks of artifacts quoted in telegram new_chunk0 (no guessing loops)."""
import hashlib

P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if a[0] == b[0] and (a[1] + b[1]) % P == 0:
        return None
    if a == b:
        l = 3 * a[0] * a[0] * pow(2 * a[1], -1, P) % P
    else:
        l = (b[1] - a[1]) * pow(b[0] - a[0], -1, P) % P
    x = (l * l - a[0] - b[0]) % P
    return (x, (l * (a[0] - x) - a[1]) % P)


def mul(k, pt=G):
    r = None
    while k:
        if k & 1:
            r = add(r, pt)
        pt = add(pt, pt)
        k >>= 1
    return r


def b58enc(b):
    n = int.from_bytes(b, 'big')
    s = ''
    while n:
        n, r = divmod(n, 58)
        s = B58[r] + s
    return '1' * (len(b) - len(b.lstrip(b'\0'))) + s


def b58dec(s):
    n = 0
    for c in s:
        n = n * 58 + B58.index(c)
    raw = n.to_bytes(38, 'big').lstrip(b'\0')
    return b'\0' * (len(s) - len(s.lstrip('1'))) + raw


def addr(pub):
    h = hashlib.new('ripemd160', hashlib.sha256(pub).digest()).digest()
    v = b'\0' + h
    return b58enc(v + hashlib.sha256(hashlib.sha256(v).digest()).digest()[:4])


def addrs(k):
    x, y = mul(k)
    comp = bytes([2 + (y & 1)]) + x.to_bytes(32, 'big')
    unc = b'\4' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    return addr(comp), addr(unc)


PRIZE = '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
keys = {
    'X #61401': '95e774ea414a6597efa7bec17f10e3533fb5ac7b7e418f4d1ef2521299af4d98',
    'Aquinas half #61339': '0423d9115a1dc756d5d08d2de880ab508bd4745fc97709f4fcb513f2cb8fcc35',
    'Aquinas better half #61339': '48cc46e66bdd36b09ae344552f606a761f9d90681f20dfefe2b43db18b623971',
}
wif = '5J7eRSvSVc8GszCPwgDGHW2LKNqqQaJcucTm3dBqkkNtVa1Ldte'  # 3.14 #62928
raw = b58dec(wif)
assert hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4] == raw[-4:], 'bad WIF checksum'
keys['3.14 WIF #62928'] = raw[1:33].hex()
for name, hx in keys.items():
    c, u = addrs(int(hx, 16))
    print(f'{name}: {hx[:16]}.. comp={c} unc={u} prize_match={PRIZE in (c, u)}')
print('Aquinas claimed: 1JG648yaB7Wp2dpUfcZoRSD4q35oq47vCu / 145ZQ9siLrsXBKf465wjdyQYAP5dRwhRhQ')

for s in ['causality', 'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe',
          'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist']:
    print('sha256', s[:30], hashlib.sha256(s.encode()).hexdigest())

url = 'gsmg.io/theseedisplanted'
bits = ''.join(str(ord(c) & 1) for c in url)
print('URL LSB', bits, hex(int(bits, 2)))

dbbi = 'dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe'
incase = 'INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE'
print('len dbbi', len(dbbi), 'len incase', len(incase))

M = ['00110b0010110y', '11b1001110b011', '1101110b001001', '0110b000011101', '0b1000110y0110',
     '100110y010y011', '100b1100010y00', 'b110F0000010y0', '00011b0111110b', '11b111y0110001',
     '1101000y011011', '11110010b01100', '0b0111010y0110', '01b0110110b011']
rows = [r.count('1') for r in M]
cols = [sum(r[j] == '1' for r in M) for j in range(14)]
print('row sums', rows, 'col sums', cols, 'concat', ''.join(map(str, rows + cols)))
print('JVTRADER p5 candidate 6108766549978798108108736759668')
# CCW spiral from top-left (down first) and CW spiral (right first); positions of coloured cells (1-based)
def spiral(cw):
    t, b, l, r = 0, 13, 0, 13
    out = []
    while t <= b and l <= r:
        if cw:
            out += [(t, j) for j in range(l, r + 1)]; t += 1
            out += [(i, r) for i in range(t, b + 1)]; r -= 1
            if t <= b:
                out += [(b, j) for j in range(r, l - 1, -1)]; b -= 1
            if l <= r:
                out += [(i, l) for i in range(b, t - 1, -1)]; l += 1
        else:
            out += [(i, l) for i in range(t, b + 1)]; l += 1
            out += [(b, j) for j in range(l, r + 1)]; b -= 1
            if l <= r:
                out += [(i, r) for i in range(b, t - 1, -1)]; r -= 1
            if t <= b:
                out += [(t, j) for j in range(r, l - 1, -1)]; t += 1
    return out
for cw in (False, True):
    seq = spiral(cw)
    pos = [(k + 1, M[i][j]) for k, (i, j) in enumerate(seq) if M[i][j] in 'byF']
    print('CW' if cw else 'CCW', [p for p, _ in pos], ''.join(c for _, c in pos))
