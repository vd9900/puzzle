import re
from common import *
def a1z26(w): return sum(ord(c)-96 for c in w.lower() if 'a'<=c<='z')
def droot(n, zero='9'):
    r=n%9
    return str(r) if r else zero
def words_of(text): return [w for w in re.findall(r"[A-Za-z']+", text) if re.search('[A-Za-z]',w)]
def root_string(words, mode='dr9'):
    out=[]
    for w in words:
        s=a1z26(w)
        if mode=='dr9': out.append(droot(s,'9'))
        elif mode=='dr0': out.append(str(s%9))          # 0..8
        elif mode=='mod10': out.append(str(s%10))
        elif mode=='sum': out.append(str(s))
        elif mode=='len': out.append(str(len(re.sub('[^a-z]','',w.lower()))))
        elif mode=='lenmod9': out.append(droot(len(re.sub('[^a-z]','',w.lower())),'9'))
    return ''.join(out)
def lcs_substring(a,b):
    # longest common substring via DP (lengths small)
    best=(0,0,0); prev=[0]*(len(b)+1)
    for i in range(1,len(a)+1):
        cur=[0]*(len(b)+1)
        for j in range(1,len(b)+1):
            if a[i-1]==b[j-1]:
                cur[j]=prev[j-1]+1
                if cur[j]>best[0]: best=(cur[j],i-cur[j],j-cur[j])
        prev=cur
    return best
def best_alignment(a,b):
    """max matches of b slid over a (no gaps); returns (matches, len compared, offset)"""
    best=(0,1,0)
    for off in range(-len(b)+1,len(a)):
        m=0;n=0
        for j in range(len(b)):
            i=off+j
            if 0<=i<len(a):
                n+=1; m+= a[i]==b[j]
        if n>=20 and (m/n> best[0]/best[1]): best=(m,n,off)
    return best
