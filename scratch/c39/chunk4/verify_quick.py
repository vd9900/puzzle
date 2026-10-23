# Quick deterministic checks of a few chat claims (chunk4). No guessing loops.
import random, sys
D94 = "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
print("len(dbbi block incl. 'abe') =", len(D94))
D = D94[:91]
print("first91 ends with:", D[-8:], "| chat #70820 string len:", len("dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeee"))
def isprime(n):
    return n > 1 and all(n % p for p in range(2, int(n**0.5) + 1))
url = "gsmg.io/theseedisplanted"
lsb = [ord(c) & 1 for c in url]
print("URL LSBs:", "".join(map(str, lsb)), "blue(1)=", sum(lsb), "yellow(0)=", 24 - sum(lsb))
def parse(s, prog):
    pos, i, k, hosts = 1, 0, 0, []
    while i < len(s):
        if isprime(pos):
            if k >= len(prog): return None, i
            n = 1 if prog[k] == 1 else 2
            hosts.append(s[i:i+n]); i += n; k += 1
        else:
            i += 1
        pos += 1
    return hosts, i
def score(hosts, prog):
    if hosts is None: return -1
    ok = 0
    for h, c in zip(hosts, prog):
        if c == 1 and h.startswith('b'): ok += 1
        elif c == 0 and h == 'be': ok += 1
    return ok
prog_fefe = lsb[:20] + [1] + lsb[20:]      # FEFEFE as blue, 21st symbol (Ugur #72215)
prog_nofe = lsb[:]                          # without FEFEFE
prog_fey  = lsb[:20] + [0] + lsb[20:]       # FEFEFE as yellow
for name, prog in [("with FEFEFE blue", prog_fefe), ("no FEFEFE", prog_nofe), ("FEFEFE yellow", prog_fey)]:
    hosts, consumed = parse(D, prog)
    print(f"{name}: hosts={len(hosts) if hosts else None} consumed={consumed} score={score(hosts, prog)} first hosts={hosts[:8] if hosts else None}")
# all-hosts-start-with-b check (Ugur: all 23 hosts start with b, yellow hosts == 'be')
hosts, _ = parse(D, prog_fefe)
print("hosts start with b:", sum(h.startswith('b') for h in hosts), "/", len(hosts), "; yellow hosts:", [h for h, c in zip(hosts, prog_fefe) if c == 0])
# shuffle control
random.seed(1)
cnt = 0; tot = 0; N = 20000
for _ in range(N):
    l = list(D); random.shuffle(l); s = "".join(l)
    h, _ = parse(s, prog_fefe); sc = score(h, prog_fefe); tot += max(sc, 0)
    if sc == 23: cnt += 1
print(f"shuffle control: mean score {tot/N:.2f}/23, hits of 23/23: {cnt}/{N}")
# Elite Booter #71166 / #71448: b's on prime positions, values at prime positions
bpos = [i+1 for i, c in enumerate(D) if c == 'b']
print("count b in dbbi91:", len(bpos), "b at prime positions:", sum(isprime(p) for p in bpos))
vals = [ord(D[p-1]) - 96 for p in range(1, 92) if isprime(p)]
print("values at prime positions (a=1..i=9):", vals, "prime-valued:", sum(v in (2,3,5,7) for v in vals), "/", len(vals))
# X #70989/#70993: primality
for n in (16763473, 574061):
    print(n, "prime" if isprime(n) else "composite", bin(n))
