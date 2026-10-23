"""H8: faed / dbbi / residual as several z-method numbers concatenated WITHOUT the 'z' delimiters (Z1/Z2 on the same
page are z-delimited). Every substring (identity map a=1..i=9, 5..120 digits) whose decimal value decodes to >=2
lowercase bytes is a candidate piece; a DP finds whether the whole string can be tiled by such pieces and, among
tilings, the one with the best English (Carroll quadgram) score. Control: 20 shuffles of each string (tiling rate,
best score). Self-test: words whose decimal forms contain no '0', concatenated, must be recovered."""
import sys, random, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common_dc import DBBI, FAED, R60, R61
from engine import text_to_digits
import cleanq

LOW = set(range(0x61, 0x7b))


def pieces(digs, minb=2, maxlen=120):
    n = len(digs); out = {}
    for i in range(n):
        for j in range(i + 5, min(n, i + maxlen) + 1):
            v = int(digs[i:j]); b = v.to_bytes((v.bit_length() + 7) // 8, 'big')
            if len(b) >= minb and all(c in LOW for c in b):
                out.setdefault(i, []).append((j, b.decode()))
    return out


def best_tiling(digs, P):
    """DP over positions: maximise (sum of word-internal quad scores + per-char bonus); returns (covered?, text, pieces)."""
    n = len(digs); NEG = -1e18
    best = [NEG] * (n + 1); back = [None] * (n + 1); best[0] = 0.0
    for i in range(n):
        if best[i] == NEG: continue
        for j, w in P.get(i, []):
            sc = best[i] + len(w) * (cleanq.score(w) + 4.4) if len(w) >= 4 else best[i] + len(w) * (-3.0 + 4.4)
            if sc > best[j]: best[j] = sc; back[j] = (i, w)
    if best[n] == NEG: return False, None, None
    ws = []; k = n
    while k: i, w = back[k]; ws.append(w); k = i
    ws.reverse(); return True, ''.join(ws), ws


def coverage(digs, P):
    """max number of digits coverable by non-overlapping pieces (DP)."""
    n = len(digs); f = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        f[i] = f[i + 1]
        for j, w in P.get(i, []): f[i] = max(f[i], (j - i) + f[j])
    return f[0]


def selftest():
    words = [w for w in 'prime basic seed door white rabbit matrix choice yellow blue sum list last words'.split() if '0' not in text_to_digits(w)]
    s = ''.join(text_to_digits(w) for w in words)
    P = pieces(s); ok, txt, ws = best_tiling(s, P)
    print('selftest words', words, 'tiled', ok, ws)
    assert ok and txt == ''.join(words)


def main():
    selftest()
    rnd = random.Random(21); rows = []
    for name, s in (('DBBI', DBBI), ('R60', R60), ('R61', R61), ('FAED', FAED), ('DBBI_rev', DBBI[::-1]), ('FAED_rev', FAED[::-1])):
        digs = ''.join(str(ord(c) - 96) for c in s)
        P = pieces(digs); npieces = sum(len(v) for v in P.values())
        ok, txt, ws = best_tiling(digs, P); cov = coverage(digs, P)
        cc = []
        for _ in range(20 if 'FAED' not in name else 5):
            l = list(digs); rnd.shuffle(l); d2 = ''.join(l); P2 = pieces(d2)
            cc.append((sum(len(v) for v in P2.values()), coverage(d2, P2), best_tiling(d2, P2)[0]))
        row = dict(s=name, ndig=len(digs), n_lower_pieces=npieces, tiled=ok, max_cover_digits=cov, tiling=ws[:20] if ws else None,
                   ctrl_pieces_mean=sum(c[0] for c in cc) / len(cc), ctrl_cover_mean=sum(c[1] for c in cc) / len(cc),
                   ctrl_tiled=sum(c[2] for c in cc))
        rows.append(row); print(json.dumps(row)[:400], flush=True)
    json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h8_undelimited.json', 'w'), indent=0)


if __name__ == '__main__':
    main()
