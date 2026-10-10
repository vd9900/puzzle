from common import *
import itertools, time
from Crypto.Cipher import AES
MAT=''.join(str(b) for row in MATRIX for b in row)
rows=[6,10,8,7,6,6,5,4,9,9,7,8,7,9]; cols=[8,10,8,10,8,7,3,6,7,5,9,6,6,8]
R=''.join(map(str,rows)); C=''.join(map(str,cols))
YB=['','9','15','915','159','0','1','01','10','yellow','blue','yellowblue','io','IO','25','2','252','YB','FFF200','3F48CC','fff200','3f48cc','FFF2003F48CC','16773632','4147404','9 15','yellow9blue15','yellow blue']
PR=['','primes','prime','2357','23571113','101','2','3','5','7','11','13','23','89','97','163','24','7575','7357','75757357']
MX=['','matrix','thematrix','14x14','196','101',MAT,'theseedisplanted','gsmg.io/theseedisplanted','matrixsumlist']
SL=['','sumlist',R,C,R+C,C+R,','.join(map(str,rows)),','.join(map(str,cols)),','.join(map(str,rows+cols)),'101','sum','list']
LW=['','wewont','hope','theproblemischoice','sheisgoingtodieandthereisnothingthatyoucandotostopit','sheisgoingtodieandthereisnothingyoucandotostopit','ifiwereyouiwouldhopethatwedontmeetagain','choice','thereisnothingyoucandotostopit','lastwordsbeforearchichoice','thispassword','trinity','toher','asyouadequatelyputtheproblemischoice']
YY=['','yinyang','yingyang','cosmicduality','salphaseion','enter','anstoo']
def fast_hits(pw):
    out=[]
    for name,(salt,ct) in BLOBS.items():
        for dg in ('sha256','md5'):
            k,iv=evp(pw,salt,dg)
            prev=ct[-32:-16]
            last=AES.new(k,AES.MODE_ECB).decrypt(ct[-16:])
            pt=bytes(a^b for a,b in zip(last,prev)); pad=pt[-1]
            if 1<=pad<=16 and pt.endswith(bytes([pad])*pad): out.append((name,dg))
    return out
n=0; t0=time.time(); seen=set(); structured=0
for parts in itertools.product(YB,PR,MX,SL,LW,YY):
    s=''.join(parts)
    if not s or s in seen: continue
    seen.add(s)
    for pw in (sha256hex(s),):
        n+=1
        if fast_hits(pw.encode()):
            for bn,dg,pt in try_pw(pw):
                if printable_ratio(pt)>0.8:
                    structured+=1; print('!!! STRUCTURED', repr(s)[:120], bn, dg, pt[:80], flush=True)
print('tried',n,'in',round(time.time()-t0),'s; structured',structured)
