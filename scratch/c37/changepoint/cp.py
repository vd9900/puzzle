"""Change-point analysis of faed's letter distribution: for every split k, the likelihood-ratio
G statistic of 'two different unigram sources' vs 'one source'; significance from 2000 shuffles
(max-over-k statistic, so the look-elsewhere effect is included)."""
import sys, math, random
from collections import Counter
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
def G(s, k):
    a, b, t = Counter(s[:k]), Counter(s[k:]), Counter(s)
    n1, n2, n = k, len(s) - k, len(s)
    g = 0.0
    for ch in t:
        for cnt, m in ((a[ch], n1), (b[ch], n2)):
            if cnt: g += cnt * math.log(cnt * n / (m * t[ch]))
    return 2 * g
def scan(s, lo=30):
    return max((G(s, k), k) for k in range(lo, len(s) - lo))
def report(name, s, N=2000):
    gmax, kbest = scan(s)
    r = random.Random(1); l = list(s); null = []
    for _ in range(N):
        r.shuffle(l); null.append(scan(''.join(l))[0])
    p = sum(x >= gmax for x in null) / N
    print(f'{name}: best split k={kbest} G={gmax:.2f}  max-scan p={p:.4f}  G at k=len/2 ({len(s)//2}) = {G(s, len(s)//2):.2f}')
    a, b = Counter(s[:kbest]), Counter(s[kbest:])
    print('   left ', ' '.join(f'{c}:{a[c]/kbest:.3f}' for c in sorted(set(s))))
    print('   right', ' '.join(f'{c}:{b[c]/(len(s)-kbest):.3f}' for c in sorted(set(s))))
    # top 8 splits
    top = sorted(((G(s, k), k) for k in range(30, len(s) - 30)), reverse=True)[:8]
    print('   top splits', [(k, round(g, 1)) for g, k in top])
report('FAED', FAED)
report('FAED reversed', FAED[::-1], N=200)
