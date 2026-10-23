"""Independent English quadgram model built ONLY from scratch/corpora/carroll_public_domain.txt (no puzzle text).
Both scratch/quadgrams.pkl and quadgrams_clean.pkl contain puzzle-derived strings (e.g. 'emck' -5.15 ~ 'tion'-class),
so they inflate scores of the btcseed decode. Use this for any test that scores puzzle-derived letter strings."""
import re, math
from collections import Counter
t = re.sub('[^a-z]', '', open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt').read().lower())
q = Counter(t[i:i+4] for i in range(len(t)-3)); N = sum(q.values())
LOGP = {k: math.log10(v/N) for k, v in q.items()}; FLOOR = math.log10(0.01/N)
