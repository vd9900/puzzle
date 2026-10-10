import hashlib, re, sys
sys.path.insert(0,'/home/vin/bitcoin_puzzle')
from tools.gsmg import PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE, TARGET_ADDRESS
H=lambda s: hashlib.sha256(s.encode()).hexdigest()
raw=open('/home/vin/bitcoin_puzzle/research/sources/salphaseion.html','rb').read()
tas=re.findall(rb'<textarea[^>]*>(.*?)</textarea>', raw, re.S); s=b''.join(tas[0].split(b' ')).decode()
DBBI=s[:91]; BIN1=s[91:195]; FAED=s[195:765]; Z1=s[766:829]; Z2=s[830:859]; Z3TXT=s[860:895]; LINE1=s[895:959]; BIN2=s[959:999]; LINE2=s[999:1063]; TAILTXT=s[1063:]
assert Z3TXT=='shabefourfirsthintisyourlastcommand' and TAILTXT=='shabefanstoo' and BIN2.startswith('abba') and len(BIN2)==40, (Z3TXT,TAILTXT,BIN2)
tr={**{c:str(k+1) for k,c in enumerate('abcdefghi')},'o':'0'}
Z1d=''.join(tr[c] for c in Z1); Z2d=''.join(tr[c] for c in Z2); Z1h=hex(int(Z1d))[2:]; Z2h=hex(int(Z2d))[2:]
lyric='theflowerblossomsthroughwhatseemstobeaconcretesurface'
FIRSTHINT='5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75'
assert H(lyric)==FIRSTHINT
URLHASH='89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32'; assert H(SALPHASEION_PREIMAGE)==URLHASH
P2SLUG='choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself'
answers=[('theseedisplanted','theseedisplanted'),('phase1lyric',lyric),('causality','causality'),('phase3',PHASE3_PREIMAGE),('phase32',PHASE32_PREIMAGE),('salphaseion',SALPHASEION_PREIMAGE)]
C=[]  # (comment, candidate)
def add(tag, c):
    if c: C.append((tag,c))
# A. each earlier phase answer: raw (oracle adds sha256), sha256hex (oracle adds double), sha256hex^2 (oracle adds triple), upper-hex, sha256 of raw digest hex
for tag,a in answers:
    add(f'A raw {tag}',a); add(f'A sha {tag}',H(a)); add(f'A sha2 {tag}',H(H(a))); add(f'A sha3 {tag}',H(H(H(a)))); add(f'A SHAUP {tag}',H(a).upper())
    add(f'A sha(digest) {tag}', hashlib.sha256(hashlib.sha256(a.encode()).digest()).hexdigest())
    add(f'A sha(nl) {tag}', H(a+'\n'))
add('A url-hash', URLHASH); add('A sha url-hash', H(URLHASH)); add('A sha2 url-hash', H(H(URLHASH)))
add('A p2 slug', P2SLUG); add('A sha p2 slug', H(P2SLUG)); add('A gsmg.io/theseedisplanted','gsmg.io/theseedisplanted'); add('A target', TARGET_ADDRESS)
# B. first hint = the posted hash (literal reading of z-seg3)
add('B firsthint hash', FIRSTHINT); add('B sha firsthint', H(FIRSTHINT)); add('B sha2 firsthint', H(H(FIRSTHINT))); add('B firsthint upper', FIRSTHINT.upper()); add('B sha firsthint upper', H(FIRSTHINT.upper()))
add('B firsthint+enter', FIRSTHINT+'enter'); add('B enter+firsthint','enter'+FIRSTHINT); add('B lyric+enter', lyric+'enter')
add('B firsthint+thispassword', FIRSTHINT+'thispassword'); add('B thispassword+firsthint','thispassword'+FIRSTHINT)
add('B sha(firsthint)+sha(ans)', H(FIRSTHINT)+H('thispassword'))
# C. page tokens and their translations
toks=['matrixsumlist','lastwordsbeforearchichoice','thispassword','enter','Enter','ENTER','shabefourfirsthintisyourlastcommand','shabefanstoo','sha256ourfirsthintisyourlastcommand','sha256anstoo','ourfirsthintisyourlastcommand','ourfirsthint','firsthint','yourlastcommand','lastcommand','anstoo','ans','answer','sha256answertoo','sha256answerstoo','sha256','shabef','salphaseion','SalPhaseIon','cosmicduality','CosmicDuality','Cosmic Duality','sha256 our first hint is your last command','sha256 ans too','shabef our first hint is your last command','shabef ans too','our first hint is your last command']
for t in toks: add('C token',t); add('C sha token',H(t))
add('C Z1 raw',Z1); add('C Z2 raw',Z2); add('C Z1 digits',Z1d); add('C Z2 digits',Z2d); add('C Z1 hex',Z1h); add('C Z2 hex',Z2h)
add('C DBBI',DBBI); add('C FAED',FAED); add('C BIN1',BIN1); add('C BIN2',BIN2); add('C LINE1',LINE1); add('C LINE2',LINE2)
add('C Z3 with z', 'z'+Z3TXT); add('C zenter','zenter'); add('C z-enter','z enter')
# D. concatenations in page order
# D1 answers cumulative and sha-chained
acc=''; chain=''; joined=''
for tag,a in answers:
    acc+=a; add(f'D1 cum {tag}',acc); add(f'D1 sha cum {tag}',H(acc))
    chain = H(chain+a) if chain else H(a); add(f'D1 chain h=sha(h+a) {tag}',chain)
    joined += H(a); add(f'D1 joined hashes {tag}',joined); add(f'D1 sha joined {tag}',H(joined))
chain2=''
for tag,a in answers:
    chain2 = H(a+chain2) if chain2 else H(a); add(f'D1 chain h=sha(a+h) {tag}',chain2)
# answers + salphaseion page tokens continuing the chain
page_ans=['matrixsumlist','lastwordsbeforearchichoice','thispassword','enter']
for extra in page_ans:
    add('D1 allanswers+'+extra, acc+extra); add('D1 sha allanswers+'+extra, H(acc+extra)); add('D1 chain+'+extra, H(chain+extra)); add('D1 joined+'+extra, joined+H(extra))
# D2 page-token order
seq=['matrixsumlist','lastwordsbeforearchichoice','thispassword','sha256ourfirsthintisyourlastcommand','enter','sha256anstoo']
for i in range(len(seq)):
    for j in range(i+1,len(seq)+1):
        c=''.join(seq[i:j])
        if j-i>=2: add('D2 tokens',c); add('D2 sha tokens',H(c))
seqb=['matrixsumlist','lastwordsbeforearchichoice','thispassword','enter']
for i in range(len(seqb)):
    for j in range(i+2,len(seqb)+1): add('D2b',''.join(seqb[i:j])); add('D2b sha', H(''.join(seqb[i:j])))
# with FIRSTHINT substituted for the hint sentence
seqc=['matrixsumlist','lastwordsbeforearchichoice','thispassword',FIRSTHINT,'enter']
for i in range(len(seqc)):
    for j in range(i+2,len(seqc)+1): add('D2c',''.join(seqc[i:j])); add('D2c sha', H(''.join(seqc[i:j])))
# D3 raw page segments in order
segs=[DBBI,BIN1,FAED,Z1,Z2,Z3TXT,LINE1,BIN2,LINE2,TAILTXT]
for i in range(len(segs)):
    for j in range(i+2,len(segs)+1): add('D3 segs',''.join(segs[i:j]))
add('D3 compact all', s); add('D3 decoded page', DBBI+'matrixsumlist'+FAED+'lastwordsbeforearchichoice'+'thispassword'+'sha256ourfirsthintisyourlastcommand'+'enter'+'sha256anstoo')
add('D3 decoded tokens only', 'matrixsumlist'+'lastwordsbeforearchichoice'+'thispassword'+'sha256ourfirsthintisyourlastcommand'+'enter'+'sha256anstoo')
add('D3 dbbi+faed', DBBI+FAED); add('D3 Z1+Z2', Z1+Z2); add('D3 Z1Z2 digits', Z1d+Z2d); add('D3 Z1Z2 decoded','lastwordsbeforearchichoicethispassword')
# E. first-hint alternatives
alts=['followthewhiterabbit','Follow the white rabbit','whiterabbitseverywhere','White Rabbits everywhere','rosesarewhitebutoftenredyellowhasanumberandsodoesblue','Roses are White but often Red, Yellow has a number and so does Blue','HASHTHETEXT','hashthetext','theseedisplanted','the seed is planted','GSMG MEGANIGMA || 5 BTC','meganigma','just try hit your options against that hash.','justtryhityouroptionsagainstthathash','5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75\n']
for a_ in alts: add('E alt firsthint',a_.rstrip('\n')); add('E sha alt',H(a_))
# F. 'last command' as openssl command strings
cmds=['openssl enc -aes-256-cbc -a -d','openssl enc -d -aes-256-cbc -a','openssl aes-256-cbc -d -a','openssl enc -aes-256-cbc -d -a -in','enc -aes-256-cbc -a','openssl','sha256sum','echo -n','exit','logout','ls','cd','sudo','enter','return','\\n']
for c_ in cmds: add('F cmd',c_); add('F sha cmd',H(c_))
# write
seen=set(); out=[]
for tag,c in C:
    c=c.replace('\n','')  # file is one candidate per line
    if c in seen or not c: continue
    seen.add(c); out.append(c)
open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_parse_skeptic.txt','w').write('# lens parse_skeptic: phase-answer sha256 chains, first-hint hash (5ac4..=sha256(phase1 lyric)), page-order concatenations, enter variants\n'+'\n'.join(out)+'\n')
print('main candidates', len(out))
# doors: lowercase-alnum preimages -> gsmg.io/sha256hex(C); filter against _doors_seen
seen_doors=set(l.strip() for l in open('/home/vin/bitcoin_puzzle/scratch/wf/_doors_seen.txt') if l.strip() and not l.startswith('#'))
seen_doors_h={H(d) for d in seen_doors}|{H(re.sub(r'[^a-z0-9]','',d.lower())) for d in seen_doors}
doors=[lyric, FIRSTHINT, H(FIRSTHINT), 'enter','shabefanstoo','sha256anstoo','anstoo','ourfirsthint','firsthint','yourlastcommand','lastcommand','ourfirsthintisyourlastcommand','shabefourfirsthintisyourlastcommand','sha256ourfirsthintisyourlastcommand','thispassword','lastwordsbeforearchichoice','matrixsumlist','theseedisplanted','causality',PHASE32_PREIMAGE,SALPHASEION_PREIMAGE,URLHASH,H(URLHASH),'salphaseion','cosmicduality','shabef','sha256','lastwordsbeforearchichoicethispassword','thispasswordenter','matrixsumlistlastwordsbeforearchichoicethispasswordenter','thispasswordsha256ourfirsthintisyourlastcommandentersha256anstoo', H(lyric+'\n'), 'followthewhiterabbit', 'hashthetext', 'enterenter', 'z', 'zenter', 'ans', 'answer', 'too']
dout=[]; dseen=set()
for d in doors:
    if H(d) in seen_doors_h or H(d) in dseen: continue
    dseen.add(H(d)); dout.append(d)
open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_parse_skeptic_doors.txt','w').write('# lens parse_skeptic doors: gsmg.io/<sha256hex(line)>; lyric line probes gsmg.io/5ac407.. (= "our first hint")\n'+'\n'.join(dout[:40])+'\n')
print('door candidates', len(dout[:40]), 'skipped as seen', len(doors)-len(dout))
# escaped side-file: passwords containing newline / raw bytes, tested via try_pw by parse_skeptic_escaped.py
esc=['\\n','\\r\\n','enter\\n','\\nenter', lyric+'\\n', FIRSTHINT+'\\n', 'causality\\n', PHASE32_PREIMAGE+'\\n', 'thispassword\\n', 'lastwordsbeforearchichoice\\n', 'matrixsumlist\\n', 'hex:'+FIRSTHINT, 'hex:'+H(FIRSTHINT), 'hex:'+URLHASH, 'hex:'+H('enter'), 'hex:'+H('thispassword'), 'hex:'+H('lastwordsbeforearchichoice'), 'b64:'+FIRSTHINT, 'b64:'+URLHASH, 'empty:']
open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_parse_skeptic_escaped.txt','w').write('# lens parse_skeptic: escaped candidates (python unicode_escape; hex:<64hex> = raw digest bytes as password; b64:<hex> = base64 of digest bytes; empty: = empty password). Retest with parse_skeptic_escaped.py\n'+'\n'.join(esc)+'\n')
print('escaped candidates', len(esc))
