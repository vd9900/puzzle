"""c43/test1: faed as a per-WORD a1z26 'sum list' of Matrix film dialogue (2003 fan-transcript family).

Derivation: roadmap 'matrix sumlist' + speech opener 'Your life is the SUM of a REMAINDER' -> per-word a1z26 sum,
reduced mod 10 (remainder), with 0 'zeroed out' and written as g (g = {0,7} as established for faed). Secondary
encodings: digital root, word length. If faed (or R60) was produced this way from film dialogue, an exact run of
>=16 consecutive symbols must exist between the target and the transcript's per-word sequence.

Usage: python3 -I word_sumlist_film.py SPEECH_WORDS TRANSCRIPT.txt [TRANSCRIPT.txt ...]
(transcripts are untrusted downloads; only read as text)
"""
import sys, re, random, difflib
# FAED copy verified identical to scratch/common.py FAED (common needs user-site Crypto, unavailable under -I)
FAED = open('/home/vin/bitcoin_puzzle/scratch/c43/ideas_transcript_specialist/faed.txt').read().strip()
assert FAED.startswith('faed')

R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
assert len(FAED) == 570 and len(R60) == 60
THR = 16
K = 5  # seed length: every run >= K is found exactly

# ---------------------------------------------------------------- transcript parsing (dialogue only)
LABEL = re.compile(r"^\s*(\[[^\]]{0,40}\]|[A-Za-z][A-Za-z .#0-9/&'()\-]{0,45}):\s*")
LOC = re.compile(r"^\s*\([^)]*\)\s*$")

def dialogue_lines(path):
    lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
    start = None
    for i, l in enumerate(lines):
        if 'http' in l or l.startswith(('#', '*', '/*')):
            continue
        if LOC.match(l) or (LABEL.match(l) and not l.strip().startswith('[Last')):
            start = i
            break
    out = []
    for l in lines[start:]:
        if l.startswith(('#', '*', '/*')) or 'http' in l or LOC.match(l):
            continue
        l = LABEL.sub('', l, count=1)
        l = re.sub(r"\[[^\]]*\]|\([^)]*\)|\{[^}]*\}", ' ', l)  # stage directions, translations
        if l.strip():
            out.append(l)
    return out

def words(text):
    text = text.lower().replace('’', "'").replace('`', "'")
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text)  # digit tokens dropped (no letters -> no a1z26 sum)

def S(w): return sum(ord(c) - 96 for c in w if 'a' <= c <= 'z')

ENCS = {
    'mod10_0g': lambda w: 'g' if S(w) % 10 in (0, 7) else chr(96 + S(w) % 10),
    'droot':    lambda w: chr(96 + (S(w) - 1) % 9 + 1),
    'len':      lambda w: chr(96 + len(w.replace("'", ''))) if 1 <= len(w.replace("'", '')) <= 9
                          else ('g' if len(w.replace("'", '')) % 10 in (0, 7) else '?'),
}

# ---------------------------------------------------------------- exact maximal common runs
def runs(target, seq, minlen):
    """All maximal exact common runs (i in target, j in seq, L) with L >= minlen (minlen >= K)."""
    idx = {}
    for i in range(len(target) - K + 1):
        idx.setdefault(target[i:i + K], []).append(i)
    seen, out = set(), []
    for j in range(len(seq) - K + 1):
        for i in idx.get(seq[j:j + K], ()):
            a, b = i, j
            while a > 0 and b > 0 and target[a - 1] == seq[b - 1]:
                a -= 1; b -= 1
            key = (a, b)
            if key in seen:
                continue
            seen.add(key)
            L = 0
            while a + L < len(target) and b + L < len(seq) and target[a + L] == seq[b + L]:
                L += 1
            if L >= minlen:
                out.append((a, b, L))
    return out

FAED8 = {FAED[i:i + 8] for i in range(len(FAED) - 7)}
def span_ok(ws):
    """one-letter-word filter + chat self-copy filter (span text containing an 8-gram of faed)."""
    L = len(ws)
    if sum(len(w) == 1 for w in ws) > 0.3 * L or sum(len(w) >= 3 for w in ws) < 0.4 * L:
        return False
    flat = ''.join(ws)
    if any(flat[k:k + 8] in FAED8 for k in range(len(flat) - 7)):
        return False
    return True

def best(target, seq, ws):
    rs = runs(target, seq, K)
    raw = max((r[2] for r in rs), default=0)
    filt = [r for r in rs if span_ok(ws[r[1]:r[1] + r[2]])]
    fmax = max((r[2] for r in filt), default=0)
    hits = [r for r in filt if r[2] >= THR]
    return raw, fmax, hits

# ---------------------------------------------------------------- main
def main():
    speech_path, tpaths = sys.argv[1], sys.argv[2:]
    speech = words(open(speech_path, encoding='utf-8', errors='replace').read())
    texts = {}
    for p in tpaths:
        name = p.rsplit('/', 1)[-1].replace('.txt', '')
        texts[name] = words(' '.join(dialogue_lines(p)))
        ws = texts[name]
        print(f'[parse] {name}: {len(ws)} dialogue words; first: {" ".join(ws[:4])!r} ... last: {" ".join(ws[-3:])!r}')

    # --- sanity: Architect scene of the Reloaded transcript vs the creator's speech (word-for-word apart from edits)
    for name, ws in texts.items():
        sm = difflib.SequenceMatcher(None, speech, ws, autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size >= 3]
        if not blocks or sum(b.size for b in blocks) < 100:
            continue
        lo = min(b.b for b in blocks); hi = max(b.b + b.size for b in blocks)
        scene = ws[lo:hi]
        sm2 = difflib.SequenceMatcher(None, speech, scene, autojunk=False)
        eq = sum(b.size for b in sm2.get_matching_blocks())
        print(f'[sanity] {name}: speech {len(speech)} words; matched {eq} in-order words to transcript words {lo}..{hi} '
              f'({eq/len(speech):.1%} of speech); longest identical block {max(b.size for b in blocks)} words')
        for tag, i1, i2, j1, j2 in sm2.get_opcodes():
            if tag != 'equal':
                print(f'    {tag:7s} speech={" ".join(speech[i1:i2])[:60]!r:64s} transcript={" ".join(scene[j1:j2])[:60]!r}')

    targets = {'faed': FAED, 'faedrev': FAED[::-1], 'head538': FAED[:538], 'R60': R60, 'R60rev': R60[::-1]}
    rng = random.Random(43)
    ctrls = {f'shuf{k}': ''.join(rng.sample(FAED, len(FAED))) for k in range(5)}

    # --- planted controls (mod10_0g): exact 120-word passage, and the same with 6 'creator edits' (substitutions)
    print('\n[planted]')
    plant_ok = True
    enc = ENCS['mod10_0g']
    for name, ws in texts.items():
        seq = ''.join(enc(w) for w in ws)
        j0 = rng.randrange(1000, len(ws) - 1200)
        passage = seq[j0:j0 + 120]
        base = ''.join(rng.sample(FAED, len(FAED)))
        t0 = rng.randrange(50, 570 - 170)
        planted = base[:t0] + passage + base[t0 + 120:]
        raw, fmax, hits = best(planted, seq, ws)
        found = any(a <= t0 and b - a == j0 - t0 and a + L >= t0 + 120 for a, b, L in hits)
        # edited variant: 6 substitutions at spread positions
        p2 = list(passage)
        for q in (15, 33, 52, 70, 88, 104):
            p2[q] = rng.choice([c for c in 'abcdefghi' if c != p2[q]])
        planted2 = base[:t0] + ''.join(p2) + base[t0 + 120:]
        raw2, fmax2, hits2 = best(planted2, seq, ws)
        on_diag = [h for h in hits2 if h[1] - h[0] == j0 - t0]
        ok = found and len(on_diag) >= 1
        plant_ok &= ok
        print(f'  {name}: exact plant at faed-offset {t0} / word {j0}: max run {fmax} found_at_right_offset={found}; '
              f'edited plant: {len(on_diag)} runs>={THR} on the right diagonal (max {fmax2}) -> {"PASS" if ok else "FAIL"}')
        print(f'      aligned words (first 5): {" ".join(ws[j0:j0+5])!r}')

    # --- main scan: 3 texts x 3 encodings = 9 sequences
    print('\n[scan] raw max / filtered max per target; controls shuf0..4')
    all_hits, ctrl_max = [], 0
    for en, fn in ENCS.items():
        for name, ws in texts.items():
            seq = ''.join(fn(w) for w in ws)
            row = []
            for tn, tg in list(targets.items()) + list(ctrls.items()):
                raw, fmax, hits = best(tg, seq, ws)
                row.append(f'{tn}={raw}/{fmax}')
                if tn.startswith('shuf'):
                    ctrl_max = max(ctrl_max, raw)
                else:
                    for a, b, L in hits:
                        all_hits.append((en, name, tn, a, b, L, ' '.join(ws[b:b + 5])))
            print(f'  {en:9s} {name:15s} ' + ' '.join(row))
    print(f'\n[controls] shuffled-faed max raw run over all 9 sequences = {ctrl_max} (must be <= 10): '
          f'{"PASS" if ctrl_max <= 10 else "FAIL"}')
    print(f'[planted] all planted controls: {"PASS" if plant_ok else "FAIL"}')
    print(f'[result] runs >= {THR} on real targets: {len(all_hits)}')
    for h in all_hits:
        print('   HIT', h)

if __name__ == '__main__':
    main()
