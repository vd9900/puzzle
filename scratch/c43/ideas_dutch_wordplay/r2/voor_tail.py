"""Dutch 'voor' = before = in front of (creator used 'in front of' for literal string placement: 'add giveit in front of the
answer'). Z1 'lastwordsbeforearchichoice' sits on the page directly after faed, so 'the last words in front of [this label]'
= faed's closing segment. faed has a data-defined change point: the last 32 letters (after the last e/g) differ in makeup
(p~0.004, cycle 37). Z2 'thispassword' follows. Closed candidate set: that segment in its page-native forms.
Oracle: common.try_pw over 3 blobs x {sha256, md5} EVP; raw / sha256hex (test_candidates) + sha256d forms below."""
import sys, hashlib
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, try_pw, printable_ratio, test_candidates
cut = max(i for i, c in enumerate(FAED) if c in 'eg') + 1
tail = FAED[cut:]; assert tail == 'bccahhbiibibbibdcbahaidhfahiihic' and cut == 538
d1 = tail.translate(str.maketrans('abcdefghi', '123456789'))
d0 = tail.translate(str.maketrans('abcdefghi', '012345678'))
base = [('tail', tail), ('tail spaced', ' '.join(tail)), ('tail a1', d1), ('tail a0', d0),
        ('tail rev', tail[::-1]), ('tail a1 rev', d1[::-1])]
test_candidates(base, 'voor-tail raw+sha256hex')
# 'Hush hush' ~ 'hash hash' (Dutch speakers merge /ʌ/ and /æ/): double-SHA forms of the same set
n = 0; hits = 0
for desc, s in base:
    h1 = hashlib.sha256(s.encode()).digest()
    for form, pw in (('sha256d-hex', hashlib.sha256(h1).hexdigest()), ('sha256(hex)-hex', hashlib.sha256(h1.hex().encode()).hexdigest())):
        n += 1
        for name, dg, pt in try_pw(pw):
            if printable_ratio(pt) > 0.85 or b'Salted__' in pt:
                hits += 1; print('!!! STRUCTURED HIT', desc, form, name, dg, pt[:80])
print(f'[voor-tail sha256d] tried {n} password forms; structured hits: {hits}')
