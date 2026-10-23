# Build the probe sources for the constant-locator test (run locally with system python3).
# Hypothesis (derivation): faed uses only a..i; g (=7) is ~2x overrepresented (107 vs ~57 mean), as if digit 0 AND 7 were both
# written 'g'. If faed (or R60/dbbi) were a stretch of a famous constant's decimal expansion with a..i=1..9 and 0->g, every
# 14-letter window would occur in that constant's digits.
import sys, json, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI, BIN1
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
assert len(FAED) == 570 and len(R60) == 60 and set(FAED) <= set('abcdefghi')
shuf = list(FAED); random.Random(4242).shuffle(shuf); shuf = ''.join(shuf)
shuf2 = list(FAED[::-1]); random.Random(4343).shuffle(shuf2); shuf2 = ''.join(shuf2)
sources = {
    'faed': FAED, 'faed_rev': FAED[::-1], 'R60': R60, 'faed_tail32': FAED[-32:],
    'dbbi_extra': DBBI,                        # cheap extra: the other a..i string
    'CONTROL_faed_shuf': shuf, 'CONTROL_faedrev_shuf': shuf2,   # matched controls: same composition/g-count, order destroyed
}
json.dump({'sources': sources, 'label_bits': BIN1}, open('/home/vin/bitcoin_puzzle/scratch/c42/test2/probes.json', 'w'))
print({k: len(v) for k, v in sources.items()}, 'label', BIN1[:16], len(BIN1))
