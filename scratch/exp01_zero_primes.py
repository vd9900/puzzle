from common import *
P = set(primes_upto(600))
def variants(s):
    d = letters_to_digits(s)
    out = {}
    for base in (0,1):
        for mode in ('replace','delete','keep_only'):
            r=[]
            for i,ch in enumerate(d):
                isp = (i+base) in P
                if mode=='replace': r.append('0' if isp else ch)
                elif mode=='delete':
                    if not isp: r.append(ch)
                else:
                    if isp: r.append(ch)
            out[f'{mode}_base{base}'] = ''.join(r)
    return out

for name,s in (('dbbi',DBBI),('faed',FAED)):
    for k,digs in variants(s).items():
        for rev in (False,True):
            dd = digs[::-1] if rev else digs
            try:
                b = zmethod_digits(dd.lstrip('0') or '0')
            except Exception as e:
                b=b''
            pr = printable_ratio(b)
            tag=f'{name}:{k}{":rev" if rev else ""}'
            if pr>0.6: print('PRINTABLE?', tag, pr, b[:60])
            # as password
            cands=[(tag+':digits', dd), (tag+':bytes-hex', b.hex())]
            for desc,pw in cands:
                for form,p in (('raw',pw),('sha256',sha256hex(pw))):
                    for bn,dg,pt in try_pw(p):
                        if printable_ratio(pt)>0.8: print('!!!',desc,form,bn,dg,pt[:60])
            # raw bytes as password
            for bn,dg,pt in try_pw(b):
                if printable_ratio(pt)>0.8: print('!!! rawbytes',tag,bn,dg,pt[:60])
print('done')
