import re, hashlib, glob, sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED

RAW = '/home/vin/bitcoin_puzzle/scratch/chat_chunks/chunk04.txt'
raw = open(RAW, encoding='utf-8', errors='replace').read()

# ---- 1. binary dump posted 11.01.2024 ----
bins = [l.strip() for l in raw.split('\n') if re.fullmatch(r'[01]{200,}', l.strip())]
print('binary lines:', [len(b) for b in bins])
def dec(bits):
    bits = bits[:len(bits)//8*8]
    return bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8))
decoded = []
for b in bins:
    d = dec(b)
    decoded.append(d)
    print('AS-IS head:', d[:120])
    print('REVERSED head:', d[::-1][:120])
full = b''.join(decoded)
rev = full[::-1]
print('FULL REVERSED (latin1):')
print(rev.decode('latin-1'))

# ---- 2. DaniyarK pair map on dbbi ----
pm = {'db':'a','bi':'b','bf':'c','bh':'d','cc':'e','be':'f','gb':'g','ih':'h','ab':'i','eb':'j','ei':'k','hb':'l','eg':'m','ge':'n','bb':'o','hh':'p','fb':'q','fd':'r','ef':'s','fc':'t','cg':'u','cb':'v','ed':'w','ci':'x','fg':'y','ig':'z','ee':' '}
def pairmap(s):
    out=''
    for i in range(0,len(s)-1,2):
        out += pm.get(s[i:i+2], '?')
    return out
pm0 = pairmap(DBBI); pm1 = pairmap(DBBI[1:])
print('pairmap0:', pm0); print('pairmap1:', pm1)
pairs = [DBBI[i:i+2] for i in range(0,90,2)]
print('distinct pairs even-split:', len(set(pairs)))

# ---- 3. digit views ----
def a2d(s): return ''.join(str(ord(c)-96) if 'a'<=c<='i' else ('0' if c=='o' else c) for c in s)
dd = a2d(DBBI); fd = a2d(FAED)
groups7 = [dd[i:i+7] for i in range(0,91,7)]
rows38 = [fd[i:i+38] for i in range(0,570,38)]
sums7 = [sum(map(int,g)) for g in groups7]
sums38 = [sum(map(int,r)) for r in rows38]
print('groups7', groups7, sums7)
print('rows38 sums', sums38)

# ---- 4. verbatim strings ----
C = []
def add(*xs):
    for x in xs:
        x = x.strip()
        if x: C.append(x)

# decoded binary dump words
try:
    txt = rev.decode('latin-1')
    add(txt)
    for tok in re.findall(r'[A-Za-z0-9_?]{3,}', txt):
        add(tok, tok.replace('_',' '), tok.replace('_','').lower())
    # Caesar shifts of lowercase runs
    for run in re.findall(r'[a-z]{20,}', txt):
        for k in range(26):
            add(''.join(chr((ord(c)-97-k)%26+97) for c in run))
except Exception as e:
    print('decode err', e)

add(pm0, pm1, pm0.replace('?',''), pm1.replace('?',''), pm0.replace(' ',''), pm1.replace(' ',''))
add(dd, fd, ''.join(groups7), ''.join(sorted(groups7, key=lambda g: sum(map(int,g)))), ''.join(map(str,sums7)), ''.join(map(str,sorted(sums7))),
    ' '.join(groups7), ''.join(sorted(rows38, key=lambda r: sum(map(int,r)))), ''.join(map(str,sums38)), ''.join(map(str,sorted(sums38))))
for g in groups7: add(g)
for r in rows38: add(r)

add(
# hint-derived phrases
'yellowblueprimes','yellow blue primes','yellowblueprime','yellowblueprimesmatrixsumlist','yellow blue primes matrix sumlist',
'yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangwewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingitverylaststepisatruegiveawaypromised',
'yellow blue primes matrix sumlist last words before archichoice yinyang we wont give away thepassword its in front of your eyes but youre not seeing it very last step is a true giveaway promised',
'yinyangwewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingitverylaststepisatruegiveawaypromised',
'wewontgiveawaythepassword','itsinfrontofyoureyes','itsinfrontofyoureyesbutyourenotseeingit','verylaststepisatruegiveawaypromised','verylaststepisatruegiveaway','atruegiveaway','giveaway','promised',
'yinyang','yin yang','yingyang','ying yang','yin-yang','YinYang','yinyangfromnothingtosomething','from nothing to something from something to nothing',
'thispassword','thepassword','this password','the password','thispasswordthepassword','thispassword||thepassword','thispasswfrd',
'lastwordsbeforearchichoice','lastwordsbeforearch','last words before archichoice','lastwordsbeforearchichoicethispassword','lastwordsbeforearchichoice thispassword',
'shabef','shabefanstoo','shabef anstoo','shabef ans too','sha256anstoo','sha256answerstoo','answerstoo','anstoo','efanstoo','sha2efanstoo','sha256ansii',
'shabefourfirsthintisyourlastcommand','ourfirsthintisyourlastcommand','our first hint is your last command','ourfirsthint','yourlastcommand','firsthint','lastcommand','ourfirsthintisyourlastcommandenter',
'shabefourfirsthintisyourlastcommandentershabefanstoo','s h a b e f o u r f i r s t h i n t i s y o u r l a s t c o m m a n d enter s h a b e f a n s t o o',
'enter','ENTER','entershabefanstoo',
'followthewhiterabbit','follow the white rabbit','follow_the_white_rabbit','follow_the_white_rabbit.png','/img/follow_the_white_rabbit.png','Follow the white rabbit','followthewhiterabbitescape','follow the white rabbit escape','whiterabbit','white rabbit','whiterabbits','white rabbits everywhere','whiterabbitseverywhere','rabbit2','rabbit','therabbit','rabbitsnest','rabbits nest','the rabbits nest','beware that the rabbits nest may contain a whole lot more','bewaretherabbitsnestmaycontainawholelotmore','rabbitsnestmaycontainawholelotmore','awholelotmore','hushhush','hush hush','Hush hush.',
'GSMG MEGANIGMA || 5 BTC','GSMGMEGANIGMA5BTC','meganigma','MEGANIGMA','GSMG MEGANIGMA','mecanigma','Mécanigma','megaenigma','mega enigma',
'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe','GSMG.IO 5 BTC PUZZLE CHALLENGE','gsmgio5btcpuzzlechallenge',
'c0SJrSYKJx2n8MDF6Wt6i5gjkpfblfETLVrChemb',
'salvation','salphation','salphaseion','SalPhaseIon','salph','Sal','Phase','Ion','SalPhase','PhaseIon','sal phase ion','as phaseolin','phaseolin','phasel','beans','salphaselon','SalPhaselon','salphasion','salphaseionsalvation','feelofsalvation','the feel of salvation',
'cosmicduality','cosmic duality','Cosmic Duality','cosmicdualitybook','Cosmic Duality Book','lifeanddeath','life and death','mysteriesoftheunknown','cosmic dulty','cosmicdulty',
'bgaehgbhfcecebia','cfobfdhgdobdgooiigdocdaoofidh','cfobfdhgdobdgooiigdocdaoofidhe',
'100433436204244105573859228564110291168344943733122168512511','ffffdfffffff7ffefffffbfff7ffeeffdffffffffffffdfff',
'69119','16382137','257','Harmonic Primes','harmonicprimes','harmonic primes 69119','000dff','010101','fefefe','FEFEFE','fefe','FEFE','f5f5f5','ffffff','FFFFFF','#FEFEFE','#fefefe','fefefeinverse','010101fefefe',
'51°31\'22.1"N 4°14\'32.4"E','51 31 22.1 N 4 14 32.4 E','51.8701111,4.4217222','51°52\'12.4"N 4°25\'18.2"E','51 52 12.4 N 4 25 18.2 E','4.4217222,51.8701111','51.8701111','4.4217222',
'3398717423028438554530123627613875835633986495969597423490929302771479','6264200187401285096151654948264442219302037178623509019111660653946049',
'3398717423028438554530123627613875835633986495969597423490929302771479*6264200187401285096151654948264442219302037178623509019111660653946049',
'21290246318258757547497882016271517497806703963277216278233383215381949984056495911366573853021918316783107387995317230889569230873441936471','RSA-140','RSA140','rsa140','hundredfourty','HUNDRED FOURTY','hundred fourty','hundredfourtytimes','140','ECC140','ecc 140','datamatrix','Data Matrix','IDMatrix','ID Matrix','ID',
'ddb56305316ba63d12c659a64708dc19f50c0f7bc515f52092a3e7b78e248738','1a57c572caf3cf722e41f5f9cf99ffacff06728a43032dd44c481c77d2ec30d5','250f37726d6862939f723edc4f993fde9d33c6004aab4f2203d9ee489d61ce4c','eb3efb5151e6255994711fe8f2264427ceeebf88109e1d7fad5b0a8b6d07e5bf',
'sknab rof tuoliab dnoces fo knirb no rollecnahC 9002/naJ/30 semiT ehT','The Times 03/Jan/2009 Chancellor on brink of second bailout for banks','TheTimes03Jan2009Chancelloronbrinkofsecondbailoutforbanks','thetimes03jan2009chancelloronbrinkofsecondbailoutforbanks',
'736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854',
'0x736B6E616220726F662074756F6C69616220646E6F63657320666F206B6E697262206E6F20726F6C6C65636E61684320393030322F6E614A2F33302073656D695420656854',
'000000000000000067736d672e696f2f746865736565646973706c616e746564','67736d672e696f2f746865736565646973706c616e746564','gsmg.io/theseedisplanted','theseedisplanted','the seed is planted','theseedisplantedwhenoppositesattract','the seed is planted when opposites attract','whenoppositesattract','when opposites attract','oppositesattract',
'icantbreathe','iliterallycantbreathe','lastwordsbeforefloydschoice',
'thematrixhasyou','THEMATRIXHASYOU','the matrix has you','control','Control','whatisthematrix','what is the matrix','causalitycontrol','controlcausality',
'follow_this_logic_instead','followthislogicinstead','follow this logic instead',
'gsmg.io magic puzzle piece','magic puzzle piece','magicpuzzlepiece','gsmgiomagicpuzzlepiece','Distance to Road','distancetoroad','estate955','955','-41,-17','-41-17','4117',
'HASHTHETEXT','hashthetext','hash the text','hashhash','hash hash',
'CIAO BELLA O','ciaobellao','ciao bella o','bellaciao','bella ciao','bella-ciao','ciaobella',
'prime basics','primebasics','the prime basics','reinsertingtheprimebasics','reinserting the prime basics','prime','primes','primenumbers','prime numbers','primecode','prime code binary','primecodebinary',
'private keynote','privatekeynote','the actual private keynote','theactualprivatekeynote','private key note','privatekeymaker','private keymaker','the private keymaker','theprivatekeymaker','keymaker','the keymaker','thekeymaker','are you looking for the private keymaker','areyoulookingforthekeymaker',
'half and better half','halfandbetterhalf','betterhalf','better half','half','HALF AND BETTER HALF','halfandbetterhalfandtheyalsoneedfundstolive','theyalsoneedfundstolive','they also need funds to live','fundstolive',
'INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE','incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive','incaseyoumanagetocrackthis','in case you manage to crack this','theprivatekeysbelongtohalfandbetterhalf',
"m/44'/0'/0'/9/11","m/44'/0'/0'/11/9","m/0'/0'/0'","m/44'/0'/0'/0/0","9/11","911","11/9","119","09112001","11092001","20010911","sept112001","september 11 2001",
'2555125','2633372','4229262','2566342','3254392','6212648','8332572','7525227','9812525','6255775','9825775','6266797','5885288',
'25 26 27 28 29 30 32 37 43 44','2526272829303237434444','25262728282930303237434344',
'9223372035151810474','9223372035151810250','4.23298e+89',
'yellow=9 blue=15','yellow9blue15','915','159','9 15','yellow 9 blue 15','Yellow=0 Blue=1','yellow0blue1','01','10','yellow=2 blue=11 red=5','2115','yellow2blue11red5',
'00000021021111','12311201102001','1000121111010','12111011210112','0000002102111112311201102001','100012111101012111011210112',
'24 bits','24bits','154 bits','154bits','24154','154','24','38','237','38237','23738',
'2','11','5','3','3 and 5','35','53','13','15','9','20','23','7','237','23 7','101','101010','010101','131313','151515',
'Simulacra Simulation','simulacrasimulation','simulacraandsimulation','simulacra and simulation','simulacra',
'trainman','Trainman','the trainman','mobilave','mobil ave',
'x2sh','X2SH','qbhs','QBHS','qbsh','QBSH','xshqb','X 2 S H 4 Y 0 Q B 15','# X 2 S H 4 Y 0 Q B 15 #','x2sh4y0qb15','#x2sh4y0qb15#','XSHYQB','xshyqb','#xsh#','xsh','x2sh4y0qb15reversed','51bq0y4hs2x',
'82','-16','25','-25','42','32','8242','82423225','823242','S32B25H42Q82','32254282','Q82','B25','B-16','H42','S32','s32b-16h42q82','32-164282','SafenetLunaHSM11110','SafenetLunaHSM1111','SafenetLunaHSM','safenetlunahsm','thales','Thales','safenet','SafeNet','Safenet Netherlands','safenetnetherlands','gemalto','belikin','budweiser',
'(i5-i)^2','(5i-i)^2','(4i)^2','(6i-i)^2','BV80605001911AP','bv80605001911ap','i5','5i','6i','i5-i','cha + (vagh * jav)','cha+(vagh*jav)','2+(5*6)','32','sqrt(-1)',
'theory of everything','theoryofeverything','thetheoryofeverything','toe','TOE','Think Different','thinkdifferent','think different',
'Infrared','infrared','belowtheredline','below the red line','redline','red line','theredline',
'Pandora','pandora','pandorasbox','pandoras box','Pandora\'s box',
'reverse binary','reversebinary','reversedbinary','binaryreversed',
'giveit','givetit','give it','giveitjustonesecond','jacquefrescogiveit','heisenbergsuncertaintyprinciple',
'LOVE','love','Love','theone','the one','neo','Neo','trinity','Trinity','oracle','Oracle','smith','Smith','morpheus','Morpheus','cypher','Cypher','zion','Zion','merovingian','Merovingian','thefrenchman','architect','Architect','thearchitect','persephone','Persephone','seraph','Seraph','niobe','sati','Sati','ramkandra','rama-kandra','agentsmith',
'alphaandomega','alpha and omega','alphaomega','beginningandend','the beginning and the end','thebeginningandtheend',
'3-2-2','322','3 2 2','pattern322',
'Rc6','rc6','RC6',
'purple pill','purplepill','thepurplepill','Have you tried the purple pill already?','haveyoutriedthepurplepillalready','candyflipping','candy flipping','Candy flipping into 2024','candyflippinginto2024','redpill','red pill','bluepill','blue pill','redpillbluepill','purple',
'Regular Bitcoin Private key','regularbitcoinprivatekey','regular bitcoin private key','RegularBitcoinPrivatekey','privatekey','private key','bitcoinprivatekey',
'~2000 new messages, great. You all doing ok?','Heeeeelllloooooooo','Happy Christmas all','happychristmasall',
'Something was solved rather... remarkable.','somethingwassolvedratherremarkable','ratherremarkable','rather remarkable','remarkable','remark',
'the internet is not needed anymore','theinternetisnotneededanymore','internetnotneeded',
'the puzzle speaks to him','thepuzzlespeakstome','the puzzle speaks to me',
'there is another door','thereisanotherdoor','anotherdoor','another door','thirddoor','third door','the third door','door','doors','backdoor','back door','the back door','thebackdoor','otherdoor','other door','theotherdoor','extradoor','extra door','theextradoor','door3','3doors','threedoors','fourdoors','4doors','2doors','twodoors','doortoheaven','door to heaven','heaven','leadingustoheaven','thirddoorisleadingustoheaven',
'left','center','right','leftdoor','centerdoor','rightdoor','left center right','leftcenterright',
'Are you really looking for just the btc...?','areyoureallylookingforjustthebtc','are you really looking for just the btc','notjustthebtc','just the btc','justthebtc',
'woman in the red dress','womanintherededress','thewomanintherededress','red dress','reddress','lookagain','look again',
'it is the question that drives us','itsthequestionthatdrivesus','thequestionthatdrivesus','the question that drives us','whatisthematrix',
'you were sent here','youweresenthere','told to come here and obeyed','toldtocomehereandobeyed',
'the ironic 2name of the keymakers','theironicnameofthekeymakers','ironic','2name','keymakers','thekeymakers',
'eps3.4_runtime-error.r00','eps3.4runtime-error.r00','eps3.4','runtime-error.r00','runtimeerror','runtime-error','r00','eps34runtimeerrorr00',
'latin 3Moon','latin3moon','luna','Luna','3Moon','moon','Moon','4How so mate','howsomate','hsm','HSM',
'hackers swordless fish','swordfish','Swordfish','blowfish','Blowfish','swordlessfish','sword',
'dbbib','dbbi','faed','fead','dbbdi','dbbibfaed','faeddbbib','dbbifaed','faeddbbi','dbbib faed','dbbi and faed','dbbibandfaed',
'matrixsumlist','matrix sum list','matrix sumlist','matrixsumlist.py','matrixsumlist.sh','matrix','Matrix','the matrix','thematrix','sumlist','sum list','matrixsum','matrix sum',
'abba','abbaa','lastwordsbeforeachichoice',
'Vic','vic','viccipher','vic cipher','VIC','checkerboard','straddlingcheckerboard','straddling checkerboard','bacon','baconcipher','Bacon cipher','bookcipher','book cipher','hitchhikersguide','hitchhiker\'s guide','hitchhikers guide to the galaxy','hillcipher','hill cipher','a1z26','A1Z26','bifid','base16','base 16','hex','base3','base 3','delastile','base58','Base58','wif','WIF','base85','base 85','127','mod127',
'Heisenberg','heisenberg','uncertaintyprinciple','uncertainty principle','jacquefresco','jacque fresco','venusproject','venus project','thevenusproject',
'causality','Causality','causalitySafenetLunaHSM11110',
'PGP Secret Sub-key','pgpsecretsubkey',
'bip39','bip 39','bip wordlist','bipwordlist','mnemonic','12words','twelve words','seed','seedphrase','seed phrase','theseed','the seed','seedisplanted','seed is planted',
'1GSMG','1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe','3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK','1ucy','1Ucy','Halving','halving','thehalving','the halving','2aa9a4a90be819d5122d70c993280785a0508f163521e7b38cebb4db0b071b13','a798905f53fdcadcbd2e2a1e61d23ba69a07e26130a78c76da4bf4d7a170f383',
'a9553269572a317e39f0f518cb87c1a0ee1dbae4','4bc468447fe1b048ad030a2f9a125478eabc4ed6','A9553269572A317E39F0F518CB87C1A0EE1DBAE4','14F23FD58189AD7EE1D794AD8CC16D7D','3AB585348552415D',
'76a914a9553269572a317e39f0f518cb87c1a0ee1dbae488ac','76a9144bc468447fe1b048ad030a2f9a125478eabc4ed688ac',
'rabbit lives at FEFE square','therabbitlivesatfefesquare','rabbitfefe','fefesquare','fefe square','white pixel','whitepixel','offbyonewhitepixel','off by one white pixel','nearwhite','near white','7,4','74','row7col4','4,7','47',
'the seed is pla(N)ted','plaNted','planted','N','pla n ted',
'Roses are White but often Red','rosesarewhitebutoftenred','roses are white but often red','rosesarewhite','white','red','ten','TEN','10','rosesarewhitebutoftenredyellowhasanumberandsodoesblue','yellowhasanumberandsodoesblue','yellow has a number and so does blue','Yellow has a number and so does Blue.','yellowhasanumber','sodoesblue','yellow','blue','yellowblue','yellow blue','blueyellow','blue yellow','yellowandblue','yellow and blue','night turns into day','nightturnsintoday','yellowintoblue','yellow into blue','reversethecolors','reverse the colors','swap','swapped','yellowblueswapped','yellow blue swapped','invert','inverse','inverted','invertlinear','invert values',
'go back to the first puzzle piece without further ado','gobacktothefirstpuzzlepiece','firstpuzzlepiece','first puzzle piece','thefirstpuzzlepiece','puzzlepiece','puzzle piece','puzzlepiece.mp3','decentraland.mp3','withoutfurtherado','without further ado','it might have shown you only one door','itmighthaveshownyouonlyonedoor','onlyonedoor','only one door','onedoor','one door',
'QmeRy5MjmEZ2W6J3DwhQfht5HKBKXBFpoGzSkzmjeGKiDK',
'Mohammed','Javeed','Saber','okayzeal','whoami','Rabbit','Robbit','sitedude','StealingApples','nadiseo','Naddiseo','IlyaVolostnykh','Ilya Volostnykh','ilyavolostnykh',
'thefunctionoftheyou','the function of the you','return to the source codes','returntothesourcecodes','sourcecodes','source codes','source code','sourcecode','thesource','the source','temporarydissemination','temporary dissemination','dissemination',
'twentythreeciphers','twenty three ciphers','23ciphers','sixteenencryptions','sixteen encryptions','16encryptions','sevenintertwinedpasswords','seven intertwined passwords','7passwords','7intertwinedpasswords','intertwined','bruteforcingmightberequired','brute forcing might be required','16 females and 7 males','16females7males','167','16 7','23 16 7','23167',
'yourlifeisthesumofaremainder','your life is the sum of a remainder','sumofaremainder','sum of a remainder','remainder','unbalancedequation','unbalanced equation','entirenessofyourself','entireness of yourself','entireness','self','Self','you','me','You Me Self','youmeself',
'theremainderwasneverspent','whoknowswhatyouwillfindafteropeningtheotherdoor','who knows what you will find after opening the other door',
'take the private key youve earned it','taketheprivatekeyyouveearnedit','youveearnedit','earned','earn it','earnit',
'tempus fugit','Tempus fugit',
'battering ram','batteringram','ram','RAM','not rabbit a ram',
'Forbidden Regions of Impedance Matching','forbiddenregionsofimpedancematching','impedance matching','impedancematching','norton','nortonstheorem','Norton','thevenin','Thevenin',
'george floyd','georgefloyd',
'scribd puzzle-1','puzzle-1','puzzle1',
'rabbit meme coin','rabbitmemecoin',
'8a70N','8а70N',
'Cookie constant notification','cookieconstant','cookie constant','cookie',
'IHDR','sRGB','gAMA','pHYs','IDAT','IEND','phys','pHYs prime hole yin-yang sha','primeholeyinyangsha','prime hole yin-yang sha','yy','YY','yy mm','yymm',
'0e c4','0ec4','3780','95 2b 0e 1b','952b0e1b','44 bc bb 3b','44bcbb3b','1048','350','350x350','1048px',
'gsmg','GSMG','gsmg.io','GSMG.io','gsmgio','gsmg.io/puzzle','/puzzle','/PuZZle','PuZZle','puzzle','Puzzle','PUZZLE','gsmg.io/PuzZle','PuzZle',
'echo -e "GET /89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32 HTTP/1.1"','GET /89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32 HTTP/1.1','89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32','openssl s_client -connect gsmg.io:443','curl','GET','openssl','openssl enc -aes-256-cbc -d -a','enc -aes-256-cbc','aes-256-cbc','aes256cbc',
'Jrk Bgrt','JrkBgrt','jrkbgrt','jrk','Jrk','SoWut','sowut','@SoWut',
'When the last Rose blooms, everyone will look at it, but no one will cut it','whenthelastroseblooms','the last rose','lastrose','last rose',
'the only date I give away is the expiry date of neos passport','neospassport','neo\'s passport','neos passport','passport',
'One for one, four for one.','oneforonefourforone','one for one four for one','1for1 4for1','1141','1 4 21','{1},{4},{21}','1 4 21 door','1421','14 21','1,4,21',
'U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z','QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ',
'U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9zQvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ',
'U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46zgKlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4',
'b6','f7','b6f7','0xb6','0xf7',
'all the 4 phases gonna decode the last face','the4phases','4phases','phase0','phase1','phase2','phase3','phase3.2','phase3.2.2','phase 3.2.2','322','3.2.2','3.2.1','3.2.3','2.4','phase2.4',
'theflowerblossomsthroughwhatseemstobeaconcretesurface','if it were to fall upon you today which flower would you be','ifitweretofalluponyoutodaywhichflowerwouldyoube','whichflowerwouldyoube','which flower would you be','flower','theflower','the flower','rose','roses','redrose','whiterose','blackrose','red rose or black rose','redroseorblackrose','noinbetween','no in-between','red rose or white rose','redroseorwhiterose',
'choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself','choice','Choice','archichoice','archi choice','architectschoice','architects choice','thearchitectschoice','choiceisanillusion','choice is an illusion','averyspecialdessertiwroteitmyself','a very special dessert i wrote it myself','dessert',
'lastwordsofjesus','last words of jesus','itisfinished','it is finished','fatherintoyourhandsicommitmyspirit','father into your hands i commit my spirit','consummatumest','consummatum est','eloieloilamasabachthani','eli eli lama sabachthani','tetelestai',
'architectlastwords','the architects last words','youhavemysympathies','you have my sympathies','ergo','concordantly','vis-a-vis','visavis','inexorably','denouement','hope','Hope','itisthequintessentialhumandelusion','quintessential human delusion','simultaneously the source of your greatest strength and your greatest weakness','asyouadequatelyputtheproblemischoice','the problem is choice','theproblemischoice','problemischoice',
'B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1','B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2','fubcd','fubcdking','oracle-queen','oraclequeen','thingky','thingkymvps','thingky mvps','sadboard','sad board','aswideasthefirstoneseen','as wide as the first one seen','raisingthestakes','raising the stakes',
'1jacquefrescogiveitjustonesecondheisenbergsuncertaintyprincipl','jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple',
'x7x7x7x6','x7','7x',
)

# ddb56305… hash check against obvious preimages
target = 'ddb56305316ba63d12c659a64708dc19f50c0f7bc515f52092a3e7b78e248738'
for p in ['yellowblueprimes', DBBI, FAED, 'matrixsumlist', 'thispassword', 'lastwordsbeforearchichoice', 'yinyang', 'salvation', 'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe', dd, fd, 'yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangwewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingitverylaststepisatruegiveawaypromised','shabefanstoo','ourfirsthintisyourlastcommand','enter','followthewhiterabbit','rabbit']:
    if hashlib.sha256(p.encode()).hexdigest() == target: print('ddb563 preimage FOUND:', p)
    if hashlib.sha256(hashlib.sha256(p.encode()).hexdigest().encode()).hexdigest() == target: print('ddb563 double preimage FOUND:', p)

# dedupe preserving order, cap 3000
seen=set(); out=[]
for c in C:
    if c not in seen:
        seen.add(c); out.append(c)
out = out[:3000]
open('/home/vin/bitcoin_puzzle/scratch/wf/cands_chunk04.txt','w',encoding='utf-8').write('# chunk04 candidates (verbatim strings + claimed decodes from Telegram chunk04, 2023-11-26 .. 2024-02-18)\n' + '\n'.join(out) + '\n')
print('wrote', len(out), 'candidates')

# doors: prefer not previously probed
prev=set()
for f in glob.glob('/home/vin/bitcoin_puzzle/scratch/wf/cands_chunk0[0-3]_doors.txt') + glob.glob('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_*doors*.txt'):
    for l in open(f, encoding='utf-8', errors='replace'):
        l=l.strip()
        if l and not l.startswith('#'): prev.add(l); prev.add(re.sub(r'[^a-z0-9]','',l.lower()))
doors_pref = ['yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyangwewontgiveawaythepassworditsinfrontofyoureyesbutyourenotseeingitverylaststepisatruegiveawaypromised',
 'ourfirsthintisyourlastcommand','shabefanstoo','shabefourfirsthintisyourlastcommand','rabbit2','follow_the_white_rabbit.png','follow_the_white_rabbit','purplepill','candyflipping','regularbitcoinprivatekey',
 'primebasics','privatekeynote','privatekeymaker','thereisanotherdoor','thirddoor','backdoor','heaven','infrared','belowtheredline','theoryofeverything','thinkdifferent','magicpuzzlepiece','gsmgiomagicpuzzlepiece','distancetoroad',
 'hushhush','hashthetext','simulacraandsimulation','trainman','control','whatisthematrix','womanintherededress','wewontgiveawaythepassword','itsinfrontofyoureyes','verylaststepisatruegiveawaypromised','atruegiveaway',
 'thepassword','lastwordsbeforearchichoicethispassword','phaseolin','harmonicprimes','rosesarewhitebutoftenred','yellowhasanumberandsodoesblue','rabbitsnestmaycontainawholelotmore','bgaehgbhfcecebia','cfobfdhgdobdgooiigdocdaoofidh',
 pm0.replace('?','').replace(' ',''), 'alphaandomega','redpill','bluepill','halfandbetterhalfandtheyalsoneedfundstolive','incaseyoumanagetocrackthis','sevenintertwinedpasswords','twentythreeciphers','sixteenencryptions',
 'yellow9blue15','fefefe','010101','000dff','salphation','thefeelofsalvation','cosmicdualitylifeanddeath','mysteriesoftheunknown','whoknowswhatyouwillfindafteropeningtheotherdoor','taketheprivatekeyyouveearnedit']
doors=[]
for d in doors_pref:
    k = re.sub(r'[^a-z0-9]','',d.lower())
    if d in prev or k in prev: continue
    if d not in doors: doors.append(d)
    if len(doors) >= 40: break
open('/home/vin/bitcoin_puzzle/scratch/wf/cands_chunk04_doors.txt','w').write('# chunk04 door-type candidates (sha256hex(C) probed as gsmg.io/<hex>); deduped against chunk00-03 and lens door files\n' + '\n'.join(doors) + '\n')
print('wrote', len(doors), 'doors'); print(doors)
