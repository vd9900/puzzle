from common import *
def square_from(order_src, alphabet='abcdefghiklmnopqrstuvwxyz'):
    seen=[]
    for ch in order_src:
        if ch not in seen and ch in alphabet: seen.append(ch)
    for ch in alphabet:
        if ch not in seen: seen.append(ch)
    return ''.join(seen)
CANON = square_from(DBBI)
def coords(sq):
    return {ch:(i//5,i%5) for i,ch in enumerate(sq)}
def bifid_decrypt(ct, sq, period):
    pos=coords(sq); out=[]
    for start in range(0,len(ct),period):
        blk=ct[start:start+period]; n=len(blk)
        seq=[]
        for ch in blk: r,c=pos[ch]; seq+=[r,c]
        rows=seq[:n]; cols=seq[n:]
        out+= [sq[rows[i]*5+cols[i]] for i in range(n)]
    return ''.join(out)
def bifid_encrypt(pt, sq, period):
    pos=coords(sq); out=[]
    for start in range(0,len(pt),period):
        blk=pt[start:start+period]; n=len(blk)
        rows=[pos[ch][0] for ch in blk]; cols=[pos[ch][1] for ch in blk]
        seq=rows+cols
        out+=[sq[seq[2*i]*5+seq[2*i+1]] for i in range(n)]
    return ''.join(out)
BIF = bifid_decrypt(FAED, CANON, 570)
if __name__=='__main__':
    print('square:', CANON)
    for i in range(0,25,5): print(' ', CANON[i:i+5])
    print(BIF)
    assert bifid_encrypt(BIF,CANON,570)==FAED
    print('even letters:', sorted(Counter(BIF[0::2]).items()))
    print('odd letters:', sorted(Counter(BIF[1::2]).items()))
    print('odd string:', BIF[1::2])
    print('even string:', BIF[0::2])
