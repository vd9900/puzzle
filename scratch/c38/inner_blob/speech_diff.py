# usage: python3 -I speech_diff.py <transcript_html> ; prints only the edit list (short fragments), never the transcript
import sys, re, html, difflib
raw = open(sys.argv[1], errors='replace').read()
txt = html.unescape(re.sub(r'<[^>]+>', ' ', raw)).lower()
a = txt.find('your life is the sum of a remainder'); b = txt.find('species', a) + len('species')
seg = txt[a:b]
for k,v in {'23':'twentythree','16':'sixteen','7':'seven'}.items(): seg = re.sub(r'\b%s\b'%k, v, seg)
film = re.sub(r'[^a-z]', '', seg)
puz = open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().strip()
sm = difflib.SequenceMatcher(a=film, b=puz, autojunk=False)
ops = [o for o in sm.get_opcodes()]
eq = sum(i2-i1 for t,i1,i2,j1,j2 in ops if t=='equal')
print('film letters', len(film), 'puzzle letters', len(puz), 'equal letters', eq)
for tag,i1,i2,j1,j2 in ops:
    if tag=='equal': continue
    o=film[i1:i2]; p=puz[j1:j2]
    ctx=puz[max(0,j1-12):j1]
    if len(o)>60: o=o[:25]+f'..[{i2-i1} film letters]..'+o[-15:]
    print(f'{tag:7s} @puz{j1:4d} ctx[..{ctx}] FILM[{o}] -> PUZ[{p}]')
