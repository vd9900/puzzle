from common import *
from exp05_prime_seg import segmentations, P
segs=segmentations(DBBI)
cands={}
for t in segs:
    L=len(t)
    toks_zero=['0' if (i+1) in P else letters_to_digits(tok) for i,tok in enumerate(t)]
    cands[f'L{L} tokens->0']=''.join(toks_zero)
    phys=[]
    for i,tok in enumerate(t):
        if (i+1) in P: phys.append('0'*len(tok))
        else: phys.append(letters_to_digits(tok))
    cands[f'L{L} phys->0']=''.join(phys)
    phys2=[]
    for i,tok in enumerate(t):
        if (i+1) in P: phys2.append('0'+('5' if tok=='be' else ''))
        else: phys2.append(letters_to_digits(tok))
    cands[f'L{L} b->0 e stays']=''.join(phys2)
    bits=''.join('1' if tok=='b' else '0' for i,tok in enumerate(t) if (i+1) in P)
    resid=''.join(tok for i,tok in enumerate(t) if (i+1) not in P)
    cands[f'L{L} resid']=letters_to_digits(resid)
    cands[f'L{L} bits+resid']=bits+letters_to_digits(resid)
    cands[f'L{L} resid+bits']=letters_to_digits(resid)+bits
    cands[f'L{L} markerbits']=bits
    # marker bit at prime, residual digits elsewhere
    cands[f'L{L} inline bits']=''.join(('1' if tok=='b' else '0') if (i+1) in P else letters_to_digits(tok) for i,tok in enumerate(t))
    cands[f'L{L} inline bits inv']=''.join(('0' if tok=='b' else '1') if (i+1) in P else letters_to_digits(tok) for i,tok in enumerate(t))
for name,digs in list(cands.items()):
    for rev in (False,True):
        dd=digs[::-1] if rev else digs
        tag=name+(' rev' if rev else '')
        n=int(dd) if dd.strip('0') else 0
        b=n.to_bytes((n.bit_length()+7)//8,'big')
        pr=printable_ratio(b)
        # also base 9 / base 10 variants: a=1..i=9 already; bits+digits
        print(f'{tag:28s} len={len(dd)} pr={pr:.2f} {b[:48]!r}')
        for form,pw in (('raw',dd),('sha',sha256hex(dd))):
            for bn,dg,pt in try_pw(pw):
                if printable_ratio(pt)>0.8: print('   !!! AES hit',tag,form,bn,dg,pt)
        for bn,dg,pt in try_pw(b):
            if printable_ratio(pt)>0.8: print('   !!! AES hit bytes',tag,bn,dg,pt)
