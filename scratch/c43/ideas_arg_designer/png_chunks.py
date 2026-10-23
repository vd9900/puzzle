import sys, struct, zlib
for path in sys.argv[1:]:
    b=open(path,'rb').read(); print('==',path.split('/')[-1],len(b))
    i=8
    while i<len(b):
        L=struct.unpack('>I',b[i:i+4])[0]; t=b[i+4:i+8]; d=b[i+8:i+8+L]
        info=''
        if t in (b'tEXt',b'iTXt',b'zTXt'): info=repr(d[:300])
        if t==b'IHDR': info=struct.unpack('>IIBBBBB',d)
        print('  ',t.decode('latin1'),L,info)
        i+=12+L
        if t==b'IEND': break
    if i<len(b): print('  TRAILING BYTES after IEND:',len(b)-i, repr(b[i:i+200]))
