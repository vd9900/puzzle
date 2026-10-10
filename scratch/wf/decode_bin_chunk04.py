import re
raw = open('/home/vin/bitcoin_puzzle/scratch/chat_chunks/chunk04.txt', encoding='utf-8', errors='replace').read()
bins = [l.strip() for l in raw.split('\n') if re.fullmatch(r'[01]{200,}', l.strip())]
bits = ''.join(bins); print('total bits', len(bits), 'bytes', len(bits)/8)
txt = bytes(int(bits[i:i+8],2) for i in range(0,len(bits)-7,8)).decode('latin-1')
print('AS-IS:'); print(txt); print()
rev = txt[::-1]; print('REVERSED:'); print(rev); print()
def caesar(s,k): return ''.join(chr((ord(c)-97-k)%26+97) if 'a'<=c<='z' else c for c in s)
for run in re.findall(r'[a-z]{6,}', txt):
    print('RUN', run[:60], '-> shift3:', caesar(run,3), '| rev shift3:', caesar(run[::-1],3))
inner = re.findall(r'[01]{40,}', txt)
for b in inner:
    print('INNER bits', len(b))
    for lab, bb in (('as-is', b), ('reversed', b[::-1])):
        s = bytes(int(bb[i:i+8],2) for i in range(0,len(bb)-7,8)).decode('latin-1')
        print(' ', lab, repr(s[:200]))
        s7 = ''.join(chr(int(bb[i:i+7],2)) for i in range(0,len(bb)-6,7))
        print(' ', lab, '7bit', repr(s7[:120]))
