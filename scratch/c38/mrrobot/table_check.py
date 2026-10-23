# Deterministic check: which resolutions of the Phase 2 table '# X 2 S H 4 Y 0 Q B 15 #' give a valid
# DMS coordinate after the 'worst gear' (reverse) instruction. S=32 (Klingon), Q in {82 (I,W below 8,2), 28}.
import itertools
S='32'
def valid_dms(d,m,s):
    try: d=int(d); m=int(m); s=float(s)
    except ValueError: return False
    return 0<=m<60 and 0<=s<60
res=[]
for B,H,Q in itertools.product(['25','-16'],['42','-42'],['82','28']):
    toks=['#','X','2',S,H,'4','Y','0',Q,B,'15','#']
    fwd=' '.join(toks)
    rev=fwd[::-1]                      # character-level reverse, as the community did
    parts=rev.strip('# ').split()
    # expected shape: d m s s' Y d m s s' X
    try:
        iy=parts.index('Y'); ix=parts.index('X')
    except ValueError: continue
    lat=parts[:iy]; lon=parts[iy+1:ix]
    ok = len(lat)==4 and len(lon)==4 and valid_dms(lat[0],lat[1],lat[2]+'.'+lat[3]) and valid_dms(lon[0],lon[1],lon[2]+'.'+lon[3])
    res.append((B,H,Q,rev,ok))
    print(f'B={B:>3} H={H:>3} Q={Q} reversed={rev!r:40} validDMS={ok}')
v=[r for r in res if r[4]]
print('valid combos:',len(v),'of',len(res))
for B,H,Q,rev,_ in v:
    p=rev.strip('# ').split(); lat=int(p[0])+int(p[1])/60+float(p[2]+'.'+p[3])/3600; lon=int(p[5])+int(p[6])/60+float(p[7]+'.'+p[8])/3600
    print(f'  B={B} H={H} Q={Q}: lat {lat:.5f} N, lon {lon:.5f} E')
