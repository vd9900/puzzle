# Yin/yang = parity (Lo Shu: odd=yang/white, even=yin/black). Letters a..i -> digit parity -> bit stream.
# Readings: 8-bit/7-bit ASCII (MSB/LSB first, all offsets), 6-bit groups -> base64 alphabet (I Ching hexagram = 6 lines);
# 570 = 95*6 exactly. Oracle: printable fraction of decoded bytes vs letter-shuffled controls; base64 'U2FsdGVk' prefix.
import sys, random, base64, string
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
B64=string.ascii_uppercase+string.ascii_lowercase+string.digits+'+/'
def bits(s,pol): return [((ord(c)-96)%2)^pol for c in s]
def pr(b): return sum(32<=x<127 or x in (9,10,13) for x in b)/max(1,len(b))
def readings(s):
    out=[]
    for pol in (0,1):
        for rev in (False,True):
            bb=bits(s[::-1] if rev else s,pol)
            for w in (7,8):
                for off in range(w):
                    for lsb in (False,True):
                        ch=[bb[i:i+w] for i in range(off,len(bb)-w+1,w)]
                        vals=[int(''.join(map(str,(c[::-1] if lsb else c))),2) for c in ch]
                        out.append((('pol',pol,'rev',rev,'w',w,'off',off,'lsb',lsb),bytes(vals)))
            for off in range(6):
                ch=[bb[i:i+6] for i in range(off,len(bb)-5,6)]
                txt=''.join(B64[int(''.join(map(str,c)),2)] for c in ch)
                t=txt[:len(txt)//4*4]
                try: raw=base64.b64decode(t)
                except Exception: raw=b''
                out.append((('pol',pol,'rev',rev,'b64off',off,txt[:16]),raw))
    return out
def best(s):
    r=readings(s); return max(r,key=lambda x:pr(x[1]))
rnd=random.Random(5)
for name,s in [('dbbi',DBBI),('R60',R60),('faed',FAED)]:
    b=best(s)
    ctrl=[]
    for _ in range(30):
        l=list(s); rnd.shuffle(l); ctrl.append(pr(best(''.join(l))[1]))
    ctrl.sort()
    print(f'{name}: best printable {pr(b[1]):.3f} {b[0]} {b[1][:40]!r}  ctrl median {ctrl[15]:.3f} max {ctrl[-1]:.3f}')
    for lab,raw in readings(s):
        if b'Salted' in raw: print('  SALTED HIT',lab)
print('faed odd fraction', sum((ord(c)-96)%2 for c in FAED)/len(FAED), 'dbbi', sum((ord(c)-96)%2 for c in DBBI)/len(DBBI))
