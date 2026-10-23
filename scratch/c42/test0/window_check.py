"""Robustness: a message occupying only part of the prime slots dilutes the whole-stream per-letter score.
Statistic = best 40-letter window (per-quadgram mean) on the Viterbi decode. Validated with partial plants
(45-letter sentence at the first prime slots, then pure single-letter filler). Same 30 shuffles per run."""
import random
from prime_a1z26_beam import *

W = 40


def best_window(out):
    q = [LOGP.get(out[i - 3:i + 1], FLOOR) for i in range(3, len(out))]
    if len(q) < W - 3:
        return sum(q) / max(1, len(q)), 0
    best = max(range(len(q) - (W - 3) + 1), key=lambda a: sum(q[a:a + W - 3]))
    return sum(q[best:best + W - 3]) / (W - 3), best


def partial_plant(sentence, start, rng, length=570):
    s = ''; p = start; k = 0
    while len(s) < length:
        if p in PR and k < len(sentence):
            s += tok(sentence[k]); k += 1
        else:
            s += rng.choices(UL, UW)[0]
        p += 1
    return s[:length], sentence[:k]


rng = random.Random(4242)
NC = 30
rows = []
sents = ['thepasswordisthenameofthebookonthetableinfrontofyou', 'lookattheyellowandbluestarsonthecoverofthebookagain',
         'whatyouseekisnotburiedinthegroundbutwritteninthesky']
for k, (sent, st) in enumerate(zip(sents, [1, 188, 189])):
    s, planted = partial_plant(sent[:45], st, rng)
    r = search(s, st); bw, a = best_window(r['out'])
    cs = []
    for c in range(NC):
        l = list(s); rng.shuffle(l); cs.append(best_window(search(''.join(l), st)['out'])[0])
    print(f'partial plant{k} s{st}: whole per={r["per"]:.3f} bestwin={bw:.3f} ctrl max={max(cs):.3f} gap={bw-max(cs):+.3f} '
          f'rec={recovery(r["out"][:len(planted)], planted):.2f} win="{r["out"][a:a+W]}"')
for nm, src in (('fwd', FAED), ('rev', FAED[::-1]), ('nohdr', FAED[4:])):
    for st in (1, 188, 189):
        r = search(src, st); bw, a = best_window(r['out'])
        cs = []
        for c in range(NC):
            l = list(src); rng.shuffle(l); cs.append(best_window(search(''.join(l), st)['out'])[0])
        m = sum(cs) / NC; sd = (sum((x - m) ** 2 for x in cs) / NC) ** .5
        print(f'real {nm} s{st}: bestwin={bw:.3f} ctrl mean={m:.3f} max={max(cs):.3f} diff={bw-max(cs):+.3f} '
              f'z={(bw-m)/sd:+.2f} win="{r["out"][a:a+W]}"')
