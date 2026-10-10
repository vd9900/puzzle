#!/usr/bin/env python3
"""Lens creator_context: candidates derived from the creator's own wording/habits."""
import hashlib, re, itertools, sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from tools.gsmg import PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE, TARGET_ADDRESS
H = lambda s: hashlib.sha256(s.encode()).hexdigest()
C = []   # (hypothesis, candidate)
def add(h, *xs):
    for x in xs:
        if x: C.append((h, x))

LYRIC = "theflowerblossomsthroughwhatseemstobeaconcretesurface"
PHASE2_URL = "choiceisanillusioncreatedbetweenthosewithpowerandthosewithoutaveryspecialdessertiwroteitmyself"
SALPH_HASH = "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32"
APR2019_HASH = "5ac407837447fba24ba2802e4d1e9aecb4580aa29fef1088cc387c180b746f75"
HINT_LINES = ["Roses are White but often Red.", "Yellow has a number and so does Blue.",
              "Go back to the first puzzle piece without further ado.",
              "It might have shown you only one door, beware that the rabbits nest may contain a whole lot more.",
              "Hush hush.", "Good luck"]
HINT_FULL = "\n".join(HINT_LINES[:5])

# ---------- H1: "our first hint" literal texts ----------
for l in HINT_LINES: add('H1', l, l.rstrip('.'), re.sub(r'[^a-z]', '', l.lower()))
add('H1', HINT_FULL, HINT_FULL + "\n", " ".join(HINT_LINES[:5]), "".join(HINT_LINES[:5]),
    re.sub(r'[^a-z]', '', HINT_FULL.lower()), "\n".join(HINT_LINES[:3]), " ".join(HINT_LINES[:3]),
    re.sub(r'[^a-z]', '', " ".join(HINT_LINES[:3]).lower()), "\n".join(HINT_LINES[:2]),
    re.sub(r'[^a-z]', '', " ".join(HINT_LINES[:2]).lower()), HINT_LINES[0] + "\n" + HINT_LINES[1],
    "Roses are White but often Red. Yellow has a number and so does Blue.",
    "rosesarewhitebutoftenred", "rosesarewhite", "oftenred", "yellowhasanumberandsodoesblue",
    "withoutfurtherado", "furtherado", "ado", "therabbitsnest", "rabbitsnest", "rabbitnest", "awholelotmore",
    "onedoor", "onlyonedoor", "itmighthaveshownyouonlyonedoor", "bewarethattherabbitsnestmaycontainawholelotmore",
    "Follow the white rabbit", "followthewhiterabbit", "follow_the_white_rabbit", "follow_the_white_rabbit.png",
    "GSMG MEGANIGMA || 5 BTC", "MEGANIGMA", "meganigma", "whiterabbit", "white rabbit", "thewhiterabbit",
    "giveit = givetit", "giveit=givetit", "givetit", "giveit", "t", "givetit=giveit",
    APR2019_HASH, APR2019_HASH.upper(), "just try hit your options against that hash",
    "HASHTHETEXT", "hashthetext", "hash the text", "hashthetext1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe",
    "White Rabbits everywhere", "gsmg.io magic puzzle piece", "magicpuzzlepiece",
    "theseedisplanted", "the seed is planted", "gsmg.io/theseedisplanted", "https://gsmg.io/theseedisplanted",
    "ourfirsthint", "our first hint", "firsthint", "first hint", "thefirsthint", "hint", "tinyhint",
    "ourfirsthintisyourlastcommand", "our first hint is your last command", "yourlastcommand", "lastcommand",
    "shabefourfirsthintisyourlastcommand", "shabef our first hint is your last command",
    "fourfirsthintisyourlastcommand", "four first hint is your last command", "sha256ourfirsthintisyourlastcommand")

# ---------- H2: "your last command" readings ----------
add('H2', "enter", "ENTER", "Enter", "\n", "\r\n", "return", "RETURN", "pressenter", "press enter", "enter.", "[enter]", "<enter>",
    "last", "exit", "quit", "logout", "halt", "shutdown", "history", "sudo", "sha256sum", "sha256", "shabef", "SHABEF",
    "openssl", "openssl enc -aes-256-cbc -a -d", "openssl enc -aes-256-cbc -d -a", "openssl enc -d -aes-256-cbc -a",
    "echo", "cat", "ls", "cd", "pwd", "whoami", "clear", "reboot", "poweroff", "end", "stop", "run", "go", "execute",
    "command", "yourlastcommand", "mylastcommand", "thelastcommand", "lastcommandisenter",
    SALPH_HASH, SALPH_HASH.upper(), "gsmg.io/" + SALPH_HASH, "https://gsmg.io/" + SALPH_HASH, "/" + SALPH_HASH,
    "GET /" + SALPH_HASH, "GET /" + SALPH_HASH + " HTTP/1.1",
    SALPHASEION_PREIMAGE, PHASE32_PREIMAGE, PHASE3_PREIMAGE, "causality", LYRIC, PHASE2_URL,
    "phase1verification", "/phase1verification", "POST /phase1verification", "password=" + LYRIC,
    "averyspecialdessertiwroteitmyself", "a very special dessert i wrote it myself", "dessert", "adessert", "thedessert",
    "cake", "thecake", "thecakeisalie", "scriptedcake", "scripted cake", "anybodyhungry", "noitsadessert",
    "thisisthewarning", "this is the warning", "theredroseortheblack", "redroseorblackrose", "redroseorblackrosenoinbetween",
    "theredroseortheblackredroseorblackrosenoinbetweenthisisthewarning", "ifitweretofalluponyoutodaywhichflowerwouldyoube",
    "the warning", "thewarning", "logic", "logicthewarning", "thejudgement", "judgement", "phasethree", "phase three")
# "ans too" as: hash the previous answer again (double/triple sha256 of every stage password)
STAGES = ["theseedisplanted", LYRIC, "causality", "SafenetLunaHSM11110", PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE,
          "GSMGIO5BTCPUZZLECHALLENGE", TARGET_ADDRESS, "HASHTHETEXT", "lastwordsbeforearchichoice", "thispassword", "matrixsumlist", "enter"]
for s in STAGES:
    add('H2', H(s), H(H(s)), H(s).upper(), H(s) + "\n")

# ---------- H3: "ans too" ----------
add('H3', "ans", "Ans", "ANS", "anstoo", "ans too", "Ans too", "answer", "Answer", "answertoo", "answer too", "theanswer", "the answer",
    "theanswertoo", "shabefanstoo", "shabef ans too", "sha256anstoo", "sha256 ans too", "sha256answertoo", "sha256(ans)", "sha256(answer)",
    "ans2", "answer2", "anstwo", "too", "also", "ook", "antwoord", "antwoordook", "antwoord ook", "hetantwoord", "het antwoord",
    "42", "fortytwo", "forty two", "-42", "42*-1", "theanswertolifetheuniverseandeverything", "lifetheuniverseandeverything",
    "theanswertoeverything", "answertoeverything", "theultimatequestion", "dontpanic", "douglasadams", "hitchhikersguide",
    "theoryofeverything", "thetheoryofeverything", "theory of everything", "toe", "everything", "theeverything",
    "theanswertoonlythispuzzlebutnothingelse", "answertoonlythispuzzlebutnothingelse", "ans_too", "ans-too", "anstoo.")

# ---------- H4: creator's typos / Dutch-English ----------
add('H4', "givetit", "beleive", "doyoubeleivemeyouneedit", "do you beleive me you need it?", "throphies", "waisting", "founded", "sqaures",
    "sqauresandarabbit", "squaresandarabbit", "squares and a rabbit", "strugle", "unforseen", "focussing", "ofcourse", "esthetician",
    "unsolvalble", "reaced", "talkinig", "dosis", "parc", "obstacleparc", "soulve", "salphation", "salphasion", "salphaseion", "SalPhaseIon",
    "salvation", "Salvation", "salvationphase", "phasesalvation", "sal phase ion", "salphase", "price", "theprice", "mainprice", "the main price",
    "priceisinhalf", "thepriceisinhalf", "the price is in half", "halfprice", "halvingtheprice", "worthlesspricesandthrophies",
    "hundredfourty", "hundred fourty", "fourty", "ancientspelling", "ancient spelling", "typo", "typos", "oneofthemanymanytypos",
    # Dutch renderings
    "prijs", "deprijs", "hoofdprijs", "sleutel", "desleutel", "privesleutel", "privésleutel", "geheimesleutel", "deur", "dedeur", "anderedeur",
    "erisnogeendeur", "er is nog een deur", "nogeendeur", "konijn", "witkonijn", "wittekonijn", "hetwittekonijn", "volghetwittekonijn",
    "volg het witte konijn", "konijnenhol", "hethol", "nest", "konijnennest", "hetzaadisgeplant", "het zaad is geplant", "zaad",
    "oorzakelijkheid", "causaliteit", "keuze", "dekeuze", "keus", "bron", "debron", "verlossing", "zaligheid", "redding", "bevrijding",
    "wederhelft", "mijnwederhelft", "mijn wederhelft", "helft", "beterehelft", "betere helft", "dehelft", "helftenbeterehelft",
    "geheim", "hetgeheim", "wachtwoord", "hetwachtwoord", "ditwachtwoord", "dit wachtwoord", "hint", "eerstehint", "onzeeerstehint",
    "laatstecommando", "laatsteopdracht", "laatstebevel", "onzeeerstehintisjelaatstecommando", "onze eerste hint is je laatste commando",
    "onzeeerstehintisuwlaatstecommando", "invoeren", "toetsenter", "drukopenter", "yinyang", "jinjang", "priemgetallen", "priemgetal",
    "priem", "matrix", "som", "somlijst", "lijst", "geel", "blauw", "geelblauw", "geelenblauw", "wit", "rood", "zwart", "roos", "rozen",
    "rozenzijnwit", "rozen zijn wit maar vaak rood", "stil", "sst", "ssst", "stilstil", "mondjedicht", "succes", "veelsucces", "veel succes",
    "goedzo", "goedgedaan", "goed gedaan", "gefeliciteerd", "proficiat", "hoi", "hallo", "hallovriend", "hallo vriend", "vriend", "vrienden",
    "goedevrienden", "mijnvrienden", "beste vrienden", "bestevrienden", "zowat", "zo wat", "sowut", "SoWut", "so wut", "so what", "sowhat",
    "jrkbgrt", "Jrk Bgrt", "jrk", "bgrt", "nederland", "holland", "dutch", "nl", "frankrijk", "france", "wortel", "wortels", "oranje",
    "carrotswereoriginallypurple", "purplecarrot", "paarsewortel")

# ---------- H5: acrostics / numeric jokes ----------
add('H5', "DOOR", "door", "Door", "thereisanotherdoor", "There is Another DOOR", "thereisanother", "anotherdoor", "another door", "anotherdoormightbefoundon",
    "RAB", "rab", "R=18 A=1 B=2", "r18a1b2", "18 1 2", "1812", "18,1,2", "21", "1812bit", "21bit", "rabbit", "RABBIT", "Rabbit", "rabbits",
    "{1},{4},{21}", "{1 },{4} ,{21}", "1,4,21", "1 4 21", "1421", "14 21", "adu", "ADU", "a d u", "uda", "1-4-21", "one four twentyone", "onefourtwentyone",
    "1357", "1357blockstogo", "1357 blocks to go", "13 5 7", "1,3,5,7", "0", "1", "01", "10", "firstorzero", "first or zero", "zero", "first", "zeroorfirst",
    "first or zero.", "FirstOrZero", "infrared", "Infrared", "INFRARED", "ir", "backstage", "thebackstage", "the backstage", "andoen", "And Oen", "oen", "Oen",
    "eon", "noe", "one", "neo", "One", "Neo", "NEO", "ONE", "andone", "and one", "oneforonefourforone", "one for one, four for one", "One for one, four for one.",
    "humph", "Humph", "hushhush", "hush hush", "Hush hush", "Hush hush.", "hush", "nohints", "no hints", "No hints", "nobodyknows", "nobody knows", "Nobody knows",
    "nohintsonlyfreewill", "no hints, only free will", "onlyfreewill", "freewill", "free will", "sevenparts", "7parts", "7 parts", "7 parts right?",
    "sevenintertwinedpasswords", "seven intertwined passwords", "twentythreeciphers", "sixteenencryptions", "only-41,-17matters", "-41,-17", "4117", "-41-17",
    "955", "estate955", "ciao", "Ciao!", "ciaobella", "ciao bella", "ciaobellao", "ciao bella o", "hat off", "hatoff", "myhatofftoyou", "youknowifyouknow",
    "you know if you know", "thepuzzletalksforme", "the puzzle talks for me", "ying yang", "yingyang", "yin yang", "yinyang", "yin-yang", "ying-yang",
    "yinandyang", "yingandyang", "taichi", "taijitu", "tao", "dao", "thedao", "DAO", "seal of 01", "sealof01")
# index picks from first hint / lyric with the creator's numbers
hint_words = re.findall(r"[A-Za-z]+", " ".join(HINT_LINES[:5]))
hint_letters = re.sub(r'[^a-z]', '', " ".join(HINT_LINES[:5]).lower())
def pick_words(ws, idx): return "".join(ws[i-1] for i in idx if 0 < i <= len(ws))
def pick_letters(s, idx): return "".join(s[i-1] for i in idx if 0 < i <= len(s))
for idx in ([1,4,21], [18,1,2], [1,8,1,2], [2,1], [1,3,5,7], [21,4,1]):
    add('H5', pick_words(hint_words, idx), pick_words(hint_words, idx).lower(), pick_letters(hint_letters, idx), pick_letters(LYRIC, idx),
        pick_letters("theseedisplanted", idx), pick_words(LYRIC and "the flower blossoms through what seems to be a concrete surface".split(), idx))
primes = [p for p in range(2, 200) if all(p % q for q in range(2, int(p**0.5)+1))]
add('H5', pick_letters(hint_letters, primes), pick_letters(LYRIC, primes), "".join(hint_words[p-1] for p in primes if p <= len(hint_words)))
# first letters of hint lines / words (acrostic habit)
add('H5', "".join(l[0] for l in HINT_LINES[:5]), "".join(w[0] for w in hint_words), "".join(w[0] for w in hint_words).lower(),
    "".join(l.split()[-1].strip('.') for l in HINT_LINES[:5]), "".join(l.split()[-1].strip('.') for l in HINT_LINES[:5]).lower())

# ---------- H6: 2026-01-01 hint ----------
NY = 'Happy new year! Make the best of everything. Oh, and here\'s a "tiny hint" <3.'
add('H6', NY, NY.rstrip('.'), re.sub(r'[^a-z0-9]', '', NY.lower()), "Happy new year!", "happynewyear", "Happy new year", "Make the best of everything.",
    "makethebestofeverything", "make the best of everything", "thebestofeverything", "bestofeverything", "best of everything", "thebest", "best",
    "Oh, and here's a \"tiny hint\" <3.", "here's a \"tiny hint\"", "tiny hint", "tinyhint", "\"tiny hint\"", "a tiny hint", "atinyhint", "tiny", "<3", "<3.",
    "heart", "love", "Love", "LOVE", "liefde", "hart", "lessthan3", "lessthanthree", "less than 3", "3", "<", "tinyfraction", "tiny fraction", "atinyfraction",
    ".", "..", "...", "....", ".....", ". .. ... .... .....", "...............", "12345", "1 2 3 4 5", "15", "5", "EISH5", "eish5", "eish", "E I S H 5",
    "countdown", "midnight", "2026", "newyear", "happy", "everything", "Everything", "best of", "makethebest", "make the best")

# ---------- H7: 2026-07-12 "close friends" + creator self-descriptors (public only) ----------
add('H7', "My close friends have the best chance of solving it", "myclosefriendshavethebestchanceofsolvingit", "closefriends", "close friends", "myclosefriends",
    "my close friends", "friends", "friend", "bestfriends", "best friends", "friendsandfamily", "friends and family", "family", "myfamily", "familyandfriends",
    "theydonthavetheskills", "skills", "noteThatisahint", "thatisahint", "that is a hint", "NOTE: that is a hint.", "hellofriend", "Hello, friend.", "hello friend",
    "Hello friend", "hello, friend", "helloelliot", "Hello, Elliot.", "hello elliot", "elliot", "Elliot", "mrrobot", "mr robot", "mr. robot", "fsociety", "FSOCIETY",
    "thelastsceneofmrrobot", "last scene of mr robot", "eps3.5_kill-process.inc", "eps3.4_runtime-error.r00", "eps3.5", "kill-process", "killprocess", "episode3.5",
    "episode 3.5", "whiterose", "white rose", "darlene", "angela", "tyrell", "ecorp", "evilcorp", "stage3", "stage 3", "stage2", "5/9", "fiveninehack",
    "Globally supporting my generation", "globallysupportingmygeneration", "Globally Supporting My Generation", "GLOBALLYSUPPORTINGMYGENERATION", "gsmg", "GSMG",
    "gsmg.io", "GSMG.io", "GSMG.IO", "gsmgio", "GSMGIO", "gsmgpuzzle", "GSMG Puzzle", "gsmg puzzle", "GSMG puzzle", "GSMGIO5BTCPUZZLECHALLENGE", "gsmgio5btcpuzzlechallenge",
    "GSMG.IO 5 BTC PUZZLE CHALLENGE", "5btcpuzzlechallenge", "5 BTC PUZZLE CHALLENGE", "betterhalf", "better half", "thebetterhalf", "the better half", "half",
    "halfandbetterhalf", "half and better half", "halfandbetterhalfandtheyalsoneedfundstolive", "theyalsoneedfundstolive", "fundstolive", "littleones", "little ones",
    "mylittleones", "kids", "children", "sowut", "SoWut", "SOWUT", "so wut", "So wut", "sowhat", "so what", "jrkbgrt", "Jrk Bgrt", "JrkBgrt", "jrk", "Jrk", "bgrt",
    "Bgrt", "jerkbogart", "jurkbogaert", "admin", "Admin", "jacquefresco", "Jacque Fresco", "jacque fresco", "jacque", "fresco", "thevenusproject", "venusproject",
    "the venus project", "resourcebasedeconomy", "resource based economy", "thezeitgeistmovement", "zeitgeist", "thebestthatmoneycantbuy", "the best that money can't buy",
    "touchgrass", "touch grass", "stacksats", "stack sats", "enjoylife", "enjoy life", "behappy", "happiness", "Happiness", "staysafe", "begood", "stayhealthy",
    "hope", "Hope", "HOPE", "hopeisthequintessentialhumandelusion", "superposition", "superpositions", "Iprefersuperpositions", "i prefer superpositions",
    "sqrt(-1)", "sqrt-1", "i", "imaginary", "imaginarypuzzle", "an imaginary puzzle", "ascii127", "ASCII 127", "127", "del", "DEL", "\x7f", "purplepill", "purple pill",
    "thepurplepill", "candyflipping", "candy flipping", "psilocybeazurescens", "psilocybe azurescens", "5-MeO-DMT", "5meodmt", "mescaline", "nad", "NAD", "blueprint",
    "Blueprint", "bryanjohnson", "dontdie", "don't die", "2145", "year2145", "18years", "underinvestigation", "under investigation", "regularbitcoinprivatekey",
    "Regular Bitcoin Private key", "regular bitcoin private key", "aprivatekey", "a private key", "privatekey", "private key", "theprivatekey", "the private key",
    "obscureintel", "obscure intel", "'obscure' intel", "intel", "someobscureintel", "thesecret", "secret", "asecret", "quiteasecret", "quite a secret",
    "iheldquiteasecretinmyhead", "sharewiththeplanet", "theplanet", "planet", "forthosewhocanunderstandwhatimeant", "areyoureallylookingforjustthebtc",
    "Are you really looking for just the btc...?", "justthebtc", "notjustthebtc", "thekey", "the key", "key", "thetruth", "truth", "freedom", "knowledge",
    "enlightenment", "thesource", "the source", "source", "sourcecode", "sourcecodes", "source codes", "thesourcecodes", "returntothesource", "return to the source",
    "thehardestpartisdone", "the hardest part is done", "hardestpart", "youhavealltheinfo", "you have all the info", "nohintsonlyfreewill", "freewill",
    "holdontobitcoin", "hold on to bitcoin", "hodl", "HODL", "hodlbitcoin", "bitcoin", "Bitcoin", "btc", "BTC", "satoshi", "satoshinakamoto", "Satoshi Nakamoto",
    "happyhalving", "happy halving", "halving", "thehalving", "nexthalving", "840000", "630000", "1050000", "209999", "210000", "16$fee", "16$ fee. Damn.",
    "seeyouin4years", "see you in 4 years", "theblockchain", "youonlyneedthelastnumberofpi", "thelastnumberofpi", "lastnumberofpi", "pi", "3.14", "314159",
    "artificialstars", "artificial stars", "chillingunderartificialstars", "clearingupdisks", "matthew", "roberto", "pimeyes", "festival", "lowlands",
    "caribbean", "Caribbean", "holiday", "onholiday", "trollingmood", "trolling", "troll", "jeremy", "Jeremy", "cartman", "chatroulette", "rustserver", "rust",
    "pvpzone", "gnomad", "bingo", "Bingo", "BINGO", "cyberpunk", "cyberpunk2077", "V", "v", "goodonev", "good one v", "thegame", "ewout", "Ewout", "EwoutM",
    "aprilfools", "april fools", "aprilfool", "1april", "april1", "firstofapril", "first of april", "whatusuallyhappensonthefirstofapril", "kirikaze")

# ---------- H8: creator's concatenation habit (Phase-3 style preimage) ----------
CHAIN = ["theseedisplanted", LYRIC, "causality", "SafenetLunaHSM11110", PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE]
SEVEN = ["theseedisplanted", LYRIC, "causality", "SafenetLunaHSM11110", PHASE3_PREIMAGE, PHASE32_PREIMAGE, SALPHASEION_PREIMAGE]
for i in range(len(CHAIN)):
    for j in range(i+1, len(CHAIN)+1):
        if j - i < 2: continue
        seg = CHAIN[i:j]
        for sep in ("", " ", "\n", "|", "+", ","):
            add('H8', sep.join(seg))
        add('H8', "".join(H(s) for s in seg), "".join(H(s) for s in seg).upper(), " ".join(H(s) for s in seg))
# reversed-order chains ("our first hint is your last command": last becomes first)
add('H8', "".join(reversed(CHAIN)), "".join(H(s) for s in reversed(CHAIN)), "".join(s[::-1] for s in CHAIN), "".join(CHAIN)[::-1])
# half and better half: first/second halves of the chain
full = "".join(CHAIN)
add('H8', full[:len(full)//2], full[len(full)//2:], full[len(full)//2:] + full[:len(full)//2])
# interleavings (intertwined) of the two preimage passwords and of yin/yang halves
def twine(a, b): return "".join(x + y for x, y in itertools.zip_longest(a, b, fillvalue=""))
add('H8', twine("half", "betterhalf"), twine("yin", "yang"), twine("causality", "givetit"), twine(PHASE32_PREIMAGE, SALPHASEION_PREIMAGE),
    twine(SALPHASEION_PREIMAGE, PHASE32_PREIMAGE), twine("lastwordsbeforearchichoice", "thispassword"), twine("yellow", "blue"), twine("blue", "yellow"),
    twine(LYRIC, "causality"), twine("theseedisplanted", LYRIC))

# dedupe preserving order
seen = set(); out = []
for h, x in C:
    if x in seen: continue
    seen.add(x); out.append((h, x))
import json
multi = [x for h, x in out if ('\n' in x or '\r' in x)]
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_creator_context.txt', 'w') as f:
    f.write("# lens creator_context: one candidate per line; newline-containing candidates live in cands_lens_creator_context_multiline.json\n")
    for h, x in out:
        if x in multi: continue
        f.write(x + '\n')
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_creator_context_multiline.json', 'w') as f:
    json.dump(multi, f)
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_creator_context_hyp.tsv', 'w') as f:
    for h, x in out: f.write(h + '\t' + x.replace('\n', '\\n').replace('\r', '\\r') + '\n')
from collections import Counter
print("total unique:", len(out), "multiline:", len(multi), Counter(h for h, x in out))

# ---------- H9: door preimages (lowercase-alnum so oracle's 3 forms collapse to 1 probe) ----------
seen_doors = set()
for l in open('/home/vin/bitcoin_puzzle/scratch/wf/_doors_seen.txt', encoding='utf-8', errors='replace'):
    l = l.rstrip('\n')
    if l.startswith('#') or not l: continue
    seen_doors.add(l); seen_doors.add(re.sub(r'[^A-Za-z0-9]', '', l)); seen_doors.add(re.sub(r'[^a-z0-9]', '', l.lower()))
DOORS = ['yourlastcommand', 'ans', 'answer', 'answertoo', '42', 'givetit', 'wederhelft', 'hellofriend', 'closefriends', 'myclosefriends', 'tinyhint', 'makethebestofeverything', 'happynewyear', 'salphation', 'backstage', 'andoen', 'rab', '1421', 'adu', 'rabbitsnest', 'therabbitsnest', 'gobacktothefirstpuzzlepiecewithoutfurtherado', 'sowut', 'jrkbgrt', 'obscureintel', 'secret', 'sqauresandarabbit', 'squaresandarabbit', 'nobodyknows', 'nohints', 'ciaobella', 'theprimepart', 'primepart', 'zeroedout', 'ancientspelling', 'hundredfourty', 'meganigma', 'gsmgmeganigma5btc', 'phase32', 'salphaseion2'] + ["ourfirsthintisyourlastcommand", "yourlastcommand", "shabefourfirsthintisyourlastcommand", "ans", "answer", "answertoo", "shabefanstoo", "42",
         "givetit", "giveitgivetit", "wederhelft", "hellofriend", "closefriends", "myclosefriends", "friends", "tinyhint", "makethebestofeverything", "happynewyear",
         "salphation", "salvation", "thesource", "source", "backstage", "thebackstage", "andoen", "rab", "1812", "1421", "adu", "thereisanotherdoor", "rabbit",
         "rabbitsnest", "therabbitsnest", "whiterabbit", "gobacktothefirstpuzzlepiecewithoutfurtherado", "rosesarewhitebutoftenred",
         "yellowhasanumberandsodoesblue", "theoryofeverything", "sowut", "jrkbgrt", "regularbitcoinprivatekey", "obscureintel", "secret", "sqauresandarabbit",
         "squaresandarabbit", "yingyang", "yinyang", "matrixsumlist", "thispassword", "lastwordsbeforearchichoice", "cosmicduality", "enter", "anstoo",
         "theseedisplanted", "followthewhiterabbit", "hushhush", "door", "anotherdoor", "globallysupportingmygeneration", "firstorzero", "infrared",
         "nobodyknows", "nohints", "oneforonefourforone", "humph", "hope", "ciaobella", "betterhalf", "halfandbetterhalf", "wewontgiveawaythepassword",
         "itsinfrontofyoureyesbutyourenotseeingit", "verylaststepisatruegiveawaypromised", "yellowblueprimes", "primes", "prime", "theprimepart", "primepart",
         "zeroedout", "zeroed", "ancientspelling", "hundredfourty", "meganigma", "gsmgmeganigma5btc", "puzzle", "phase4", "phase32", "salphaseion2", "yinyangphase",
         "cosmic", "duality", "lifeanddeath", "thetruth", "freedom", "hodl", "satoshi", "thekey", "privatekey", "aprivatekey", "elliot", "mrrobot", "fsociety",
         "whiterose", "jacquefresco", "venusproject", "thevenusproject", "freewill", "superposition", "superpositions", "ascii127", "purplepill", "pi",
         "hash", "sha256", "shabef", "thesecret", "quiteasecret", "theplanet", "notjustthebtc", "areyoureallylookingforjustthebtc", "thehardestpartisdone",
         "youhavealltheinfo", "onlyfreewill", "sevenintertwinedpasswords", "twentythreeciphers", "sixteenencryptions", "bruteforce", "hint", "hints",
         "firsthint", "ourfirsthint", "lasthint", "thelasthint", "tinyfraction", "ourfirsthintisyourlastcommandshabefanstoo", "lastwordsbeforearchichoicethispassword"]
dnew = []
for d in DOORS:
    if d in seen_doors or d in dnew: continue
    dnew.append(d)
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_creator_context_doors.txt', 'w') as f:
    f.write("# lens creator_context door preimages (gsmg.io/<sha256hex(line)>), lowercase-alnum so each line = 1 probe; first 40 probed\n")
    for d in dnew: f.write(d + '\n')
print("door preimages new (not in _doors_seen):", len(dnew), "of", len(DOORS)); print(dnew[:45])
