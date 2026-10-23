"""Quick deterministic checks of chat claims (chunk1). Reads repo puzzle image only."""
import sys, random, json
sys.path.insert(0, "/home/vin/bitcoin_puzzle")
from tools.gsmg import extract_grid, spiral_coordinates, SOURCES

g = extract_grid(SOURCES / "gsmg-puzzle.png")
M, C = g["matrix"], g["colors"]
out = {"decoded": g["decoded"], "trailing_bits": g["trailing_bits"]}
fe = g["near_white_cells_zero_based"]
sp = spiral_coordinates(14)
out["fe_cells"] = fe
out["fe_rowmajor_idx0"] = [r * 14 + c for r, c in fe]
out["fe_spiral_idx0"] = [sp.index((r, c)) for r, c in fe]
out["ones_total"] = sum(map(sum, M))
# Diego: drop FE row/col -> 13x13 sums
r0, c0 = fe[0]
sub = [[M[r][c] for c in range(14) if c != c0] for r in range(14) if r != r0]
out["sub13_sum"] = sum(map(sum, sub))
out["sub13_rows"] = [sum(r) for r in sub]
out["sub13_cols"] = [sum(sub[r][c] for r in range(13)) for c in range(13)]
out["diego_rows_match"] = out["sub13_rows"] == [6,10,7,6,6,5,4,8,8,7,8,6,8]
out["diego_cols_match"] = out["sub13_cols"] == [7,9,7,10,7,3,6,7,5,8,6,6,8]
# colour counts
cells = {k: [(r, c) for r in range(14) for c in range(14) if C[r][c] == k] for k in ("yellow", "blue", "near_white")}
out["n_yellow"], out["n_blue"] = len(cells["yellow"]), len(cells["blue"])
# Denis: coloured cells form a turning grille (disjoint under 4 rotations)
def rot(rc): r, c = rc; return (c, 13 - r)
def grille_ok(S):
    seen, S = set(), set(S)
    for _ in range(4):
        if seen & S: return False
        seen |= S; S = {rot(x) for x in S}
    return True
col = cells["yellow"] + cells["blue"]
out["grille_yb"] = grille_ok(col)
out["grille_yb_fe"] = grille_ok(col + cells["near_white"])
allc = [(r, c) for r in range(14) for c in range(14)]
random.seed(1); N = 200000
hits = sum(grille_ok(random.sample(allc, len(col))) for _ in range(N))
out["grille_random_rate"] = hits / N
# GF(2) rank (original, and FE cell flipped to 1)
def rank2(rows):
    rows = [int("".join(map(str, r)), 2) for r in rows]; rk = 0
    for bit in reversed(range(14)):
        piv = next((i for i in range(rk, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None: continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        for i in range(len(rows)):
            if i != rk and rows[i] >> bit & 1: rows[i] ^= rows[rk]
        rk += 1
    return rk
out["gf2_rank"] = rank2(M)
M2 = [row[:] for row in M]; M2[r0][c0] = 1
out["gf2_rank_fe_flipped"] = rank2(M2)
# Diego: chars of decoded URL at yellow positions / prime-ASCII chars
url = g["decoded"]
yel_idx = sorted(sp.index(x) for x in cells["yellow"]); blu_idx = sorted(sp.index(x) for x in cells["blue"])
out["yellow_spiral_idx"] = yel_idx; out["blue_spiral_idx"] = blu_idx
out["url_chars_at_yellow_bytes"] = "".join(url[i // 8] for i in yel_idx if i < 192)
isp = lambda n: n > 1 and all(n % d for d in range(2, int(n ** .5) + 1))
out["url_prime_ascii_chars"] = "".join(ch for ch in url if isp(ord(ch)))
# string-length claims
instr = "matrixsumlistlastwordsbeforearchichoicethispasswordshabefourfirsthintisyourlastcommandentershabefanstoo"
out["salph_instr_len"] = len(instr)
out["lwbac_thispassword_len"] = len("lastwordsbeforearchichoicethispassword")
btc = "btcseeddeoemckeadhbschdkbdcsdkdvbxcpcochcrdicibqeebddbcndsbdcpdgcpdncncsescgddclenbmcuducqcacdeldzel"
out["btcseed_del_idx"] = btc.find("del", 3)
out["x_17118919131997_prime"] = isp(17118919131997)
out["hex_dec_88888"] = "88888" in str(int("89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32", 16))
out["h160_dec_9999"] = "9999" in str(int("a9553269572a317e39f0f518cb87c1a0ee1dbae4", 16))
print(json.dumps(out, indent=1))
