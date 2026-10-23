"""Shared helpers for the cycle-37 'matrixsumlist' lens.
Detectors are structural (printable / lowercase / English quadgram) -- never the AES oracle."""
import sys, random, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, Z1, Z2, Z3, BIN1, MATRIX, primes_upto, letters_to_digits, zmethod_digits
import textmodel

LABEL = 'matrixsumlist'
PRIMES = set(primes_upto(10000))
RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'


def dig(s, a0=False):
    """letters a..i -> ints (a=1..i=9, or a=0..i=8), 'o' -> 0"""
    off = 97 if a0 else 96
    return [0 if c == 'o' else ord(c) - off for c in s]


def int_to_bytes(n):
    if n <= 0:
        return b''
    return n.to_bytes((n.bit_length() + 7) // 8, 'big')


def zdec(digs, base=10):
    """page z-method: digit list (most significant first) -> integer in `base` -> big-endian bytes"""
    n = 0
    for d in digs:
        n = n * base + d
    return int_to_bytes(n)


def pr(b):
    return sum(32 <= c < 127 for c in b) / max(1, len(b))


def lowr(b):
    return sum(97 <= c <= 122 for c in b) / max(1, len(b))


def eng(b):
    t = ''.join(chr(c) for c in b if 97 <= c <= 122 or 65 <= c <= 90)
    if len(t) < 6:
        return -9.0
    return textmodel.score(t)


def longest_printable_run(b):
    best = cur = 0
    for c in b:
        if 32 <= c < 127:
            cur += 1; best = max(best, cur)
        else:
            cur = 0
    return best


def grid_sums(v, w, axis):
    """v: list of ints laid row-major in rows of width w (last row may be partial).
    axis='rows' -> list of row sums; 'cols' -> list of column sums."""
    if axis == 'rows':
        return [sum(v[i:i + w]) for i in range(0, len(v), w)]
    return [sum(v[j::w]) for j in range(w)]


def shuffled(s, seed):
    r = random.Random(seed)
    l = list(s); r.shuffle(l)
    return ''.join(l)


def text_to_zletters(t):
    """inverse of the page z-method: text -> letters a..i/o"""
    n = int.from_bytes(t.encode(), 'big')
    return str(n).translate(str.maketrans('1234567890', 'abcdefghio'))


assert zdec(dig(Z1)) == b'lastwordsbeforearchichoice'
assert text_to_zletters('lastwordsbeforearchichoice') == Z1
