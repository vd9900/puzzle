"""T3: CyberChef 'From Base' (BigNumber(str, radix), case-insensitive, radix 2..36) on faed/dbbi/res60 (+reversed).
Letters a..i are digit values 10..18, so radix must be >= 19 (radix <= 18 -> BigNumber NaN in CyberChef).
Then 'To Base 16' + 'From Hex' (big-endian bytes). Oracle: printable ratio, 'Salted__' prefix, base64/hex/base58 charset.
Control: planted ASCII payloads round-tripped through ToBase(radix)->FromBase(radix)."""
import sys, string, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import *
RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def tob(n):
    return n.to_bytes((n.bit_length()+7)//8, 'big') if n else b'\0'
def to_base(n, r):
    d = '0123456789abcdefghijklmnopqrstuvwxyz'; s = ''
    while n: s = d[n % r] + s; n //= r
    return s or '0'
def assess(b):
    pr = sum(32 <= x < 127 for x in b)/len(b)
    return pr, b.startswith(b'Salted__'), all(chr(x) in string.hexdigits for x in b), all(chr(x) in string.ascii_letters+string.digits+'+/=' for x in b)
# control
rng = random.Random(5); ok = 0; tot = 0
for r in range(19, 37):
    for pay in [b'Salted__' + bytes(rng.randrange(256) for _ in range(8)), b'the quick brown fox 1GSMG']:
        n = int.from_bytes(pay, 'big'); s = to_base(n, r); tot += 1; ok += tob(int(s, r)) == pay
print('planted round-trip control: %d/%d' % (ok, tot))
best = []
for name, s in [('faed', FAED), ('dbbi', DBBI), ('res60', RES60)]:
    for rev in (False, True):
        t = s[::-1] if rev else s
        for r in range(19, 37):
            b = tob(int(t, r)); pr, salted, hx, b64 = assess(b)
            best.append((pr, name + ('_rev' if rev else ''), r, len(b), salted, hx, b64, b[:16].hex()))
best.sort(reverse=True)
print('candidates:', len(best))
for x in best[:6]: print(' printable=%.2f %s radix=%d len=%d salted=%s hex=%s b64=%s head=%s' % x)
print('any Salted__/hex/b64-charset hit:', any(x[4] or x[5] or x[6] for x in best))
# expected printable ratio for random bytes = 95/256 = 0.371
