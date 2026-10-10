import itertools, re, hashlib
old = set(l.rstrip('\n') for f in ('cands_lens_mr_robot_table.txt','cands_lens_mr_robot_table_2.txt','cands_lens_mr_robot_table_hash.txt') for l in open(f) if l.strip())
C = []
def add(*xs):
    for x in xs:
        if x and x not in C and x not in old: C.append(x)
# --- A. place-name strings from the reversed-table GPS reading (51°52'28.0"N 4°24'23.2"E -> Seattleweg 5, Pernis, Rotterdam 3195 ND)
place = ["Seattleweg", "seattleweg", "Seattleweg 5", "Seattleweg5", "seattleweg5", "Seattleweg 5 Pernis", "Seattleweg 5 Rotterdam", "Seattleweg 5, 3195 ND Rotterdam",
 "Seattleweg 5 3195 ND Rotterdam", "Seattleweg 5, Pernis, Rotterdam", "3195ND", "3195 ND", "3195", "Pernis", "pernis", "Pernis Rotterdam", "Rotterdam-Pernis", "Rotterdam Pernis", "Rotterdam", "rotterdam",
 "Zuid-Holland", "ZuidHolland", "Nederland", "Netherlands", "Seattle", "seattle", "Columbusstraat 25", "Columbusstraat25", "Columbusstraat", "3165 AC", "3165AC", "Albrandswaard", "Rotterdam-Albrandswaard",
 "SafeNet Technologies B.V.", "SafeNet Technologies BV", "Safenet Technologies B.v.", "SafeNet BV", "safenetbv", "Seattleweg 5, 3195 ND Rotterdam-Pernis", "seattleweg 5 pernis rotterdam",
 "Thales Rotterdam", "thalesrotterdam", "Gemalto Rotterdam", "Thales Nederland", "Thales DIS", "ThalesDIS", "Thales CPL", "thalescpl", "Hoofddorp", "Huizen", "Hengelo"]
add(*place)
# --- B. value variants incl. X=24, Y=25 (letter positions), S reversed 23, Q=28, B in {25,-16,16}, H in {42,-42}
vals = {'S': (32, 23), 'H': (42, -42, 24), 'Q': (82, 28), 'B': (25, -16, 16, 52, 61)}
seen_seq = set()
for S, H, Q, B in itertools.product(*vals.values()):
    seq = [2, S, H, 4, 0, Q, B, 15]
    xs, ys = seq[:4], seq[4:]
    t = tuple(seq)
    if t in seen_seq: continue
    seen_seq.add(t)
    j = lambda L, sep='': sep.join(map(str, L))
    add(j(seq), j(seq, ' '), j(seq, ','), j(xs) + j(ys), f"X{j(xs)}Y{j(ys)}", f"x{j(xs)}y{j(ys)}", f"#X{j(xs)}Y{j(ys)}#",
        f"24{j(xs)}25{j(ys)}", f"24 {j(xs,' ')} 25 {j(ys,' ')}", f"# 24 {j(xs,' ')} 25 {j(ys,' ')} #", f"24{j(xs)}25{j(ys)}".replace('-', ''),
        j(xs, ','), j(ys, ','), f"{j(xs, ',')};{j(ys, ',')}", f"({j(xs, ',')}),({j(ys, ',')})", f"[{j(xs, ',')}],[{j(ys, ',')}]",
        j(seq[::-1]), j(seq[::-1], ' '), j(seq)[::-1], j(seq, ' ')[::-1],
        " ".join(f"{x},{y}" for x, y in zip(xs, ys)), "".join(f"{x}{y}" for x, y in zip(xs, ys)), " ".join(f"{x}{y}" for x, y in zip(xs, ys)),
        "".join(f"{y}{x}" for x, y in zip(xs, ys)), "".join(f"{x},{y};" for x, y in zip(xs, ys)),
        str(sum(xs) * sum(ys)), str(sum(seq)), f"{sum(xs)}+{sum(ys)}", j([x + y for x, y in zip(xs, ys)]), j([x - y for x, y in zip(xs, ys)], ' '), j([x * y for x, y in zip(xs, ys)]),
        "".join(f"{abs(v):02d}" for v in seq), "".join(f"{v & 0xffff:04x}" for v in seq), "".join(f"{abs(v):02x}" for v in seq))
    # letter-position decode (a=1) and mod-26
    L = lambda v: chr(64 + v) if 1 <= v <= 26 else ''
    add("".join(L(v) for v in seq), "".join(chr(65 + (v % 26)) for v in seq), "".join(chr(97 + (v % 26)) for v in seq), "".join(chr(v) for v in seq if 32 <= v < 127))
# --- C. ordered pair strings from the full value set (decentraland-style)
V = [2, 4, 0, 15, 32, 42, -42, 82, 28, 25, -16, 16, 24, 23, 52, 51]
for a in V:
    for b in V:
        add(f"{a},{b}", f"{a} {b}", f"({a},{b})", f"{a}{b}")
# --- D. chess squares for Q in (82, 28), B in (25, 16), H 42
def sq_variants(v):
    out = {}
    if 0 <= v <= 63:
        out['fm0'] = "abcdefgh"[v % 8] + str(v // 8 + 1)      # file-major, 0-based (a1=0,b1=1)
        out['rm0'] = "abcdefgh"[v // 8] + str(v % 8 + 1)      # rank-major, 0-based (a1=0,a2=1)
    if 1 <= v <= 64:
        out['fm1'] = "abcdefgh"[(v - 1) % 8] + str((v - 1) // 8 + 1)
        out['rm1'] = "abcdefgh"[(v - 1) // 8] + str((v - 1) % 8 + 1)
    if 11 <= v <= 88 and 1 <= v % 10 <= 8 and 1 <= v // 10 <= 8:
        out['fr'] = "abcdefgh"[v // 10 - 1] + str(v % 10)
        out['rf'] = "abcdefgh"[v % 10 - 1] + str(v // 10)
    return out
for Q, B, H in itertools.product((82, 28), (25, 16), (42,)):
    seq = [2, 32, H, 4, 0, Q, B, 15]
    for key in ('fm0', 'rm0', 'fm1', 'rm1', 'fr', 'rf'):
        sq = [sq_variants(v).get(key) for v in seq]
        sq2 = [s for s in sq if s]
        add("".join(sq2), " ".join(sq2), "".join(sq2).upper(), "-".join(sq2))
        xs = [s for s in sq[:4] if s]; ys = [s for s in sq[4:] if s]
        add("".join(xs) + " " + "".join(ys), "".join(xs), "".join(ys))
# pairs (x,y) as (file,rank) with mod 8 / 1-based
for Q, B in itertools.product((82, 28), (25, 16)):
    xs, ys = [2, 32, 42, 4], [0, Q, B, 15]
    add("".join("abcdefgh"[x % 8] + str(y % 8 + 1) for x, y in zip(xs, ys)), "".join("abcdefgh"[(x - 1) % 8] + str((y - 1) % 8 + 1) for x, y in zip(xs, ys)),
        "".join("abcdefgh"[y % 8] + str(x % 8 + 1) for x, y in zip(xs, ys)))
# pieces: S=Springer(knight) H=hetman(Polish queen) Q B; German/Dutch piece letters
add("Sh4", "Sh4 Qb1", "2.Sh4", "Sh4Qb15", "X2 Sh4 Y0 Qb15", "x2sh4 y0qb15", "2 S h4 0 Q b1 5", "Nh4Qb1", "Nh4 Qb1 5", "Bb5", "Qb5", "Qb1", "0-0", "0-0-0", "Sh4 0-0 Qb1",
    "knight queen bishop", "springer dame laufer", "Springer", "springer", "Hetman", "hetman", "paard", "loper", "toren", "dame", "koning", "pion", "SpringerHetmanQueenBishop",
    "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1 2 32 42 4 0 82 25 15", "c6 e4", "c6e4", "Rc6 ke4", "c1a5c6e1a1e4b4h2", "c1 a5 c6 e1 a1 e4 b4 h2", "RkP", "c6e4h2", "c6 e4 h2")
# --- E. Mr Robot / HSM / PED specific strings tied to the riddle's defining text
mr = ["Qwerty", "qwerty82", "Qwerty82", "QWERTY82", "qwerty 82", "82qwerty", "Elliot's fish", "elliotsfish", "fish", "Fish", "swordfish", "Swordfish", "hackers", "Hackers", "swordless", "Swordless",
 "fsociety", "fsociety00.dat", "fsociety.dat", "mrrobot", "Mr. Robot", "MrRobot", "mr robot", "eps3.4_runtime-error.r00", "eps3.4", "runtime-error", "runtime-error.r00", "r00", "eps3.4_runtime-error.r00.", "runtimeerror",
 "ecorp", "E Corp", "EvilCorp", "evilcorp", "Evil Corp", "Phillip Price", "phillipprice", "Price", "whiterose", "Whiterose", "White Rose", "whiterosewhiterabbit", "Angela Moss", "angelamoss", "Angela", "angela",
 "Elliot Alderson", "elliotalderson", "Elliot", "elliot", "Darlene", "darlene", "Tyrell Wellick", "tyrellwellick", "Tyrell", "Dark Army", "darkarmy", "Deus Group", "deusgroup", "five nine", "fivenine", "5/9", "59",
 "hello friend", "hellofriend", "Hello, friend.", "Hello friend", "Washington Township", "washingtontownship", "eCoin", "ecoin", "E-Coin", "Allsafe", "allsafe", "Ron's Coffee", "ronscoffee", "Krista", "Mobley", "Trenton", "Romero",
 "Shayla", "Gideon", "Irving", "Dom DiPierro", "Sam Esmail", "samesmail", "Rami Malek", "ramimalek", "Mr. Robot S3E5", "s03e05", "S03E05", "3x05", "eps3.4", "Stage 2", "stage2", "Stage2", "Red Wheelbarrow", "redwheelbarrow",
 "Luna", "luna", "LUNA", "Luna HSM", "LunaHSM", "lunahsm", "SafeNet Luna", "safenetluna", "SafeNetLuna", "Luna SA", "LunaSA", "Luna SA 7000", "LunaSA7000", "Luna PED", "LunaPED", "lunaped", "PED", "ped", "PED key", "pedkey", "PEDkey", "PED keys",
 "magic keypad", "magickeypad", "magic keypads", "magickeypads", "daughters", "Daughters", "keypad", "Trusted Path", "trustedpath", "Trusted Path Authentication", "Gemalto", "gemalto", "Thales", "thales", "Thales Luna", "thalesluna",
 "Luna Network HSM", "lunanetworkhsm", "HSM", "hsm", "Hardware Security Module", "hardwaresecuritymodule", "SafeNet Luna HSM", "SafenetLunaHSM", "safenetlunahsm", "SafeNetLunaHSM", "Safenet Luna HSM 11110", "SafenetLunaHSM11110",
 "Luna PCI", "LunaPCI", "Luna G5", "LunaG5", "KeySecure", "keysecure", "ProtectServer", "protectserver", "HSM Luna", "hsmluna", "cloning domain", "red key", "blue key", "black key", "orange key", "redkey", "bluekey", "blackkey", "orangekey",
 "Security Officer", "securityofficer", "Crypto Officer", "cryptoofficer", "partition", "Partition", "11110", "Executive Order 11110", "EO11110", "eo11110", "keymaker", "Keymaker", "keymakers", "the keymaker", "thekeymaker",
 "ironic", "ironic name", "Phillip", "phillip", "valleys of Phillip", "valleysofphillip", "Price Valley", "Moon", "moon", "Luna moon", "lunamoon", "How so mate", "howsomate", "worst gear", "worstgear", "reverse", "Reverse", "REVERSE",
 "reverse gear", "reversegear", "on the highway", "highway", "Ok kid", "okkid", "kid", "Blowfish Twofish", "blowfishtwofish", "Threefish", "threefish", "Twofish Blowfish", "fish without sword", "fishwithoutsword",
 "the I and W are below", "I and W", "IW", "WI", "iw", "wi", "8 2", "2 8", "28", "I8W2", "W2I8", "i8w2", "cha vagh jav", "cha'vagh jav", "wa'maH cha'", "wejmaH cha'", "wejmaHcha'", "wejmaH", "loSmaH cha'", "loSmaHcha'",
 "Klingon", "klingon", "tlhIngan", "tlhingan", "Qapla'", "qapla", "Star Trek", "startrek", "StarTrek", "Hitchhiker's Guide", "hitchhikersguide", "hitchhikersguidetothegalaxy", "Deep Thought", "deepthought", "Douglas Adams", "douglasadams",
 "Lynnfield", "lynnfield", "i5", "i5-750", "Core i5", "corei5", "Intel", "intel", "Nehalem", "nehalem", "LGA1156", "lga1156", "8MB", "2.66GHz", "266", "45nm", "SLBLC", "slblc", "sqrt(-1)", "sqrt-1", "imaginary", "Imaginary", "4i", "-16i", "16i", "i",
 "(4i)^2", "(5)^2", "5i-i", "i5-i", "25", "-16", "16", "-42", "42", "82", "32", "28", "23", "24", "52", "61"]
add(*mr)
# --- F. numeric: GPS variants not in old file; decimal degrees w/ different precision; Decentraland land ids
gps = ["51.8744444", "4.4064444", "51.8744444,4.4064444", "51.8744444, 4.4064444", "51.874444 N 4.406444 E", "51.874444N4.406444E", "N51.874444 E4.406444", "51°52'28.0\"N, 4°24'23.2\"E",
 "51 52 28.0, 4 24 23.2", "51,52,28.0,4,24,23.2", "5152280,4242320", "515228.0,42423.2", "515228N0042423E", "515228N 0042423E", "5152N00424E", "51.8744,4.4064", "51.87444, 4.40644", "51.874444;4.406444",
 "4.406444,51.874444", "4.406444, 51.874444", "4°24'23.2\"E 51°52'28.0\"N", "4 24 23.2 E 51 52 28.0 N", "42423251522804", "424232 5152280", "4242320 5152280", "E4°24'23.2\" N51°52'28.0\"",
 "51.874444 4.406444 Seattleweg 5", "Seattleweg 5 51.874444 4.406444", "51°52'28.0\"N 4°24'23.2\"E Seattleweg 5", "geo:51.874444,4.406444", "51.874444,4.406444,0", "51°52'28\"N 4°24'23\"E",
 "51 52 28 N 4 24 23 E", "515228 N 042423 E", "N 51 52.467 E 4 24.387", "N51 52.467 E004 24.387", "51 52.467 4 24.387", "51.874444° N, 4.406444° E", "51.874444°N 4.406444°E",
 "u15p", "u15pk", "u15pkd", "u15pkdx", "u15pkdxy", "u15pkdxyq"]
add(*gps)
# --- G. Decentraland parcel / estate ids: LAND tokenId = (x<<128)|(y mod 2^128) for the four pairs + estate neighbours
def land_id(x, y):
    ux = x & ((1 << 128) - 1); uy = y & ((1 << 128) - 1)
    return (ux << 128) | uy
for x, y in [(-41, -17), (-41, -16), (-42, -16), (2, 0), (32, 82), (42, 25), (4, 15), (-42, -17)]:
    add(str(land_id(x, y)), hex(land_id(x, y)), hex(land_id(x, y))[2:], f"{x},{y}")
add("estate 955", "estate955", "Estate 955", "955", "0x959e104e1a4db6317fa58f8295f586e1a978c297", "0x959e104E1a4dB6317fA58F8295F586e1A978c297", "0x5D801b2B0B216790A49898b322246282547b546b", "0x5d801b2b0b216790a49898b322246282547b546b",
    "5D801b2B0B216790A49898b322246282547b546b", "5d801b2b0b216790a49898b322246282547b546b", "White Rabbits everywhere", "whiterabbitseverywhere", "white rabbits everywhere", "gsmg.io magic puzzle piece", "magic puzzle piece", "magicpuzzlepiece",
    "GSMG.io Puzzle piece", "gsmgiopuzzlepiece", "puzzlepiece.mp3", "sounds/puzzlepiece.mp3", "spawn1", "favicon_asset", "-41,-17 -41,-16", "-41,-16 -41,-17", "-41,-16", "-41,-17,-41,-16", "(-41,-17),(-41,-16)")
open('cands_lens_mr_robot_table_r2.txt', 'w').write("\n".join(C) + "\n")
# doors: new only
seen_doors = set(l.rstrip('\n') for l in open('_doors_seen.txt'))
doors = ["Seattleweg", "seattleweg", "Seattleweg 5", "Seattleweg5", "seattleweg5", "Pernis", "pernis", "3195ND", "3195 ND", "Rotterdam", "rotterdam", "Seattleweg 5, 3195 ND Rotterdam", "seattleweg5pernis",
 "2,32", "42,4", "0,82", "25,15", "-42,-17", "-41,-16", "24,25", "2324240822515", "2 32 42 4 0 82 25 15", "232424082-1615", "2 32 -42 4 0 82 -16 15", "X232424Y082-1615", "2324240822515" , "24232424250822515",
 "Qwerty", "qwerty82", "fsociety", "mrrobot", "luna", "Luna", "lunaped", "PED", "11110", "Elliot", "eps3.4_runtime-error.r00", "whiterose", "hetman", "c1a5c6e1a1e4b4h2", "c6e4h2", "Sh4Qb15", "Nh4Qb1", "2,0 32,82 42,25 4,15", "28", "82"]
doors = [d for d in dict.fromkeys(doors) if d not in seen_doors][:40]
open('cands_lens_mr_robot_table_doors_r2.txt', 'w').write("\n".join(doors) + "\n")
print("main", len(C), "doors", len(doors))
