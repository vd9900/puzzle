import re, base64, hashlib
from collections import Counter
raw = open('/home/vin/bitcoin_puzzle/research/sources/salphaseion.html','rb').read()
tas = re.findall(rb'<textarea[^>]*>(.*?)</textarea>', raw, re.S)
s = b''.join(tas[0].split(b' ')).decode()
def bits_to_ascii(b, width=8, a='a'):
    bits = ''.join('0' if c==a else '1' for c in b)
    if len(bits)%width: return None
    try: return bytes(int(bits[i:i+width],2) for i in range(0,len(bits),width)).decode('ascii')
    except Exception: return repr(bytes(int(bits[i:i+width],2) for i in range(0,len(bits),width)))
i64 = s.find('U2FsdGVkX1'); print('base64 marker at absolute', i64)
after = s[i64:]
m2 = re.search(r'[ab]{16,}', after)
line1 = after[:m2.start()]; BIN2 = after[m2.start():m2.end()]; tail = after[m2.end():]
print('line1 len', len(line1), 'line1:', line1, ' last char:', repr(line1[-1]))
print('BIN2 len', len(BIN2), '->', repr(bits_to_ascii(BIN2)), ' 7bit:', bits_to_ascii(BIN2,7), ' inverted:', bits_to_ascii(BIN2,8,'b'))
print('char before BIN2:', repr(after[m2.start()-1]), ' char after BIN2:', repr(after[m2.end()]))
# could BIN2 extend left into 'z'? z not in {a,b}. Could it extend right? next char 'Q'. So BIN2 run is forced.
m3 = re.match(r'[A-Za-z0-9+/=]+', tail); greedy = m3.group(0)
print('greedy base64-alphabet run after BIN2 len', len(greedy))
found=[]
for L in range(len(greedy), 0, -1):
    b64 = line1 + greedy[:L]
    if len(b64)%4: continue
    try: d = base64.b64decode(b64, validate=True)
    except Exception: continue
    if d[:8]==b'Salted__' and (len(d)-16)%16==0:
        found.append((L, len(b64), len(d), d[8:16].hex(), greedy[L:]))
for f in found: print('valid Salted__ decode: line2 len %d total %d bytes %d salt %s trailing text %r' % f)
# Alternative: binary 'z'+'enter' hypothesis — what if line1 WITHOUT the trailing z plus line2? (127 chars -> invalid)
b64alt = line1[:-1] + greedy[:64]
print('alt (drop z) len', len(b64alt), 'mod4', len(b64alt)%4)
try:
    d=base64.b64decode(b64alt+'='); print('alt decode head', d[:8])
except Exception as e: print('alt decode fails:', e)
# salts
small = base64.b64decode(line1+greedy[:64]); print('small salt', small[8:16].hex(), 'ct len', len(small)-16, 'ct sha256', hashlib.sha256(small[16:]).hexdigest()[:16])
t1 = tas[1]; lines=[l for l in t1.split(b'\n') if l.strip()]
print('cosmic lines', len(lines), Counter(len(l) for l in lines))
cb = base64.b64decode(b''.join(lines)); print('cosmic bytes', len(cb), 'salt', cb[8:16].hex(), 'ct', len(cb)-16)
for nm,salt in [('small', small[8:16]), ('cosmic', cb[8:16])]:
    print(nm, 'salt printable?', all(32<=c<127 for c in salt), salt)
# z-segments by position
zs=[i for i,c in enumerate(s) if c=='z']; print('z absolute positions', zs, 'gaps', [zs[i+1]-zs[i] for i in range(len(zs)-1)])
print('text after blob:', greedy[64:])
# z-method on faed/dbbi
DBBI=s[:91]; FAED=s[195:765]
def zdec(w, base=10, amap='abcdefghi', zero='o', off=1):
    tr = {c:str(i+off) for i,c in enumerate(amap)}; tr[zero]='0' if off==1 else '9'
    n = int(''.join(tr[c] for c in w), base); h = hex(n)[2:]; h = ('0'+h) if len(h)%2 else h
    return bytes.fromhex(h)
for nm,w in [('FAED',FAED),('DBBI',DBBI)]:
    for lab,kw in [('dec a=1',dict()),('base9 a=0',dict(base=9,off=0)),('dec a=0',dict(base=10,off=0))]:
        try:
            d=zdec(w,**kw); print(nm,lab,'len',len(d),'printable',round(sum(32<=c<127 for c in d)/len(d),2),'head',d[:24])
        except Exception as e: print(nm,lab,'err',e)
# counts
print('o count total', s.count('o'), 'o in FAED', FAED.count('o'), 'o in DBBI', DBBI.count('o'))
# digits of z1/z2 as strings for candidate use
tr={**{c:str(k+1) for k,c in enumerate('abcdefghi')},'o':'0'}
Z1=s[766:829]; Z2=s[830:859]
print('Z1digits', ''.join(tr[c] for c in Z1)); print('Z2digits', ''.join(tr[c] for c in Z2))
print('Z1hex', hex(int(''.join(tr[c] for c in Z1)))[2:]); print('Z2hex', hex(int(''.join(tr[c] for c in Z2)))[2:])
