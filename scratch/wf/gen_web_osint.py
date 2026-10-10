#!/usr/bin/env python3
"""Generate candidate lists for lens web_osint from post-2024 public write-ups (GitHub issues/repos, bitcointalk, Telegram quotes)."""
import sys, hashlib, re, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
WF = '/home/vin/bitcoin_puzzle/scratch/wf/'
out = []          # (candidate, source-tag)
def add(c, tag):
    c = c.strip('\n')
    if c: out.append((c, tag))

# ---------- A. Issue #115 (akaVARU, 2026-10-09) FAED chain, reproduced ----------
F = FAED.upper()
assert len(F) == 570 and F.startswith('FAED')
def groupsum_letters(s, g):
    vals = [ord(ch) - 64 for ch in s]
    res = ''
    for i in range(0, len(vals) - len(vals) % g, g):
        res += chr(65 + sum(vals[i:i + g]) % 26)
    return res
s63 = groupsum_letters(F[3:], 9)
claim63 = 'RPRRUAVBQMTOLVAZUUVXKNXXPIPDEZSSIEELUSODWOCXFSBYOGZAETLSEOKNAIJ'
print('#115 step2 reproduce:', s63 == claim63, s63)
def vig_sub(ct, key, period=None):
    period = period or len(key)
    return ''.join(chr(65 + (ord(c) - ord(key[i % period])) % 26) for i, c in enumerate(ct))
p12 = vig_sub(s63, 'THEPROBLEMIS')
p11 = vig_sub(s63, 'THEPROBLEMIS', 11)
claimP = 'YINCDMUQMALWSOWKDGUMGBPFWBLONLRHESWTBLKOFABMBGTGVZVLNFKHACCVHBF'
print('#115 step3 reproduce (period12):', p12 == claimP, ' (period11):', p11 == claimP)
print('   p12=', p12); print('   p11=', p11)
P = claimP
rest = P[3:]
A = rest[0::2]; B = rest[1::2]
print('   streams', A, B, A == 'CMQAWOKGMBFBOLHSTLOAMGGZLFHCVB', B == 'DUMLSWDUGPWLNREWBKFBBTVVNKACHF')
x = [(ord(a) - 65) ^ (ord(b) - 65) for a, b in zip(A, B)]
B32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
xs = ''.join(B32[v] for v in x)
m = [xs[i * 5:(i + 1) * 5] for i in range(6)]
def spiral_ccw(m):  # down left col, right along bottom, up right col, left along top, inward
    r, c = len(m), len(m[0]); top, bot, left, right = 0, r - 1, 0, c - 1; res = ''
    while top <= bot and left <= right:
        for i in range(top, bot + 1): res += m[i][left]
        left += 1
        for j in range(left, right + 1): res += m[bot][j]
        bot -= 1
        if left <= right:
            for i in range(bot, top - 1, -1): res += m[i][right]
            right -= 1
        if top <= bot:
            for j in range(right, left - 1, -1): res += m[top][j]
            top += 1
    return res
sp = spiral_ccw(m)
print('#115 step6 reproduce:', sp == 'BYTENPHASEGBDOEL4YJKSVTML2KSDB', sp)
for c in [s63, p12, p11, A, B, xs, sp, sp[:10], sp[10:], 'BYTENPHASE', 'BYTE N PHASE', 'byteandphase', 'bytenphase', 'BYTENPHASEGBDOEL[28]YJKSVTML[26]KSDB',
          'THEPROBLEMIS', 'theproblemischoice', 'THEPROBLEMISCHOICE', 'theproblemis', 'YIN', 'yinyang' + sp, 'yin' + sp[10:].lower(),
          ''.join(format(v, '05b') for v in x), ''.join(format(v, '05b') for v in x[10:])]:
    add(c, 'issue115')
# own variants: other group sizes / no FAE removal / other keys
for g in (5, 6, 10, 15, 19, 30, 57):
    add(groupsum_letters(F, g), f'issue115var_g{g}')
for g in (7, 9):
    add(groupsum_letters(F, g), f'issue115var_full_g{g}')
for key in ('CHOICE', 'THEPROBLEMISCHOICE', 'THEMATRIXHASYOU', 'LASTWORDSBEFOREARCHICHOICE', 'CAUSALITY', 'YINYANG', 'MATRIXSUMLIST', 'ARCHITECT', 'DENIAL', 'THEONE'):
    add(vig_sub(s63, key), f'issue115var_key_{key}')
# same chain on DBBI (91 = 7*13)
D = DBBI.upper()
for g in (7, 13):
    add(groupsum_letters(D, g), f'issue115var_dbbi_g{g}')

# ---------- B. XOR-of-sha256 master keys claimed in issues #56/#62/#69/#74/#94/#96, jackdevs66 repo ----------
def xorkey(tokens):
    k = bytearray(32)
    for t in tokens:
        for i, b in enumerate(hashlib.sha256(t.encode()).digest()): k[i] ^= b
    return bytes(k).hex()
T1 = ['matrixsumlist', 'enter', 'lastwordsbeforearchichoice', 'thispassword', 'matrixsumlist', 'yourlastcommand', 'secondanswer']
T2 = ['matrixsumlist', 'enter', 'lastwordsbeforearchichoice', 'thispassword', 'matrixsumlist', 'sha256', 'theone']
T3 = ['matrixsumlist', 'enter', 'lastwordsbeforearchichoice', 'thispassword', 'matrixsumlist', 'HASHTHETEXT', 'secondanswer']
T4 = ['matrixsumlist', 'enter', 'lastwordsbeforearchichoice', 'thispassword', 'yellowblueprimes', 'yinyang', 'esrever']
T5 = ['yellowblueprimes', 'matrixsumlist', 'lastwordsbeforearchichoice', 'yinyang']
for T, tag in ((T1, 'xor_T1'), (T2, 'xor_T2'), (T3, 'xor_T3'), (T4, 'xor_T4'), (T5, 'xor_T5')):
    add(xorkey(T), tag); add(''.join(T), tag + '_concat'); add(' '.join(T), tag + '_sp'); add('|'.join(T), tag + '_pipe')
    add(''.join(hashlib.sha256(t.encode()).hexdigest() for t in T), tag + '_hexconcat')
print('xor T1 =', xorkey(T1), 'claimed a795de11..', xorkey(T1).startswith('a795de11'))
print('xor T2 =', xorkey(T2), 'claimed 818af53d..', xorkey(T2).startswith('818af53d'))
print('xor T3 =', xorkey(T3), 'claimed b2d66f24..', xorkey(T3).startswith('b2d66f24'))
for h in ['a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735', '818af53daa3028449f125a2e4f47259ddf9b9d86e59ce6c4993a67ffd76bb402',
          'b2d66f2487d4172ce4ebfaea0763a65b363496df6c984c3d7759bb837d08899c', 'c3b87356f769b1a12acf2a76df3d7a5f1db595f07a5c0d4b5abdf731eab13ff5',
          '4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081', 'e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b',
          '9f06936a48d393c858a6fdce281540946e8f5365d632ad756c280b400c9d632c', 'a80a399af1221bd62538594141bee1064e1b071b547d60729f13c0224041a0f7',
          '38d4f4c90cb45fdfc8cff50d0ed1c5', '740a25de4b8e946d0a5ae2667a23a2', '31f6b59ad263158ca0aaa9bc5b6374c8e636a70e3328650b62533bc9ab173c12',
          'b522875df97efa3624957d4f41f82b59', '6ac438facf366702b60d6dfcebd39815b582f19b591b3fdf69240c6966f4fc23', 'c6ff2e39d98843bc3c26b8a33a15b5c9',
          '5bbd88ac32481bca', '0423d9115a1dc756d5d08d2de880ab508bd4745fc97709f4fcb513f2cb8fcc35', '48cc46e66bdd36b09ae344552f606a761f9d90681f20dfefe2b43db18b623971',
          'fc0c1b02', 'f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a464', 'a9553269572a317e39f0f518cb87c1a0ee1dbae4',
          '4b984b7d043aa90dff14759950b8c62616d45365cf8c8b4992ed90a0b4e78fa181033c668b9e0363f9dbba83ef851d41d08abb0d30243b726f60b4653edbd4eca74f76872a78163e93d720de1cce92bf',
          '15d62c82', 'e2590f15', 'cd3fea3d', '1449a217']:
    add(h, 'claimed_hex')

# ---------- C. token words / phrases from issues, forks, bitcointalk ----------
for w in ['yourlastcommand', 'secondanswer', 'theone', 'HASHTHETEXT', 'hashthetext', 'sha256', 'anstoo', 'answertoo', 'answertwo', 'answer2', 'answeralso', 'ans2000', 'A141920',
          'esrever', 'reverse', 'sumlist', 'rowcolsum', 'fourfirsthintisyourlastcommand', 'ourfirsthintisyourlastcommand', 'firsthintisyourlastcommand', 'yourlastcommandsecondanswer',
          'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist', 'matrixsumlistenterlastwordsbeforearchichoicethispassword', 'shabefanstoo', 'shabef', 'fanstoo',
          'followthewhiterabbit', 'Follow the white rabbit', 'matrixsumlist|enter|lastwordsbeforearchichoice|thispassword|matrixsumlist', 'MATRIXSUMLIST SECONDANSWER', 'shabefthispassword',
          'enterthispassword', 'thispasswordenter', 'enter thispassword', 'salvation', 'salphaseion', 'SalPhaseIon', 'cosmicduality', 'Cosmic Duality', 'dualite', 'Dualite',
          'yellowblueprimes', 'yinyang', 'yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang', 'yellow blue primes matrixsumlist lastwordsbeforearchichoice yinyang',
          'rabbitsnest', 'therabbitsnest', 'hushhush', 'Hush hush', 'merlon', 'Merlon', 'norton', 'nortonstheorem', 'emperornorton', 'FORTWOSEESEE', 'fortwoseesee', 'for two see see',
          'halfandbetterhalf', 'HalfABetterHalf', 'betterhalf', 'half', 'thebetterhalf', 'THE_HALF', 'THE_BETTER_HALF', 'bellaciao', 'BellaCiao', 'ciaobellao', 'CIAO BELLA O', 'ciaobella',
          'reinsertingtheprimebasics', 'theprimebasics', 'primebasics', 'anotherdoor', 'thirddoor', 'door', 'DOOR', 'youwon', 'YOUWON', 'wiseman', 'wisemanabove', 'thewisemanabove',
          'theoryofeverything', 'mtheory', 'unifiedfield', 'bytenphase', 'xortriangle', 'XOR triangle', 'triangular', 'K_I1', 'cosmic_A', 'robnik', 'ROBNIK', 'basefd^5',
          'Causality Transcended', 'causalitytranscended', 'false || echo "5 BTC"', 'entertherabbithole', 'redpill', 'iamtheone', 'leavethematrix', 'There is no spoon', 'thereisnospoon',
          'ALPHANOISES', 'alphanoises', 'The answer is women', 'theansweriswomen', 'itisonlywiththeheartthatoneseesrightlywhatisessentialisinvisibletotheeye',
          'FromN0EHalfABetterHalfBuiltItBellaCiao1_1Pi36y7LJugXwFNDVjR1p8p5JoB7eN5zSZ', 'FromN0EHalfABetterHalfBuiltItBellaCiao', '673b7b4b67571b1b4b-3.o', '844e86a69a04eea672049e0e0e8612',
          'HalfABetterHalfBuiltIt', '1_1Pi', 'N0E', 'FromN0E',
          '1vzA0tQRHbnXKd9C0W1yJ3C:vzDWa4yEERR', '1vzA0tQRHbnXKd9-C0W1-yJ3C:vzDWa4yEERR', 'HbnXKd9-C', '0W1-yJ3C:', '8b4e7DLwgG9', 'vzDWa4yEERR',
          'flag{4ES_1s_e4sy_t0_cr4ck_w1th_p4ssw0rd}', 'flag{8KJ}', 'M3DGNJTGMZTCMZTG', 'shposnitovermmjiolsjpjsroh', 'lastword sbee', 'lastwordsbee',
          'GSMG PUZZLE PHASE 3 SOLVED - HALF & BETTER HALF DERIVED FROM COSMIC DUALITY MATRIX',
          'Congratulations, but as you well know appearences can be deceiving', 'appearencescanbedeceiving', 'appearances can be deceiving',
          'wewontgiveawaythepassword', 'itsinfrontofyoureyesbutyourenotseeingit', 'verylaststepisatruegiveaway', 'promised', 'verylaststepisatruegiveawaypromised', 'wivp', '25392708',
          '11419201515', '1 14 19 20 15 15', 'whiterabbitseverywhere', 'White Rabbits everywhere']:
    add(w, 'tokens')
# verknode/GSMR + Naddiseo#13 + protogrid strings
for w in ['YOUDOIT', 'ANDYOUDOIT', 'youdoit', 'andyoudoit', 'privatekeyyouveearnedit', 'HEARTOFKEY', 'heartofkey', '0x1234D3F1', '1234D3F1', '1234d3f1', 'D3F1', '305452017',
          '10010001101001101001111110001', 'QNDPGPSDKLRNNLGFAKNSRRGVVDMGWGYBGLRAEELMKAEPMXXRM', 'YOUWONXCPKWGBNAXDGJGDUNNVMPABTAFPAAXMJYLZBUWERDNX', 'CDCQXCVHXJRJCMXIXHIDERI',
          'Rb7xh7', 'Rxh7', 'Rh7', 'b7h7', 'OOIIOOOIIOOIOIIOIOOOOIOIIOIOI', 'ECDCDDCEBCEDBECDECCEECEBCDDDC', 'DBIFHCEGA', 'DBIFHCEG', 'dbifhcegaklmnopqrstuvwxyz', 'DBIFHCEGAKLMNOPQRSTUVWXYZ',
          'DBIFGCEHA', 'DCHAGBEIF', 'DCGAHBEIF', 'EBIFHCDGA', 'EBIFGCDHA', 'ECHAGBDIF', 'ECGAHBDIF', 'THEDOORTOYOURRIGHT', '103993525', '632d0b5', '432877386', '19cd2f4a',
          'elastpartofthepuzzletaketheprivatekeyyouveearneditbutplease', 'thelastpartofthepuzzletaketheprivatekeyyouveearneditbutplease', 'takethistoheart', '450', '511', '482', '479', '484', '61', '452', '59',
          'deoemckeadhbschdkbdcsdkdvbxcpcochcrdicibqeebddbcndsbdcpdgcpdncncsescgddclenbmcuducqcacdeld', 'btcseeddeoemckeadhbschdkbdcsdkdvbxcpcochcrdicibqeebddbcndsbdcpdgcpdncncsescgddclenbmcuducqcacdeld',
          'elcmefdfesdodwckbycubwba', 'btcseed', 'BTCSEED', 'eyeseed', 'facebtc', 'HILLFEXMGSGQ', 'PRIVATEKEY', 'gsmg.io/theseedispla~ted', 'theseedispla~ted',
          '-4,2,32,12,4,27,0,2,-16,15', '-4 2 32 12 4 27 0 2 -16 15', '-42321242702-1615', '4232124270216 15', 'X=-4,H=12,Y=27,Q=2', '-4 12 27 2', '-412272',
          '610876654997879', '8108108736759668', '6108766549978798108108736759668', '610876654997879 8108108736759668', '6 10 8 7 6 6 5 4 9 9 7 8 7 9', '8 10 8 10 8 7 3 6 7 5 9 6 6 8',
          '6108766549978798108108736759668'[::-1], 'gsmgio/eseeisae', '.thdplntd', 'banking', 'ca', 'digi', 'dig i', 'crypto', 'you', 'bankingwar', 'warning', 'logic', 'digital', 'cryptologic',
          'digitallogic', 'digitallogiccryptography', 'youcan', 'locking', 'unlocking', 'opening', 'digit', 'cat', 'caning', 'cryptobanking', 'digitalbanking', 'bankingcrypto', 'lockit', 'nothing',
          'youcandigit', 'cadigi', 'ca dig i', 'warningyou', 'cryptogicyou', 'blue_ca', 'blue_dig_i', 'blue_lock_lo', 'red_crypto_gic', 'red_n_you', 'red_open_lock_n_ing', 'red_t', 'black_banking_-_war',
          'Rose', 'redrose', 'blackrose', 'whiterose', 'red rose', 'black rose', 'Ok kid, on the highway, let put it in the worst gear', 'worstgear', 'reversegear',
          'B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1', '0xBC', 'BC']:
    add(w, 'misc_osint')
# reversed ("esrever") readings of key tokens as a quick check
for w in ['matrixsumlist', 'lastwordsbeforearchichoice', 'thispassword', 'enter', 'yinyang', 'yellowblueprimes', 'causality', 'thematrixhasyou', 'btcseed', 'salphaseion', 'cosmicduality']:
    add(w[::-1], 'esrever')

# ---------- write main file ----------
seen = set(); lines = ['# lens web_osint — candidates from post-2024 public write-ups (GitHub puzzlehunt issues #51-#115, verknode/GSMR, floflo777, HosterjackAGV, jackdevs66, Naddiseo#13/#17, bitcointalk 5151725/5532424, Telegram quotes). tag after TAB is provenance.']
for c, tag in out:
    if c in seen: continue
    seen.add(c); lines.append(c)
open(WF + 'cands_lens_web_osint.txt', 'w').write('\n'.join(lines) + '\n')
open(WF + 'cands_lens_web_osint_tags.tsv', 'w').write('\n'.join(f'{c}\t{t}' for c, t in out) + '\n')
print('main candidates', len(seen))

# ---------- doors: lowercase alnum, one probe per line, deduped against _doors_seen.txt ----------
doors = ['bytenphase', 'byteandphase', 'bytenphasegbdoel4yjksvtml2ksdb', 'theproblemischoice', 'theproblemis', 'esrever', 'yinyang', 'yellowblueprimes', 'salvation', 'cosmicduality', 'dualite',
         'halfandbetterhalf', 'betterhalf', 'bellaciao', 'ciaobellao', 'ciaobella', 'anotherdoor', 'thirddoor', 'secondanswer', 'yourlastcommand', 'fourfirsthintisyourlastcommand', 'theone',
         'hashthetext', 'rabbitsnest', 'therabbitsnest', 'hushhush', 'warning', 'logic', 'digital', 'banking', 'cryptologic', 'digitallogic', 'bankingwar', 'youcan', 'merlon', 'nortonstheorem',
         'emperornorton', 'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist', 'btcseed', 'dbifhceg', 'dbifhcega', 'youdoit', 'andyoudoit', 'heartofkey', '1234d3f1',
         'reinsertingtheprimebasics', 'primebasics', 'theoryofeverything', 'xortriangle', 'causalitytranscended', 'thereisnospoon', 'theansweriswomen', 'salphaseion', 'anstoo', 'shabefanstoo',
         'yellowblueprimesmatrixsumlistlastwordsbeforearchichoiceyinyang', 'itsinfrontofyoureyesbutyourenotseeingit', 'wewontgiveawaythepassword', 'verylaststepisatruegiveaway',
         'thispassword', 'enter', 'matrixsumlist', 'lastwordsbeforearchichoice', 'whiterabbitseverywhere', 'followthewhiterabbit', 'theseedisplanted', 'causality', 'thematrixhasyou',
         xorkey(T1), 'a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735', '4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081', 'c3b87356f769b1a12acf2a76df3d7a5f1db595f07a5c0d4b5abdf731eab13ff5',
         s63.lower(), claimP.lower(), sp.lower()]
seen_doors = set()
for l in open(WF + '_doors_seen.txt', encoding='utf-8', errors='replace'):
    l = l.strip()
    if not l or l.startswith('#'): continue
    seen_doors.add(l); seen_doors.add(re.sub(r'[^a-z0-9]', '', l.lower()))
# also any door preimage already probed by other lens door files
import glob
for f in glob.glob(WF + 'cands_lens_*_doors*.txt'):
    if 'web_osint' in f: continue
    for l in open(f, encoding='utf-8', errors='replace'):
        l = l.strip()
        if l and not l.startswith('#'): seen_doors.add(l); seen_doors.add(re.sub(r'[^a-z0-9]', '', l.lower()))
new_doors = []
for d in doors:
    d2 = re.sub(r'[^a-z0-9]', '', d.lower())
    if d2 and d2 not in seen_doors and d2 not in new_doors: new_doors.append(d2)
print('door candidates new/unseen:', len(new_doors), 'of', len(doors))
open(WF + 'cands_lens_web_osint_doors.txt', 'w').write('# lens web_osint door preimages (gsmg.io/<sha256hex(line)>), lowercase-alnum, one probe per line, pre-deduped against _doors_seen.txt and other lens door files\n' + '\n'.join(new_doors[:40]) + '\n')
