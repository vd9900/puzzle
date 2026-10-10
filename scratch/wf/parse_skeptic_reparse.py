# Independent re-parse of salphaseion.html from raw bytes. Deliberately does NOT import scratch/common.py.
import re, sys, base64, hashlib
from collections import Counter
raw = open('/home/vin/bitcoin_puzzle/research/sources/salphaseion.html','rb').read()
print('file bytes', len(raw), 'sha256', hashlib.sha256(raw).hexdigest())
print('non-ascii bytes:', [b for b in set(raw) if b>126 or (b<32 and b not in (10,))])
tas = re.findall(rb'<textarea[^>]*>(.*?)</textarea>', raw, re.S)
print('textareas', len(tas), [len(t) for t in tas])
t0 = tas[0]
print('ta0 contains newline?', b'\n' in t0, ' tab?', b'\t' in t0, ' double-space?', b'  ' in t0, ' leading space?', t0[:1]==b' ', ' trailing space?', t0[-1:]==b' ')
toks = t0.split(b' ')
print('tokens', len(toks), 'token length histogram', Counter(len(t) for t in toks))
print('multi-char tokens:', [t for t in toks if len(t)!=1])
s = b''.join(toks).decode()
print('compact length', len(s))
# alphabet per region
print('char counts overall', Counter(s).most_common())
# find boundaries without assuming lengths
# 1) first run of only a/b of length>=16 after a non-ab char
m = re.search(r'(?<=[^ab])[ab]{16,}', s)
print('first long ab-run: start', m.start(), 'end', m.end(), 'len', m.end()-m.start())
# but the preceding char could be a/b (ambiguous start). show context
print('context before run:', s[m.start()-12:m.start()], '| run head', s[m.start():m.start()+16], '| after run:', s[m.end():m.end()+6])
# find the maximal ab-run containing it (ambiguous extension)
ext = re.search(r'[ab]+', s[m.start()-20:]); 
mx = re.search(r'[ab]{16,}', s)
print('maximal ab-run: start', mx.start(), 'end', mx.end(), 'len', mx.end()-mx.start())
def bits_to_ascii(b, width=8, a='a'):
    bits = ''.join('0' if c==a else '1' for c in b)
    if len(bits)%width: return None
    try: return bytes(int(bits[i:i+width],2) for i in range(0,len(bits),width)).decode('ascii')
    except Exception as e: return repr(bytes(int(bits[i:i+width],2) for i in range(0,len(bits),width)))
run = s[mx.start():mx.end()]
print('maximal run as 8-bit:', bits_to_ascii(run), ' as 7-bit:', bits_to_ascii(run,7), ' inverted 8-bit:', bits_to_ascii(run,8,'b'))
# try every sub-run start/end alignment that gives clean ascii in 8-bit
for st in range(mx.start(), mx.start()+9):
    for en in range(mx.end(), mx.end()-9, -1):
        sub = s[st:en]
        if len(sub)%8==0 and len(sub)>=16:
            d = bits_to_ascii(sub)
            if isinstance(d,str) and all(32<=ord(c)<127 for c in d): print('  clean 8-bit decode start',st,'end',en,'->',d)
    for en in range(mx.end(), mx.end()-9, -1):
        sub = s[st:en]
        if len(sub)%7==0 and len(sub)>=14:
            d = bits_to_ascii(sub,7)
            if isinstance(d,str) and all(32<=ord(c)<127 for c in d): print('  clean 7-bit decode start',st,'end',en,'->',d)
DBBI = s[:mx.start()]; BIN1 = run
print('DBBI len', len(DBBI), DBBI)
print('BIN1 len', len(BIN1), '->', bits_to_ascii(BIN1))
rest = s[mx.end():]
zpos = [i for i,c in enumerate(rest) if c=='z']
print('z positions in rest (relative):', zpos, ' absolute:', [p+mx.end() for p in zpos])
FAED = rest[:zpos[0]]
print('FAED len', len(FAED), 'alphabet', sorted(set(FAED)), 'head', FAED[:20], 'tail', FAED[-20:])
segs = [rest[zpos[i]+1:(zpos[i+1] if i+1<len(zpos) else len(rest))] for i in range(len(zpos))]
for i,sg in enumerate(segs): print(f'z-seg{i+1} len {len(sg)} alphabet {"".join(sorted(set(sg)))} :: {sg[:80]}{"..." if len(sg)>80 else ""}')
# z-word decode: a..i -> 1..9, o -> 0, decimal -> bytes
def zdec(w, base=10, amap='abcdefghi', zero='o'):
    tr = {c:str(i+1) for i,c in enumerate(amap)}; tr[zero]='0'
    if any(c not in tr for c in w): return None
    n = int(''.join(tr[c] for c in w), base)
    h = hex(n)[2:]; h = ('0'+h) if len(h)%2 else h
    return bytes.fromhex(h)
for i,sg in enumerate(segs[:2]):
    digits = ''.join({**{c:str(k+1) for k,c in enumerate('abcdefghi')},'o':'0'}[c] for c in sg)
    print(f'z-seg{i+1} digits ({len(digits)}): {digits}')
    print(f'   decimal->bytes: {zdec(sg)}')
    # alternative conventions
    for name,fn in [('a=0..i=8,o=9 dec', lambda w: zdec(w,10,'abcdefghi','o') ),]: pass
    # base-9 style a=0..i=8 ignoring o? (o present -> invalid)
    try:
        tr = {c:str(k) for k,c in enumerate('abcdefghi')}; tr['o']='9'
        n=int(''.join(tr[c] for c in sg)); h=hex(n)[2:]; h=('0'+h) if len(h)%2 else h
        print('   alt a=0..i=8,o=9 ->', bytes.fromhex(h)[:40])
    except Exception as e: print('   alt failed', e)
    try:
        tr = {c:str(k+1) for k,c in enumerate('abcdefghi')}; tr['o']='0'
        n=int(''.join(tr[c] for c in sg),11); h=hex(n)[2:]; h=('0'+h) if len(h)%2 else h
        print('   alt base11 ->', bytes.fromhex(h)[:40])
    except Exception as e: print('   alt failed', e)
# third z-seg: text + base64 + binary + text
sg3 = segs[2]
i64 = sg3.find('U2FsdGVkX1')
print('z-seg3 text before base64:', sg3[:i64], ' (len', i64, ')')
after = sg3[i64:]
m2 = re.search(r'[ab]{16,}', after)
print('base64 line1 len before binary run:', m2.start(), ' line1:', after[:m2.start()])
BIN2 = after[m2.start():m2.end()]
print('BIN2 len', len(BIN2), '->', bits_to_ascii(BIN2), ' 7bit:', bits_to_ascii(BIN2,7))
# ambiguity: chars adjacent to BIN2
print('char before BIN2:', after[m2.start()-1], ' char after:', after[m2.end()])
tail = after[m2.end():]
# base64 alphabet run after binary
m3 = re.match(r'[A-Za-z0-9+/=]+', tail)
print('base64 line2 candidate (greedy):', m3.group(0), 'len', len(m3.group(0)))
# The greedy run swallows trailing 'shabefanstoo' -> determine by decode validity
line1 = after[:m2.start()]
for L in range(len(m3.group(0)), 0, -1):
    b64 = line1 + m3.group(0)[:L]
    if len(b64)%4: continue
    try:
        d = base64.b64decode(b64, validate=True)
    except Exception: continue
    if d[:8]==b'Salted__' and (len(d)-16)%16==0:
        print('valid Salted__ decode with line2 len', L, 'total b64', len(b64), 'bytes', len(d), 'salt', d[8:16].hex(), 'ct', len(d)-16, ' trailing text:', m3.group(0)[L:])
print('line1 len', len(line1), 'line1 last char', line1[-1])
# second textarea
t1 = tas[1]
lines = [l for l in t1.split(b'\n') if l.strip()]
print('cosmic lines', len(lines), 'line lengths', Counter(len(l) for l in lines))
cb = base64.b64decode(b''.join(lines))
print('cosmic bytes', len(cb), 'salt', cb[8:16].hex(), 'ct', len(cb)-16, 'ct%16', (len(cb)-16)%16)
# salts printable?
for nm,salt in [('small', base64.b64decode(line1+m3.group(0)[:64])[8:16]), ('cosmic', cb[8:16])]:
    print(nm, 'salt hex', salt.hex(), 'printable?', all(32<=c<127 for c in salt), salt)
# "z-method" on faed and dbbi (a..i -> 1..9), decimal and base-9 -> bytes
for nm,w in [('FAED',FAED),('DBBI',DBBI)]:
    d10 = zdec(w)
    print(nm, 'z-method decimal bytes len', len(d10), 'printable ratio', sum(32<=c<127 for c in d10)/len(d10), 'head', d10[:32])
    tr = {c:str(k) for k,c in enumerate('abcdefghi')}
    n = int(''.join(tr[c] for c in w), 9); h=hex(n)[2:]; h=('0'+h) if len(h)%2 else h; d9=bytes.fromhex(h)
    print(nm, 'base-9 (a=0) bytes len', len(d9), 'printable ratio', sum(32<=c<127 for c in d9)/len(d9), 'head', d9[:32])
    n = int(''.join(tr[c] for c in w), 10); h=hex(n)[2:]; h=('0'+h) if len(h)%2 else h; d0=bytes.fromhex(h)
    print(nm, 'decimal a=0 bytes len', len(d0), 'printable ratio', sum(32<=c<127 for c in d0)/len(d0), 'head', d0[:32])
print('counts: z in compact', s.count('z'), ' o in compact', s.count('o'))
print('o positions in z-seg1:', [i for i,c in enumerate(segs[0]) if c=='o'], ' in z-seg2:', [i for i,c in enumerate(segs[1]) if c=='o'])
print('TOTAL check: dbbi+bin1+faed =', len(DBBI)+len(BIN1)+len(FAED))
