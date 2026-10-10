import hashlib, itertools, re
C = []  # main candidates
def add(*xs):
    for x in xs:
        if x and x not in C: C.append(x)
S = 32
# 1. raw table forms
add("# X 2 S H 4 Y 0 Q B 15 #", "X 2 S H 4 Y 0 Q B 15", "X2SH4Y0QB15", "#X2SH4Y0QB15#", "x2sh4y0qb15", "XSHYQB", "SHQB", "QBHS", "X2SH", "x2sh", "Y0QB", "2SH4", "0QB15")
# 2. resolved forms for every value combination
for H, Q, B in itertools.product((42, -42), (82, 28), (25, -16, 16)):
    seq = [2, S, H, 4, 0, Q, B, 15]
    xs, ys = seq[:4], seq[4:]
    sp = " ".join(map(str, seq)); ns = "".join(map(str, seq))
    add(f"# X {xs[0]} {xs[1]} {xs[2]} {xs[3]} Y {ys[0]} {ys[1]} {ys[2]} {ys[3]} #",
        f"X {xs[0]} {xs[1]} {xs[2]} {xs[3]} Y {ys[0]} {ys[1]} {ys[2]} {ys[3]}",
        f"X{xs[0]}{xs[1]}{xs[2]}{xs[3]}Y{ys[0]}{ys[1]}{ys[2]}{ys[3]}",
        sp, ns, "".join(map(str, xs)), "".join(map(str, ys)), " ".join(map(str, xs)), " ".join(map(str, ys)),
        "".join(map(str, xs)) + " " + "".join(map(str, ys)),
        " ".join(f"{x},{y}" for x, y in zip(xs, ys)), ";".join(f"{x},{y}" for x, y in zip(xs, ys)),
        "".join(f"({x},{y})" for x, y in zip(xs, ys)), ",".join(f"({x},{y})" for x, y in zip(xs, ys)),
        " ".join(f"{y},{x}" for x, y in zip(xs, ys)), "".join(f"({y},{x})" for x, y in zip(xs, ys)),
        ns[::-1], " ".join(map(str, seq[::-1])), "".join(map(str, seq[::-1])),
        str(sum(xs)), str(sum(ys)), f"{sum(xs)}{sum(ys)}", f"{sum(xs)},{sum(ys)}", f"{sum(xs)} {sum(ys)}", str(sum(seq)),
        "".join(f"{v:02d}" for v in seq if v >= 0), "".join(f"{abs(v):02x}" for v in seq), "".join(f"{abs(v):02X}" for v in seq))
    for x, y in zip(xs, ys):
        add(f"{x},{y}", f"{y},{x}", f"{x} {y}", f"{x}{y}", f"({x},{y})", f"({y},{x})", f"x{x}y{y}", f"X{x}Y{y}", f"{x},{y},{x},{y}")
# 3. GPS (community) forms
gps = [
 "51°52'28.0\"N 4°24'23.2\"E", "51°52'28.0\"N4°24'23.2\"E", "51°52′28.0″N 4°24′23.2″E", "51°52'28\"N 4°24'23\"E",
 "51 52 28.0 N 4 24 23.2 E", "515228.0N42423.2E", "5152280N4242320E", "51522804242322", "515228042423 2", "51 52 28 0 4 24 23 2",
 "51.874444,4.406444", "51.874444, 4.406444", "51.874444 4.406444", "51.874444", "4.406444", "51.8744444,4.4064444", "51.87444,4.40644",
 "51.874444N 4.406444E", "N51 52 28.0 E4 24 23.2", "N51°52'28.0\" E4°24'23.2\"", "51°52'28.0\"N", "4°24'23.2\"E",
 "51d52m28.0sN 4d24m23.2sE", "5152280 4242320", "51 52 28 4 24 23", "515228 42423", "5152284 2423", "51522804242320",
 "SafeNet Technologies", "safenettechnologies", "SafeNet", "safenet", "SafeNet Technologies BV", "Safenet BV", "SafeNet Inc",
 "51°52'28.0\"N 4°24'23.2\"E SafeNet", "safenet51522804242322",
]
add(*gps)
# 4. chess readings
fr = lambda v: "abcdefgh"[v // 10 - 1] + str(v % 10) if 11 <= v <= 88 and 1 <= v % 10 <= 8 and 1 <= v // 10 <= 8 else None
rf = lambda v: "abcdefgh"[v % 10 - 1] + str(v // 10) if 11 <= v <= 88 and 1 <= v % 10 <= 8 and 1 <= v // 10 <= 8 else None
i0 = lambda v: "abcdefgh"[(v % 64) % 8] + str((v % 64) // 8 + 1)
i1 = lambda v: "abcdefgh"[((v - 1) % 64) % 8] + str(((v - 1) % 64) // 8 + 1)
for H, Q, B in itertools.product((42,), (82, 28), (25, 16)):
    seq = [2, S, H, 4, 0, Q, B, 15]
    two = [v for v in seq if v >= 10]
    for f in (fr, rf):
        sq = [f(v) for v in two if f(v)]
        add("".join(sq), " ".join(sq))
    for f in (i0, i1):
        sq = [f(v) for v in seq]; add("".join(sq), " ".join(sq))
        sq = [f(v) for v in seq if v < 64]; add("".join(sq))
add("c2d2h2b5a5", "c2 d2 h2 b5 a5", "b3b4b8e2e1", "Sh4", "Qb15", "Nh4", "Qb1", "Sh4Qb15", "2.Sh4 Qb1", "Nh4 Qb1", "c2d2h2b5a5b d", "SHQB->NQB", "NQB", "KNIGHTQUEENBISHOP", "knightqueenbishop",
    "B5KR/1r5B/2R5/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 b - - 0 1 c2d2h2b5a5", "b2c3d3d5a1h3c6b6")
# 5. value-derived words
add("Twofish", "twofish", "TWOFISH", "Blowfish", "blowfish", "qwertyuiop", "QWERTYUIOP", "Qwerty", "qwerty", "Swordfish", "swordfish", "wertyuiop",
    "Lynnfield", "i5-750", "i5750", "Core i5-750", "BV80605001911AP", "bv80605001911ap", "cha'", "vagh", "jav", "cha' vagh jav", "chavaghjav", "wejmaH cha'", "wejmaHcha'", "wejmaH cha", "wejmaHcha",
    "fortytwo", "forty-two", "42", "-42", "32", "82", "25", "-16", "16", "28", "Hitchhiker", "DontPanic", "Don't Panic", "dontpanic", "Thales", "Gemalto", "ThalesLuna", "SafenetLuna", "Luna HSM",
    "32 42 82 25", "32428225", "3242 8225", "S32H42Q82B25", "S32 H42 Q82 B25", "S=32 H=42 Q=82 B=25", "S32H-42Q82B-16", "S=32 B=25 H=42 Q=82", "S-32 B-25 H-42 Q-82", "32254282", "32,42,82,25", "25,42,32,82",
    "SHQB32428225", "X2324244Y0822515", "QBHS82254232", "82254232", "32 -42 82 -16", "3242 82-16", "32-428216", "324282-16", "32 -42 82 -16 2 4 0 15")
# 6. decentraland pairs
add("-41,-17", "-41-17", "-41 -17", "(-41,-17)", "-41,-16", "-42,-16", "-42-16", "(-42,-16)", "-17,-41", "-16,-42", "4,15", "15,4", "x4y15", "X4Y15", "x-42y-16", "X-42Y-16", "-42,-17", "-40,-16",
    "4117", "4216", "-4216", "41,17", "42,16", "gsmg.io magic puzzle piece", "GSMG.io Puzzle piece", "puzzlepiece", "-41,-17 -42,-16", "estate955", "955")
# 7. hex / key fragments (64-hex for bw_oracle's hex-as-key path)
def h64(n): return format(n, 'x').zfill(64)
for H, Q, B in itertools.product((42, -42), (82, 28), (25, -16)):
    seq = [2, S, H, 4, 0, Q, B, 15]
    ns = "".join(str(v) for v in seq)
    digs = re.sub(r'\D', '', ns)
    add(h64(int(digs)), h64(int(digs[::-1])), digs.zfill(64), digs[::-1].zfill(64), "".join(f"{abs(v):02x}" for v in seq).zfill(64),
        "".join(f"{v & 0xff:02x}" for v in seq).zfill(64), "".join(f"{abs(v):02x}" for v in seq) * 8)
add(h64(int("51522804242322")), "51522804242322".zfill(64), h64(51874444 * 10**6 + 4406444), h64(int("5152280") * 10**7 + int("4242320")), ("5152280" + "4242320").zfill(64))
open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_mr_robot_table.txt', 'w').write("\n".join(C) + "\n")
doors = ["X2SH4Y0QB15", "x2sh4y0qb15", "2324240822515", "232-424082-1615", "5152280424232", "51522804242322", "51°52'28.0\"N 4°24'23.2\"E", "51.874444,4.406444", "51.874444, 4.406444",
 "safenet", "SafeNet", "SafeNet Technologies", "safenettechnologies", "-42,-16", "-42-16", "4,15", "2,0", "32,82", "42,25", "twofish", "blowfish", "qwertyuiop", "qwerty", "wejmaHcha'",
 "232424 0822515", "2324240822515 51522804242322", "X232424Y0822515", "2 32 42 4 0 82 25 15", "2 32 -42 4 0 82 -16 15", "80122", "c2d2h2b5a5", "32428225", "S32H42Q82B25", "fortytwo", "Lynnfield", "BV80605001911AP",
 "-41,-17", "SHQB", "QBHS", "515228.0N42423.2E"]
open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_mr_robot_table_doors.txt', 'w').write("\n".join(doors) + "\n")
print("main", len(C), "doors", len(doors))
