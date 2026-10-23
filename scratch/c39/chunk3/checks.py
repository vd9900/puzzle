"""Quick deterministic checks of concrete claims found in telegram new_chunk3 (Aug-Sep 2026).
Run: python3 -I scratch/c39/chunk3/checks.py   (adds scratch/ to sys.path explicitly)."""
import sys, hashlib
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import tas, SMALL_SALT, SMALL_CT, INNER_SALT, INNER_CT, COSMIC_SALT, COSMIC_CT, FAED, DBBI
from bifid import BIF
from Crypto.Hash import RIPEMD160

# 1. #69910 SalPhaseIon entrance hash
s = 'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'
print('1 sha256 entrance', hashlib.sha256(s.encode()).hexdigest())

# 2. #69275 LSB parity of URL chars
url = 'gsmg.io/theseedisplanted'
par = ''.join(str(ord(c) & 1) for c in url)
print('2 url parity', par, 'claim 111101110011110110010010 ->', par == '111101110011110110010010')

# 3. blob sizes / salts (#69276, #69281, #69323, #68515)
for name, salt, ct in [('small', SMALL_SALT, SMALL_CT), ('inner', INNER_SALT, INNER_CT), ('cosmic', COSMIC_SALT, COSMIC_CT)]:
    print('3', name, 'salt', salt.hex(), 'ct_len', len(ct), 'pt_len_range', (len(ct) - 16, len(ct) - 1))

# 4. Cosmic Duality textarea layout (#68750 line-4 case bias, #68758 28 lines / second half)
lines = [l.strip() for l in tas[1].splitlines() if l.strip()]
print('4 cosmic lines', len(lines))
l4 = lines[3]
print('4 line4', l4, 'upper', sum(c.isupper() for c in l4), 'lower', sum(c.islower() for c in l4), 'digit', sum(c.isdigit() for c in l4))
# baseline: line-wise uppercase counts over all full 64-char lines
ups = sorted(sum(c.isupper() for c in l) for l in lines if len(l) == 64)
print('4 upper counts per 64-char line (sorted)', ups)
print('4 line14 head', lines[13][:16], '| line15 head', lines[14][:16] if len(lines) > 14 else None)

# 5. btcseed Bifid (#69800, #69763)
print('5 BIF head', BIF[:12], 'sha256[:8]', hashlib.sha256(BIF.encode()).hexdigest()[:8], 'len', len(BIF),
      'z count', BIF.count('z'), 'z pos', [i for i, c in enumerate(BIF) if c == 'z'])
even = set(BIF[0::2]); print('5 even-position alphabet', sorted(even))

# 6. #70303 SALPH instruction letter count
instr = 'matrixsumlistlastwordsbeforearchichoicethispasswordshabefourfirsthintisyourlastcommandentershabefanstoo'
print('6 instr len', len(instr))

# 7. #68664 / #69938 pubkey -> hash160
pub = bytes.fromhex('04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559')
h = RIPEMD160.new(hashlib.sha256(pub).digest()).hexdigest()
print('7 hash160', h, h == 'a9553269572a317e39f0f518cb87c1a0ee1dbae4')

# 8. WIF-size deduction for 80-byte ciphertext: plaintext 64..79 bytes under PKCS7
for label, n in [('WIF uncompressed', 51), ('WIF compressed', 52), ('WIF c + newline', 53), ('64-hex', 64), ('64-hex + newline', 65)]:
    print('8', label, n, '-> ct', (n // 16 + 1) * 16)
