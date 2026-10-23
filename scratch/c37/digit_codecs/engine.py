"""Generalized z-method decoding engine (cycle 37, lens digit_codecs).

A "slot program" is a left-to-right list of slots. Each slot is one of
  ('fix', '123')               fixed digit string
  ('ind', ('0','','2'))        independent choice among digit strings (per occurrence)
  ('cls', name)                class-consistent choice: every slot of this class takes the same option,
                               options listed in classes[name]
The decimal integer formed by concatenating the chosen digit strings is converted to big-endian bytes
(z-method: decimal -> hex -> ASCII). Since 10^p == 0 mod 2^p, the low p bits of the integer depend only on
its lowest p decimal digits, so we search from the right and prune whenever a (partially) determined low
byte cannot lie in the target charset.
"""
import string, sys

CHARSETS = {
    'lower': set(range(0x61, 0x7b)),
    'lowsp': set(range(0x61, 0x7b)) | {0x20},
    'print': set(range(0x20, 0x7f)),
    'printnl': set(range(0x20, 0x7f)) | {9, 10, 13},
    'hex': set(b'0123456789abcdef'),
    'HEX': set(b'0123456789ABCDEF'),
    'b64': set((string.ascii_letters + string.digits + '+/=').encode()),
    'b58': set(b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'),
    'alnum': set((string.ascii_letters + string.digits).encode()),
    'digits': set(b'0123456789'),
}


def lowmasks(charset):
    """allowed[m] = set of residues c mod 2^m for c in charset (m=0..8)."""
    return [set(c & ((1 << m) - 1) for c in charset) for m in range(9)]


class Search:
    def __init__(self, slots, classes, charset, max_nodes=5_000_000, max_solutions=50, min_bytes=1):
        self.slots = slots
        self.classes = classes
        self.cs = charset
        self.low = lowmasks(charset)
        self.max_nodes = max_nodes
        self.max_solutions = max_solutions
        self.min_bytes = min_bytes
        self.nodes = 0
        self.truncated = False
        self.solutions = []
        self.deepest = 0
        self.deep_val = None
        # precompute powers of 10
        self.p10 = [10 ** i for i in range(4000)]

    def ok_partial(self, val, p, k):
        """bytes 0..k-1 already verified; bits 0..p-1 determined. verify newly determined full bytes and
        the partial byte. returns new k or -1."""
        while 8 * (k + 1) <= p:
            if ((val >> (8 * k)) & 0xFF) not in self.cs:
                return -1
            k += 1
        rem = p - 8 * k
        if rem > 0:
            if ((val >> (8 * k)) & ((1 << rem) - 1)) not in self.low[rem]:
                return -1
        return k

    def final_ok(self, val, k):
        if val <= 0:
            return False
        nb = (val.bit_length() + 7) // 8
        if nb < self.min_bytes:
            return False
        for j in range(k, nb):
            if ((val >> (8 * j)) & 0xFF) not in self.cs:
                return False
        return True

    def run(self):
        sys.setrecursionlimit(100000)
        self._rec(len(self.slots) - 1, 0, 0, 0, {}, [])
        return self

    def _rec(self, i, val, p, k, assign, choice):
        self.nodes += 1
        if self.nodes > self.max_nodes:
            self.truncated = True
            return
        if len(self.solutions) >= self.max_solutions:
            return
        if k > self.deepest:
            self.deepest = k
            self.deep_val = (val, p)
        if i < 0:
            if self.final_ok(val, k):
                self.solutions.append((val, dict(assign), list(choice)))
            return
        kind, arg = self.slots[i]
        if kind == 'fix':
            opts = (arg,)
            nv = val + int(arg) * self.p10[p] if arg else val
            np_ = p + len(arg)
            nk = self.ok_partial(nv, np_, k)
            if nk >= 0:
                self._rec(i - 1, nv, np_, nk, assign, choice)
            return
        if kind == 'cls':
            if arg in assign:
                opts = (assign[arg],)
                fresh = False
            else:
                opts = self.classes[arg]
                fresh = True
        else:
            opts = arg
            fresh = False
        for o in opts:
            nv = val + int(o) * self.p10[p] if o else val
            np_ = p + len(o)
            nk = self.ok_partial(nv, np_, k)
            if nk < 0:
                continue
            if fresh:
                assign[arg] = o
            if kind == 'ind':
                choice.append((i, o))
            self._rec(i - 1, nv, np_, nk, assign, choice)
            if kind == 'ind':
                choice.pop()
            if fresh:
                del assign[arg]
            if self.nodes > self.max_nodes or len(self.solutions) >= self.max_solutions:
                return


def to_bytes(v):
    return v.to_bytes((v.bit_length() + 7) // 8, 'big')


def text_to_digits(t):
    return str(int.from_bytes(t.encode() if isinstance(t, str) else t, 'big'))


DIG = {c: str(i + 1) for i, c in enumerate('abcdefghi')}
DIG['o'] = '0'
