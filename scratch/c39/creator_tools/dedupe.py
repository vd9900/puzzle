import sys, re
src, dst = sys.argv[1], sys.argv[2]
seen = set()
out = []
for line in open(src, encoding='utf-8'):
    line = line.rstrip('\n')
    m = re.match(r'^  prev #(\d+) ', line)
    if m:
        mid = m.group(1)
        if mid in seen:
            continue
        seen.add(mid)
        # shorten "prev" prefix
        out.append(' p' + line[6:])
        continue
    if line.startswith('===== CREATOR MSG #'):
        mid = line.split('#')[1].split()[0]
        seen.add(mid)
        out.append(line.replace('===== CREATOR MSG ', '== C'))
        continue
    if line.strip() == '':
        continue
    out.append(line)
open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
