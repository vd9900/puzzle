# count embossed frame ridges on each side of the inset picture (deterministic profile peak count)
import sys
from PIL import Image
import numpy as np
im=np.asarray(Image.open(sys.argv[1]).convert('L')).astype(float)
def ridges(prof, k=9, thr=8):
    base=np.convolve(prof,np.ones(k)/k,'same'); d=prof-base
    pk=[i for i in range(2,len(d)-2) if d[i]==max(d[i-2:i+3]) and d[i]>thr]
    return pk
bands={'top (cols 220-340, rows 135-226)':im[135:226,220:340].mean(1),
       'bottom (cols 220-340, rows 546-640)':im[546:640,220:340].mean(1),
       'left (rows 300-460, cols 30-118)':im[300:460,30:118].mean(0),
       'right (rows 300-460, cols 448-545)':im[300:460,448:545].mean(0)}
for name,p in bands.items():
    for thr in (5,8,12):
        print(name,'thr',thr,'n=',len(ridges(p,thr=thr)),ridges(p,thr=thr))
