#!/usr/bin/env python3
"""Generate dictionary-campaign candidates from a corpus.
Rules: for each non-empty line (metadata header lines '#### source:' / '## SOURCE:' skipped):
  - the whole line (and, if it starts with '#', the line with leading '#'/spaces removed, because fastcheck treats '#'-lines as comments)
  - every clause: split on , ; : . ? !  (stripped, non-empty)
  - every word window of length 1..MAXWIN over whitespace-split tokens, joined by single spaces
Output is streamed unsorted to stdout; caller dedups with `sort -u`.
Usage: gen_engine.py CORPUS [MAXWIN]
"""
import sys, re
SPLIT = re.compile(r'[,;:.?!]')
path = sys.argv[1]; maxwin = int(sys.argv[2]) if len(sys.argv) > 2 else 8
w = sys.stdout.write
for raw in open(path, encoding='utf-8', errors='replace'):
    line = raw.strip()
    if not line or line.startswith('#### source:') or line.startswith('## SOURCE:'): continue
    w(line + '\n')
    if line.startswith('#'):
        s = line.lstrip('# ').strip()
        if s: w(s + '\n')
    for cl in SPLIT.split(line):
        cl = cl.strip()
        if cl and cl != line: w(cl + '\n')
    words = line.split(); n = len(words)
    for i in range(n):
        for L in range(1, maxwin + 1):
            if i + L > n: break
            w(' '.join(words[i:i + L]) + '\n')
