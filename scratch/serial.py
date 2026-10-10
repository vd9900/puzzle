# serial-structure detector: conditional entropy H(next|prev) z-score vs shuffles
import random, math
from collections import Counter
def hcond(s):
    pairs=Counter(zip(s,s[1:])); firsts=Counter(s[:-1]); n=len(s)-1
    return -sum(c/n*math.log2(c/firsts[a]) for (a,b),c in pairs.items())
def hcond_z(s, trials=200, seed=0):
    r=random.Random(seed); l=list(s); vals=[]
    for _ in range(trials):
        r.shuffle(l); vals.append(hcond(l))
    m=sum(vals)/trials; sd=(sum((v-m)**2 for v in vals)/trials)**.5 or 1e-9
    return (hcond(list(s))-m)/sd
if __name__=='__main__':
    import sys; sys.path.insert(0,'.')
    from common import *
    vic='15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
    print('3.2.2 stream hcond z:', round(hcond_z(vic),2))
    f=letters_to_digits(FAED); d=letters_to_digits(DBBI)
    print('faed z:', round(hcond_z(f),2), 'dbbi z:', round(hcond_z(d),2))
    # positive control: columnar-transpose the vic stream (pad to 150) and check detector on right vs wrong key
    import exp02_transposition as T
    pt=vic+'1'
    ct=T.col_transpose_encrypt(pt,'lastwordsbeforearchichoicethispassword'[:15])  # 10 rows x 15
    print('transposed vic z:', round(hcond_z(ct),2))
    print('untransposed with right key z:', round(hcond_z(T.col_transpose_decrypt(ct,'lastwordsbeforearchichoicethispassword'[:15])),2))
    print('untransposed with wrong key z:', round(hcond_z(T.col_transpose_decrypt(ct,'matrixsumlistab')),2))
