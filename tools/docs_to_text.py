#!/usr/bin/env python3
"""Convert untrusted shared documents to plain text for reading (never executes anything).

Usage: python3 -I tools/docs_to_text.py <out_dir> <label> <file_or_dir> [...]
Writes <out_dir>/<label>/<flattened name>.txt per input file plus <out_dir>/<label>/INDEX.tsv
(path, kind, bytes, text_chars). Archives are listed and their text-like members are unpacked
into <out_dir>/<label>__unpacked/<archive>/ (fresh dirs) and converted too.
Images/audio/video are skipped (indexed only).
"""
import csv, html, io, json, re, subprocess, sys, tarfile, zipfile
from pathlib import Path

TEXT_EXT = {'.txt', '.md', '.py', '.js', '.h', '.cu', '.c', '.cpp', '.pyx', '.csv', '.json', '.ipynb', '.sh', '.java',
            '.rs', '.go', '.ts', '.sol', '.cfg', '.ini', '.log', '.b64', '.patch', '.xml', '.yaml', '.yml', ''}
MEDIA_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.mp3', '.mp4', '.webm', '.mkv', '.ogg', '.wav', '.tgs',
             '.mov', '.svg', '.xcf', '.heic'}
MAX_CHARS = 400_000


def strip_tags(s):
    s = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', s)
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    return re.sub(r'[ \t]+', ' ', html.unescape(s))


def docx_text(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        xml = z.read('word/document.xml').decode('utf-8', 'replace')
    xml = re.sub(r'</w:p>', '\n', xml)
    return strip_tags(xml)


def xlsx_text(b):
    out = []
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss = z.read('xl/sharedStrings.xml').decode('utf-8', 'replace')
            shared = [strip_tags(x) for x in re.findall(r'(?s)<si>(.*?)</si>', ss)]
        for name in sorted(n for n in z.namelist() if n.startswith('xl/worksheets/sheet')):
            xml = z.read(name).decode('utf-8', 'replace')
            out.append(f'## {name}')
            for row in re.findall(r'(?s)<row[^>]*>(.*?)</row>', xml):
                cells = []
                for attrs, inner in re.findall(r'(?s)<c([^>]*)>(.*?)</c>', row):
                    v = re.search(r'(?s)<v>(.*?)</v>', inner)
                    t = re.search(r't="(\w+)"', attrs)
                    val = v.group(1) if v else strip_tags(inner)
                    if t and t.group(1) == 's' and v:
                        try:
                            val = shared[int(v.group(1))]
                        except (ValueError, IndexError):
                            pass
                    cells.append(val.strip())
                out.append('\t'.join(cells))
    return '\n'.join(out)


def rtf_text(s):
    s = re.sub(r'\\par[d]?', '\n', s)
    s = re.sub(r'\{\\\*[^{}]*\}', '', s)
    s = re.sub(r'\\[a-z]+-?\d* ?', '', s)
    return s.replace('{', '').replace('}', '')


def convert(path: Path):
    ext = path.suffix.lower()
    b = path.read_bytes()
    if ext in MEDIA_EXT:
        return 'media', ''
    if ext == '.pdf':
        r = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, timeout=120)
        return 'pdf', r.stdout.decode('utf-8', 'replace')
    if ext == '.docx':
        return 'docx', docx_text(b)
    if ext == '.xlsx':
        return 'xlsx', xlsx_text(b)
    if ext == '.rtf':
        return 'rtf', rtf_text(b.decode('latin-1'))
    if ext in ('.html', '.htm'):
        return 'html', strip_tags(b.decode('utf-8', 'replace'))
    if ext in TEXT_EXT or ext not in ('.zip', '.xz', '.gz', '.tar', '.7z', '.rar', '.jar', '.bin', '.aes', '.zlib', '.mid',
                                      '.midi', '.so', '.exe', '.dll'):
        s = b.decode('utf-8', 'replace')
        printable = sum(c.isprintable() or c in '\n\r\t' for c in s) / max(1, len(s))
        if printable > 0.9:
            return 'text', s
        return 'binary', f'[binary {len(b)} bytes] hex head: {b[:64].hex()}'
    return 'archive_or_binary', f'[{ext} {len(b)} bytes] hex head: {b[:64].hex()}'


def safe_members_zip(z):
    for m in z.infolist():
        n = m.filename
        if m.is_dir() or n.startswith('/') or '..' in Path(n).parts or m.file_size > 20_000_000:
            continue
        yield m


def unpack(path: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    listing = []
    try:
        if path.suffix.lower() in ('.zip', '.jar'):
            with zipfile.ZipFile(path) as z:
                for m in safe_members_zip(z):
                    listing.append(f'{m.file_size}\t{m.filename}')
                    target = dest / m.filename
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(z.read(m))
        elif path.name.endswith(('.tar.xz', '.tar.gz', '.tgz', '.tar')):
            with tarfile.open(path) as t:
                for m in t.getmembers():
                    if not m.isfile() or m.name.startswith('/') or '..' in Path(m.name).parts or m.size > 20_000_000:
                        continue
                    listing.append(f'{m.size}\t{m.name}')
                    target = dest / m.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(t.extractfile(m).read())
    except Exception as e:  # corrupt/unsupported archive: just record it
        listing.append(f'ERROR {e!r}')
    return listing


def flat(name):
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name)[:150]


def main():
    out_root, label, inputs = Path(sys.argv[1]), sys.argv[2], [Path(p) for p in sys.argv[3:]]
    out = out_root / label
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for p in inputs:
        files += sorted(x for x in p.rglob('*') if x.is_file()) if p.is_dir() else [p]
    rows = []
    for f in files:
        try:
            kind, txt = convert(f)
        except Exception as e:
            kind, txt = 'error', f'[error {e!r}]'
        if kind == 'archive_or_binary' and f.suffix.lower() in ('.zip', '.jar', '.xz', '.gz', '.tar'):
            dest = out_root / f'{label}__unpacked' / flat(f.name)
            listing = unpack(f, dest)
            txt += '\n[archive members]\n' + '\n'.join(listing)
            for m in sorted(x for x in dest.rglob('*') if x.is_file()):
                try:
                    k2, t2 = convert(m)
                except Exception as e:
                    k2, t2 = 'error', repr(e)
                if k2 != 'media':
                    (out / (flat(f.name) + '__' + flat(str(m.relative_to(dest))) + '.txt')).write_text(t2[:MAX_CHARS])
                rows.append((str(m), 'archive:' + k2, m.stat().st_size, len(t2)))
        if kind != 'media':
            (out / (flat(f.name) + '.txt')).write_text(txt[:MAX_CHARS])
        rows.append((str(f), kind, f.stat().st_size, len(txt)))
    with (out / 'INDEX.tsv').open('w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['path', 'kind', 'bytes', 'text_chars'])
        w.writerows(rows)
    kinds = {}
    for r in rows:
        kinds[r[1]] = kinds.get(r[1], 0) + 1
    print(label, len(rows), 'files', json.dumps(kinds))


if __name__ == '__main__':
    main()
