"""H5: single-letter zero disguise (each occurrence of letter L may stand for 0), FORWARD and REVERSED
strings, with truncation accounting (zero_dfs.py ran forward only, 2M node cap, no truncation flag).
Oracle: byte-local DFS, all bytes in charset. Self-test: planted texts with 0 -> random letter recovered."""
import sys, time, json, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import Search, CHARSETS, to_bytes, text_to_digits, DIG
from common_dc import DBBI, FAED, R60, R61

def slots_for(s, L):
    return [('ind', (DIG[c], '0')) if c == L else ('fix', DIG[c]) for c in s]

def selftest():
    rnd = random.Random(3)
    for text in ('lastwordsbeforearchichoice', 'reinsertingtheprimebasicsisrequired'):
        D = text_to_digits(text)
        L = rnd.choice('abcdefghi')
        s = ''.join(L if ch == '0' else 'abcdefghi'[int(ch) - 1] for ch in D)
        S = Search(slots_for(s, L), {}, CHARSETS['lower'], max_nodes=5_000_000, max_solutions=100).run()
        got = [to_bytes(v) for v, a, c in S.solutions]
        print('selftest', text, 'L=', L, 'recovered', text.encode() in got, 'nsol', len(got), 'nodes', S.nodes)
        assert text.encode() in got

def main(maxn):
    selftest()
    rows = []
    for name, s0 in (('DBBI', DBBI), ('R60', R60), ('R61', R61), ('FAED', FAED)):
        for rev in (False, True):
            s = s0[::-1] if rev else s0
            for L in 'abcdefghi':
                for cs in ('lower', 'printnl'):
                    t0 = time.time()
                    S = Search(slots_for(s, L), {}, CHARSETS[cs], max_nodes=maxn, max_solutions=20, min_bytes=4).run()
                    sols = [to_bytes(v).decode('latin1') for v, a, c in S.solutions]
                    row = dict(name=name, rev=rev, L=L, cs=cs, nodes=S.nodes, trunc=S.truncated, deepest=S.deepest, nsol=len(sols), sols=sols[:5])
                    rows.append(row)
                    print(('!!! ' if sols else '    ') + json.dumps(row)[:300], f'{time.time()-t0:.1f}s', flush=True)
    json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h5_results.json' if len(sys.argv) < 3 else sys.argv[2], 'w'), indent=0)

if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20_000_000)
