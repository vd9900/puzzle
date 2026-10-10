"""Assemble chat_substantive corpus from scratch/chat_chunks/chunk*.filtered.txt.

Rules (from task): strip header lines, one message per line (multi-line bodies
joined), drop exact duplicates, drop lines shorter than 8 characters.
Conventions mirror wf/build_creator_corpus.py (same HDR regex, same flatten,
dedupe keeps earliest timestamp, chronological output).
"""
import glob, re
from datetime import datetime

ROOT = "/home/vin/bitcoin_puzzle"
SRC = sorted(glob.glob(f"{ROOT}/scratch/chat_chunks/chunk*.filtered.txt"))
OUT = f"{ROOT}/scratch/corpora/chat_substantive.txt"
MIN_CHARS = 8

HDR = re.compile(r"^=== \[(\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2}:\d{2}) UTC[+-]\d{2}:\d{2}\] (.*)$")

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

seen = {}  # text -> earliest timestamp
n_records = 0; n_empty = 0; n_short = 0; n_dupe = 0
per_file = {}
for path in SRC:
    recs = parse(path)
    per_file[path.rsplit("/", 1)[-1]] = len(recs)
    for (d, t, _author), body in recs:
        n_records += 1
        txt = flatten(body)
        if not txt:
            n_empty += 1; continue
        if len(txt) < MIN_CHARS:
            n_short += 1; continue
        ts = datetime.strptime(f"{d} {t}", "%d.%m.%Y %H:%M:%S")
        if txt in seen:
            n_dupe += 1
            if ts < seen[txt]: seen[txt] = ts
        else:
            seen[txt] = ts

ordered = sorted(seen.items(), key=lambda kv: kv[1])
with open(OUT, "w", encoding="utf-8") as fh:
    for txt, _ in ordered:
        fh.write(txt + "\n")

print("source files:", len(SRC))
print("records per file:", per_file)
print("total records:", n_records)
print("dropped empty:", n_empty, "| dropped <%d chars:" % MIN_CHARS, n_short, "| dropped dupes:", n_dupe)
print("unique messages written:", len(ordered))
print("date span:", ordered[0][1].date(), "->", ordered[-1][1].date())
