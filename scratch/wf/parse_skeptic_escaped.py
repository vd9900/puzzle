import sys, base64, json
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import try_pw, printable_ratio
n=0; hits=0
for line in open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_parse_skeptic_escaped.txt'):
    line=line.rstrip('\n')
    if not line or line.startswith('#'): continue
    if line.startswith('hex:'): pw=bytes.fromhex(line[4:])
    elif line.startswith('b64:'): pw=base64.b64encode(bytes.fromhex(line[4:]))
    elif line=='empty:': pw=b''
    else: pw=line.encode().decode('unicode_escape').encode()
    n+=1
    for name,d,pt in try_pw(pw):
        if printable_ratio(pt)>0.8 or b'Salted__' in pt or b'U2FsdGVk' in pt:
            hits+=1; print('!!! STRUCTURED HIT', json.dumps({'candidate':line,'blob':name,'kdf':d,'head':pt[:60].decode('latin-1')}))
            open('/home/vin/bitcoin_puzzle/scratch/wf/HITS.log','a').write(json.dumps({'label':'parse_skeptic_escaped','candidate':line,'blob':name,'kdf':d,'plaintext_head':pt[:120].decode('latin-1')})+'\n')
print(f'[parse_skeptic_escaped] candidates={n} structured_hits={hits}')
