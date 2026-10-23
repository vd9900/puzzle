# usage: python3 -I speech_wdiff.py <transcript_html> ; word-level edit list (short fragments only)
import sys, re, html, difflib, json
raw = open(sys.argv[1], errors='replace').read()
txt = html.unescape(re.sub(r'<[^>]+>', ' ', raw)).lower().replace("'", "").replace("’","")
a = txt.find('your life is the sum of a remainder'); b = txt.find('species', a) + len('species')
seg = txt[a:b]
for k,v in {'23':'twenty three','16':'sixteen','7':'seven'}.items(): seg = re.sub(r'\b%s\b'%k, v, seg)
film = re.findall(r'[a-z]+', seg)
pw = re.findall(r'[a-z]+', open('/home/vin/bitcoin_puzzle/scratch/speech32_words.txt').read().lower().replace("'",""))
assert ''.join(pw) == open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().strip()
sm = difflib.SequenceMatcher(a=film, b=pw, autojunk=False)
out=[]
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='equal': continue
    o=' '.join(film[i1:i2]); p=' '.join(pw[j1:j2])
    if i2-i1>10: o=' '.join(film[i1:i1+4])+f' ..[{i2-i1} film words omitted].. '+' '.join(film[i2-3:i2])
    out.append(dict(tag=tag,puz_word=j1,film=o,puzzle=p))
    print(f'{tag:7s} w{j1:3d} FILM[{o}] -> PUZ[{p}]')
json.dump(out, open('/home/vin/bitcoin_puzzle/scratch/c38/inner_blob/speech_edits.json','w'), indent=1)
