"""H1: dbbi prime markers replaced by class-consistent digit strings (z-method reinsertion).
Classes: by token ('b','be'), by image colour (B/Y/W), or one class for all markers.
Options per class: every digit string of length 0..2 (111) plus a1z26-style specials.
Residual letters: a=1..i=9 (id), a=0..i=8 (a0), letter L consistently 0 (Lz), letter L independently 0 (Ld).
Directions: forward and reversed digit string. Oracle: decimal integer -> big-endian bytes all in charset
(base charset printnl; solutions then classified into lower/hex/b58/b64/...). Byte-local DFS (engine.Search).
"""
import sys, time, random, json, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import Search, CHARSETS, to_bytes, text_to_digits, DIG
from common_dc import marked, SEGS

OPTS = tuple([''] + [str(d) for d in range(10)] + ['%02d' % d for d in range(100)] + ['1812', '182', '218', '125', '40', '92', '65', '27'])
OPTS = tuple(dict.fromkeys(OPTS))


def classify(bs):
    return [n for n, cs in CHARSETS.items() if all(c in cs for c in bs)]


def build(seg_len, classing, resid, rev):
    slots = []
    for tok, mk, pos, m in marked(seg_len):
        if mk:
            if classing == 'tok': name = 'tok_' + tok
            elif classing == 'col': name = 'col_' + 'BBBBYBBBYYBBBBYBBYYBWYYBY'[m]
            else: name = 'one'
            slots.append(('cls', name))
        else:
            if resid == 'id':
                slots.append(('fix', DIG[tok]))
            elif resid == 'a0':
                slots.append(('fix', str(int(DIG[tok]) - 1)))
            elif resid.endswith('z'):
                slots.append(('fix', '0' if tok == resid[0] else DIG[tok]))
            elif resid.endswith('d'):
                slots.append(('ind', (DIG[tok], '0')) if tok == resid[0] else ('fix', DIG[tok]))
    if rev:
        slots = [(k, a[::-1] if k == 'fix' else (tuple(x[::-1] for x in a) if k == 'ind' else a)) for k, a in slots[::-1]]
    classes = {n: OPTS for k, n in slots if k == 'cls'}
    return slots, classes


def selftest():
    rnd = random.Random(7)
    ok = 0
    for trial, text in enumerate(['plantedsecretmessagefortesting', 'thepasswordisprimebasics']):
        D = text_to_digits(text)
        slots = []
        for ch in D:
            if rnd.random() < 0.12: slots.append(('cls', 'X'))       # class X maps to '' (deleted)
            if ch == '0': slots.append(('cls', 'Z'))                   # zeros disguised as class Z
            elif ch == '7' and trial == 1: slots.append(('cls', 'S'))  # some digit carried by a class
            else: slots.append(('fix', ch))
        classes = {'X': OPTS, 'Z': OPTS, 'S': OPTS}
        s = Search(slots, classes, CHARSETS['lower'], max_nodes=5_000_000, max_solutions=1000).run()
        found = [to_bytes(v) for v, a, c in s.solutions]
        hit = text.encode() in found
        print(f'selftest {trial}: planted={text!r} solutions={len(found)} recovered={hit} nodes={s.nodes} trunc={s.truncated}')
        ok += hit
    assert ok == 2


def main():
    selftest()
    rows = []
    t0 = time.time()
    resids = ['id', 'a0'] + [L + 'z' for L in 'abcdefghi'] + [L + 'd' for L in 'abcdefghi']
    for seg_len in (83, 84):
        for classing in ('one', 'tok', 'col'):
            for resid in resids:
                for rev in (False, True):
                    slots, classes = build(seg_len, classing, resid, rev)
                    s = Search(slots, classes, CHARSETS['printnl'], max_nodes=30_000_000, max_solutions=200, min_bytes=8).run()
                    sols = []
                    for v, a, c in s.solutions:
                        bs = to_bytes(v)
                        sols.append({'assign': a, 'n_ind_zero': sum(1 for _, o in c if o == '0'), 'bytes': bs.decode('latin1'), 'cs': classify(bs)})
                    row = dict(seg=seg_len, classing=classing, resid=resid, rev=rev, nodes=s.nodes, trunc=s.truncated,
                               deepest=s.deepest, nsol=len(sols), sols=sols[:20])
                    rows.append(row)
                    flag = '!!!' if sols else '   '
                    print(f'{flag} L{seg_len} {classing:3s} {resid:3s} rev={int(rev)} nodes={s.nodes:>9} trunc={int(s.truncated)} deepest={s.deepest:2d} nsol={len(sols)} t={time.time()-t0:.0f}s', flush=True)
                    for so in sols[:5]:
                        print('      ', so['assign'], so['cs'], repr(so['bytes'][:80]))
    json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h1_results.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
