"""Build a printed-page-indexed token model of the Cosmic Duality scan from the PDF's OCR text layer
(pdftotext -bbox-layout, reading order = pdftotext flow/block/line order). Output model.json.
Caveats: Internet Archive OCR (noisy: 'DualUy', 'Oppo$lf€§'); display headings mangled; captions interleave
with body text; two-column pages are ordered by pdftotext flow detection (column-wise mostly)."""
import subprocess, re, json, sys, html
from xml.etree import ElementTree as ET
PDF='/home/vin/bitcoin_puzzle/data/user_supplied/cosmic_duality/cosmic_duality.pdf'
out=subprocess.run(['pdftotext','-bbox-layout',PDF,'-'],capture_output=True,text=True).stdout
out=re.sub(r'<!DOCTYPE[^>]*>','',out)
out=out.replace('xmlns="http://www.w3.org/1999/xhtml"','')
root=ET.fromstring(out)
pages=root.find('body').find('doc').findall('page')
model=[]
for pi,pg in enumerate(pages,1):
    H=float(pg.get('height')); lines=[]; nums=[]
    for fl in pg.findall('flow'):
        for bl in fl.findall('block'):
            for ln in bl.findall('line'):
                ws=[w.text or '' for w in ln.findall('word')]
                ys=[float(w.get('yMin')) for w in ln.findall('word')]
                lines.append(ws)
                for w,y in zip(ws,ys):
                    if re.fullmatch(r'\d{1,3}',w) and (y<0.08*H or y>0.90*H): nums.append(int(w))
    model.append({'pdf':pi,'lines':lines,'edge_nums':nums})
# printed page detection: edge number n with n == pdf-4 confirms offset
conf={}
for m in model:
    off=[m['pdf']-n for n in m['edge_nums'] if 0<m['pdf']-n<10]
    m['offset_obs']=off
for m in model: m['printed']=m['pdf']-4
json.dump(model,open('model.json','w'))
from collections import Counter
c=Counter(o for m in model for o in m['offset_obs'])
print('offset votes',c)
print('pages with observed offset',sum(1 for m in model if m['offset_obs']), 'of',len(model))
print('non-4 obs',[(m['pdf'],m['offset_obs']) for m in model if m['offset_obs'] and 4 not in m['offset_obs']])
print('words total',sum(len(l) for m in model for l in m['lines']))
