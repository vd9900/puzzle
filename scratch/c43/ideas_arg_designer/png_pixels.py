import sys, struct, zlib
from collections import Counter
def load(path):
    b=open(path,'rb').read(); i=8; idat=b''
    while i<len(b):
        L=struct.unpack('>I',b[i:i+4])[0]; t=b[i+4:i+8]; d=b[i+8:i+8+L]
        if t==b'IHDR': w,h,bd,ct=struct.unpack('>IIBB',d[:10])
        if t==b'IDAT': idat+=d
        i+=12+L
    raw=zlib.decompress(idat); bpp=4; stride=w*bpp; out=[]; prev=bytearray(stride); p=0
    z=zlib.decompressobj(); 
    filt=Counter()
    for y in range(h):
        f=raw[p]; p+=1; line=bytearray(raw[p:p+stride]); p+=stride; filt[f]+=1
        for x in range(stride):
            a=line[x-bpp] if x>=bpp else 0; bb=prev[x]; c=prev[x-bpp] if x>=bpp else 0
            if f==1: line[x]=(line[x]+a)&255
            elif f==2: line[x]=(line[x]+bb)&255
            elif f==3: line[x]=(line[x]+((a+bb)>>1))&255
            elif f==4:
                pa=abs(bb-c); pb=abs(a-c); pc=abs(a+bb-2*c)
                pr=a if pa<=pb and pa<=pc else (bb if pb<=pc else c); line[x]=(line[x]+pr)&255
        out.append(bytes(line)); prev=line
    return w,h,out,filt,len(idat),len(raw)
path=sys.argv[1]
w,h,rows,filt,li,lr=load(path)
print(path.split('/')[-1],w,h,'filters',dict(filt),'idat',li,'raw',lr,'ratio %.2f'%(li/lr))
px=[tuple(r[x*4:x*4+4]) for r in rows for x in range(w)]
c=Counter(px); print('unique RGBA',len(c),'top',c.most_common(6))
alpha=Counter(p[3] for p in px); print('alpha values',len(alpha),alpha.most_common(5))
# ascii render by alpha/luma
for r in rows:
    s=''
    for x in range(w):
        R,G,B,A=r[x*4:x*4+4]
        s+=' ' if A<64 else ('#' if (R+G+B)/3<100 else ('+' if (R+G+B)/3<180 else '.'))
    print(s)
# LSB planes of fully-transparent pixels' RGB (hidden data in invisible pixels)
inv=[p for p in px if p[3]==0]
print('fully transparent px',len(inv),'distinct RGB under alpha=0',len(set(p[:3] for p in inv)), Counter(p[:3] for p in inv).most_common(4))
# LSB planes (row-major, RGB and RGBA orders) -> bytes, printable ratio
def bits2bytes(bits): return bytes(int(''.join(map(str,bits[i:i+8])),2) for i in range(0,len(bits)-7,8))
for name,seq in (('RGB',[v for p in px for v in p[:3]]),('RGBA',[v for p in px for v in p]),('R',[p[0] for p in px]),('A',[p[3] for p in px])):
    for bit in (0,1):
        by=bits2bytes([(v>>bit)&1 for v in seq])
        pr=sum(32<=c<127 for c in by)/len(by)
        print(name,'bit',bit,'printable %.2f'%pr, repr(by[:40]))
