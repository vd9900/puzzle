"""Index (printed p.140-143 = PDF 144-147): re-order words by column (x gap clustering) then line y, then
split into entries: a new entry starts at a line whose first char is uppercase and which is not indented
(continuation lines are indented in the scan). OCR caveat: page numerals noisy ('6J-64', '/5')."""
import subprocess, re, json
from xml.etree import ElementTree as ET
PDF='/home/vin/bitcoin_puzzle/data/user_supplied/cosmic_duality/cosmic_duality.pdf'
entries=[]
for pdf in range(144,148):
    out=subprocess.run(['pdftotext','-f',str(pdf),'-l',str(pdf),'-bbox-layout',PDF,'-'],capture_output=True,text=True).stdout
    out=re.sub(r'<!DOCTYPE[^>]*>','',out).replace('xmlns="http://www.w3.org/1999/xhtml"','')
    root=ET.fromstring(out); lines=[]
    for ln in root.iter('line'):
        ws=ln.findall('word'); 
        if not ws: continue
        lines.append((float(ln.get('xMin')),float(ln.get('yMin')),[w.text for w in ws]))
    if pdf==144:
        y0=[y for x,y,w in lines if w==['INDEX']][0]; xi=[x for x,y,w in lines if w==['INDEX']][0]
        lines=[l for l in lines if (l[0]>=xi-20 and l[1]>y0) or l[0]>xi+100]
    xs=sorted(set(round(l[0]) for l in lines))
    # column starts: cluster x positions with gap > 60
    cols=[]; 
    for x in xs:
        if not cols or x-cols[-1][-1]>60: cols.append([x])
        else: cols[-1].append(x)
    def colof(x):
        for i,c in enumerate(cols):
            if c[0]-1<=x<=c[-1]+1: return i
    lines.sort(key=lambda l:(colof(l[0]),l[1]))
    for x,y,w in lines:
        c=cols[colof(x)]; indented = x > c[0]+5
        if not indented and w[0][:1].isupper(): entries.append([pdf,w[:]])
        elif entries: entries[-1][1]+=w
ents=[{'pdf':p,'text':' '.join(w),'head':re.split(r'[,.:;(]',' '.join(w))[0].strip()} for p,w in entries]
ents=[e for e in ents if e['head'] not in ('Numerals in italics indicate an illustration of',)]
json.dump(ents,open('index_entries.json','w'),indent=0)
print(len(ents)); print([e['head'] for e in ents[:30]]); print([e['head'] for e in ents[-10:]])
