import re, sys
from datetime import datetime

ROOT = "/home/vin/bitcoin_puzzle"
SRC = [
    f"{ROOT}/research/evidence/cycle02/_work__creator_jrk.txt",
    f"{ROOT}/research/evidence/cycle02/_work__chat_transcript.txt",
]
OUT = f"{ROOT}/scratch/corpora/creator_messages.txt"

HDR = re.compile(r"^=== \[(\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2}:\d{2}) UTC[+-]\d{2}:\d{2}\] (.*)$")
# author forms accepted: "Jrk Bgrt", forwarded "Jrk Bgrt dd.mm.yyyy hh:mm:ss", "SoWut", "Admin"
AUTH = re.compile(r"^(Jrk Bgrt|SoWut|Admin)(?: (\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2}:\d{2}))?\s*$")

def parse(path):
    recs = []
    hdr = None; body = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = HDR.match(line)
            if m:
                if hdr: recs.append((hdr, body))
                hdr = m.groups(); body = []
            elif hdr is not None:
                body.append(line)
    if hdr: recs.append((hdr, body))
    return recs

def flatten(body):
    parts = [re.sub(r"\s+", " ", l).strip() for l in body]
    return " ".join(p for p in parts if p)

stats = {"records": {}, "selected": {}, "by_author": {}}
seen = {}   # text -> (ts, author)
for path in SRC:
    recs = parse(path)
    stats["records"][path.split("/")[-1]] = len(recs)
    sel = 0
    for (d, t, author), body in recs:
        am = AUTH.match(author)
        if not am: continue
        name, fd, ft = am.groups()
        txt = flatten(body)
        if not txt: continue
        sel += 1
        stats["by_author"][name] = stats["by_author"].get(name, 0) + 1
        ts = datetime.strptime(f"{fd or d} {ft or t}", "%d.%m.%Y %H:%M:%S")
        if txt not in seen or ts < seen[txt][0]:
            seen[txt] = (ts, name)
    stats["selected"][path.split("/")[-1]] = sel

ordered = sorted(seen.items(), key=lambda kv: kv[1][0])
with open(OUT, "w", encoding="utf-8") as fh:
    for txt, _ in ordered:
        fh.write(txt + "\n")

# sanity: creator-file texts not present among transcript Jrk Bgrt texts
cf = {flatten(b) for (_, _, a), b in parse(SRC[0]) if AUTH.match(a)}
tr = {flatten(b) for (_, _, a), b in parse(SRC[1]) if AUTH.match(a)}
print("stats:", stats)
print("unique messages written:", len(ordered))
print("creator-file texts missing from transcript selection:", len(cf - tr))
print("author breakdown of unique lines:", {n: sum(1 for _, (ts, a) in ordered if a == n) for n in stats["by_author"]})
print("date span:", ordered[0][1][0].date(), "->", ordered[-1][1][0].date())
