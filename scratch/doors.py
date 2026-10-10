import hashlib, re, subprocess, time, json, sys
sys.path.insert(0,'.')
from common import DBBI, FAED, Z1, Z2
sp=open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().strip()
ADDR='1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe'; ADDR2='17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
TITLE='GSMGIO5BTCPUZZLECHALLENGE'
cb='incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive'
texts = [DBBI, FAED, DBBI+FAED, 'matrixsumlist','lastwordsbeforearchichoice','thispassword','enter','anstoo','shabef','sha256',
 'yinyang','yingyang','yin yang','ying yang','YinYang','cosmicduality','CosmicDuality','Cosmic Duality','salphaseion','SalPhaseIon','ourfirsthintisyourlastcommand',
 'shabefourfirsthintisyourlastcommand','shabefanstoo','lastwordsbeforearchichoicethispassword',
 cb, cb.upper(), 'halfandbetterhalf','betterhalf','half','HALFANDBETTERHALF',
 sp, sp.upper(), 'theflowerblossomsthroughwhatseemstobeaconcretesurface','causality','thematrixhasyou','THEMATRIXHASYOU',
 'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple','fubcdora/lethingkymvpszjqwx.',
 TITLE, ADDR, ADDR2, TITLE+ADDR2, TITLE+ADDR+ADDR2, ADDR+ADDR2, 'gsmg.io/theseedisplanted','theseedisplanted','followthewhiterabbit','FOLLOWTHEWHITERABBIT','follow the white rabbit',
 '89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32', hashlib.sha256((TITLE+ADDR).encode()).hexdigest().upper(),
 'HASHTHETEXT','hashthetext','wewont','We wont','theproblemischoice','theproblemis','sheisgoingtodieandthereisnothingyoucandotostopit','sheisgoingtodieandthereisnothingthatyoucandotostopit',
 'thereisnothingyoucandotostopit','hope','Hope','ifiwereyouiwouldhopethatwedontmeetagain','thesourceandthesalvationofzion','salvationofzion','salvation','thesource','source',
 'yellowblueprimes','yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang','wewontgiveawaythepassword','itsinfrontofyoureyesbutyourenotseeingit','verylaststepisatruegiveawaypromised',
 'regularbitcoinprivatekey','lookingforward','LookingForward','jacquefresco','thevenusproject','theoryofeverything','globallysupportingmygeneration','GloballySupportingMyGeneration','Globally supporting my generation',
 '1812bit','1812','21','rabbit','whiterabbit','purplepill','infrared','Infrared','firstorzero','primes','prime','btcseed','11SEP2001','11092001','neo','Neo','trinity','architect','thearchitect','oracle','merovingian','keymaker','zion','choice','door','anotherdoor','thereisanotherdoor','THEREISANOTHERDOOR',
 'roses are white but often red','rosesarewhitebutoftenred','yellowhasanumberandsodoesblue','gobacktothefirstpuzzlepiece','hushhush','Hush hush',
 'GSMG','gsmg','gsmg.io','GSMG Puzzle','puzzle','theseedisplanted.png','matrix','thematrix','thematrixreloaded','mrrobot','elliot','mrrobot','freewill','free will',
 '915','159','201','92','40','252','25','2','FFF2003F48CC','fff2003f48cc','3F48CCFFF200',
 ''.join(str(b) for row in __import__('common').MATRIX for b in row),
]
seen=set(); urls=[]
for t in texts:
    h=hashlib.sha256(t.encode()).hexdigest()
    if h not in seen: seen.add(h); urls.append((t[:50],h))
# also plain paths
paths=['yinyang','yingyang','cosmicduality','salphaseion','matrixsumlist','lastwordsbeforearchichoice','thispassword','enter','anstoo','btcseed','halfandbetterhalf','theproblemischoice','wewont','hope','door','anotherdoor','salvation','source','thesource','zion','phase4','phase5','cosmic','duality','yin','yang','key','privatekey','seed','primes','prime','matrix','sumlist','rabbit','whiterabbit','followthewhiterabbit','hashthetext','theseedisplanted2','choice','archichoice','lastwords','enter.html','phase3.3','phase4verification','salphaseionverification','yinyangverification']
print(len(urls),'hash urls,',len(paths),'paths')
out=[]
def get(u):
    r=subprocess.run(['curl','-s','-o','/tmp/d.html','-w','%{http_code} %{size_download}','--max-time','20',u],capture_output=True,text=True)
    code,size=r.stdout.split()
    body=open('/tmp/d.html','rb').read()
    return code,int(size),body
for label,h in urls:
    code,size,body=get('https://gsmg.io/'+h)
    out.append((label,h,code,size))
    if not (code=='404' and size==9):
        print('!!! INTERESTING', label, h, code, size, body[:300])
    time.sleep(0.7)
for p in paths:
    code,size,body=get('https://gsmg.io/'+p)
    out.append((p,'',code,size))
    if not (code=='404' and size==9):
        print('!!! INTERESTING path', p, code, size, body[:300])
    time.sleep(0.7)
json.dump(out,open('doors_results.json','w'),indent=1)
from collections import Counter
print(Counter((c,s) for _,_,c,s in out))
