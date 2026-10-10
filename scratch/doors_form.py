import subprocess, time, re, json, hashlib
lines=["The warning","Phase one","The seed is planted when opposites attract","The seed is planted","when opposites attract","opposites attract","Can you dig it","It takes the physical to create the physical","Phase two",
"I.e. greed, racism, insanity, physical and social handicaps","greed racism insanity physical and social handicaps","These are the things that mob the flower","Red rose or black rose no in-between","Red rose or black rose","no in-between","Phase three","Phase 3","The judgement","The judgment","If it were to fall upon you today which flower would you be","which flower would you be","The red rose or the black","red rose or the black","This is the warning",
"red rose","black rose","white rose","the white rose","the red rose","the black rose","yellow rose","blue rose","rose","roses","roses are white","roses are white but often red","Roses are White but often Red.","judgement","warning","Logic","whiterose","WhiteRose","Whiterose",
"yinyang","yin yang","matrixsumlist","lastwordsbeforearchichoice","thispassword","cosmicduality","salphaseion","enter","wewont","we wont","hope","theproblemischoice","the problem is choice","z1on0101","022350","hashthetext","followthewhiterabbit","follow the white rabbit","causality","theseedisplanted",
"Red rose or black rose; no in-between","the flower","mob the flower","physical","the physical","can you dig it?","dig it","in between","inbetween","nointbetween","both","neither","white","red","black","yellow","blue"]
def norm_variants(s):
    v=set()
    v.add(re.sub(r'[^a-z0-9]','',s.lower()))
    v.add(s)
    v.add(s.lower())
    return v
cands=[]
seen=set()
for l in lines:
    for v in norm_variants(l):
        if v and v not in seen: seen.add(v); cands.append(v)
# calibration
cands=['THEFLOWERBLOSSOMSTHROUGHWHATSEEMSTOBEACONCRETESURFACE','the flower blossoms through what seems to be a concrete surface']+cands
print(len(cands),'candidates')
res=[]
for pw in cands:
    r=subprocess.run(['curl','-s','-o','/tmp/f.html','-D','/tmp/f.h','-w','%{http_code} %{size_download}','--max-time','20','-X','POST','--data-urlencode','password='+pw,'https://gsmg.io/phase1verification'],capture_output=True,text=True)
    code,size=r.stdout.split()
    loc=''
    for h in open('/tmp/f.h').read().splitlines():
        if h.lower().startswith('location'): loc=h.strip()
    res.append((pw,code,size,loc))
    if code!='404':
        print('!!! NON-404:', repr(pw), code, size, loc, open('/tmp/f.html','rb').read()[:200])
    time.sleep(0.6)
json.dump(res,open('doors_form_results.json','w'),indent=1)
from collections import Counter
print(Counter((c,s) for _,c,s,_ in res))
