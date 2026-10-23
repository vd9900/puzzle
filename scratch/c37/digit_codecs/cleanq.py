"""Uncontaminated quadgram model from public-domain Carroll text only (chat-derived models contain dbbi/faed verbatim)."""
import re, math, pickle, os
from collections import Counter
P = '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/quad_carroll.pkl'
if os.path.exists(P):
    LOGP, FLOOR = pickle.load(open(P, 'rb'))
else:
    t = re.sub('[^a-z]', '', open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt', errors='ignore').read().lower())
    q = Counter(t[i:i + 4] for i in range(len(t) - 3)); tot = sum(q.values())
    LOGP = {k: math.log10(v / tot) for k, v in q.items()}; FLOOR = math.log10(0.01 / tot)
    pickle.dump((LOGP, FLOOR), open(P, 'wb'))
def score(t):
    t = re.sub('[^a-z]', '', t.lower())
    if len(t) < 4: return FLOOR
    return sum(LOGP.get(t[i:i + 4], FLOOR) for i in range(len(t) - 3)) / (len(t) - 3)
