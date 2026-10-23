# Viterbi/beam checkerboard decoder that resolves a hidden digit (e.g. 0 disguised as letter X) with a quadgram LM.
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/vic_cipher')
import vicfast as V

QL, QF = V.QL, V.QF
NONLET_PEN = -3.0     # cost for '.', '/' (no LM context)

def beam_decode(u, mapname, tables, X=None, B=400):
    """u: list/array of letter indices 0..8. mapname a1 (digit=idx+1, hidden 0) or a0 (digit=idx, hidden 9).
    X: letter index whose occurrences may be the hidden digit (None = no hidden digit).
    Returns (score_per_char, text)."""
    single, isesc, double = tables
    off = 1 if mapname == 'a1' else 0
    hid = 0 if mapname == 'a1' else 9
    n = len(u)
    opts = []
    for x in u:
        o = [int(x) + off]
        if X is not None and int(x) == X: o.append(hid)
        opts.append(o)
    # states: dict pos -> dict ctx(last3 letters) -> (score, nchars, textlist-tuple)
    layers = [dict() for _ in range(n + 2)]
    layers[0][''] = (0.0, 0, None)
    back = {}
    def push(pos, ctx, sc, nch, parent, ch):
        L = layers[pos]
        cur = L.get(ctx)
        if cur is None or sc > cur[0]:
            L[ctx] = (sc, nch, (parent, ch))
    for pos in range(n):
        L = layers[pos]
        if not L: continue
        if len(L) > B:
            items = sorted(L.items(), key=lambda kv: -kv[1][0])[:B]
            L = dict(items); layers[pos] = L
        for ctx, (sc, nch, bp) in L.items():
            node = (pos, ctx)
            for d in opts[pos]:
                if isesc[d]:
                    if pos + 1 >= n: continue
                    for e in opts[pos + 1]:
                        ch = double[d][e]
                        _emit(push, pos + 2, ctx, sc, nch, node, ch)
                else:
                    ch = single[d]
                    _emit(push, pos + 1, ctx, sc, nch, node, ch)
    # best final state
    final = layers[n] or layers[n - 1]
    ctx, (sc, nch, bp) = max(final.items(), key=lambda kv: kv[1][0])
    # backtrack
    endpos = n if layers[n] else n - 1
    chars = []
    pos = endpos
    while bp is not None:
        (ppos, pctx), ch = bp
        chars.append(ch)
        sc_, nch_, bp = layers[ppos][pctx]
        pos = ppos
    text = ''.join(reversed(chars))
    return sc / max(1, nch), text

def _emit(push, npos, ctx, sc, nch, node, ch):
    if ch is None:
        push(npos, ctx, sc - 6.0, nch + 1, node, '?'); return
    if 'a' <= ch <= 'z':
        g = ctx + ch
        if len(g) == 4:
            sc2 = sc + QL.get(g, QF)
        else:
            sc2 = sc - 1.5          # first chars: unigram-ish constant
        push(npos, g[-3:], sc2, nch + 1, node, ch)
    else:
        push(npos, ctx, sc + NONLET_PEN, nch + 1, node, ch)
