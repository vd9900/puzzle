#!/usr/bin/env python3
"""Parse a Telegram Desktop HTML chat export (messages*.html) into JSON lines.

Usage: python3 -I tools/tg_html_parse.py <export_dir> <out.jsonl>
Stdlib only. Reads the export as data; executes nothing from it.
Each record: id, date (as exported, with its UTC offset), date_utc, from (sender display name,
carried forward for 'joined' continuation messages), reply_to, forwarded_from, text,
media (list of relative file paths / media kinds), page.
"""
import datetime as dt
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


VOID = {'br', 'img', 'hr', 'input', 'meta', 'link', 'source', 'wbr'}


def page_key(p):
    m = re.search(r'messages(\d*)\.html$', p.name)
    return int(m.group(1) or 1)


class ExportParser(HTMLParser):
    def __init__(self, page):
        super().__init__(convert_charrefs=True)
        self.page = page
        self.records = []
        self.cur = None
        self.stack = []          # (tag, classes) for open elements
        self.capture = None      # which field is being captured
        self.capture_depth = 0
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get('class') or '').split())
        if self.capture is not None and tag not in VOID:
            self.capture_depth += 1
        if tag == 'div' and 'message' in cls and 'default' in cls:
            self.cur = {'id': int(a['id'].replace('message', '')) if a.get('id', '').startswith('message') else None,
                        'joined': 'joined' in cls, 'from': None, 'date': None, 'reply_to': None,
                        'forwarded_from': None, 'text': '', 'media': [], 'page': self.page}
            self.records.append(self.cur)
        if self.cur is not None:
            if tag == 'div' and 'date' in cls and 'details' in cls and a.get('title'):
                self.cur['date'] = a['title']
            if tag == 'div' and 'reply_to' in cls:
                self._start_capture('reply')
            elif tag == 'div' and 'from_name' in cls:
                self._start_capture('forward_from' if self._in_forwarded() else 'from')
            elif tag == 'div' and 'text' in cls and self.capture is None:
                self._start_capture('text')
            if tag == 'a' and self.capture == 'reply':
                m = re.search(r'go_to_message(\d+)', a.get('href', ''))
                if m:
                    self.cur['reply_to'] = int(m.group(1))
            if tag == 'a' and a.get('href') and ('media' in cls or 'photo_wrap' in cls or 'animated_wrap' in cls
                                                 or 'video_file_wrap' in cls):
                self.cur['media'].append(a['href'])
            if tag == 'img' and self.capture is None and a.get('src') and 'emoji' not in cls:
                src = a['src']
                if not src.startswith('data:') and src not in self.cur['media']:
                    self.cur['media'].append(src)
            if tag == 'br' and self.capture == 'text':
                self.buf.append('\n')
        if tag not in VOID:
            self.stack.append((tag, cls))

    def _in_forwarded(self):
        return any('forwarded' in c for _, c in self.stack)

    def _start_capture(self, field):
        self.capture = field
        self.capture_depth = 0
        self.buf = []

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack:
            self.stack.pop()
        if self.capture is not None:
            if self.capture_depth == 0:
                val = html.unescape(''.join(self.buf)).strip()
                if self.capture == 'from':
                    self.cur['from'] = val or self.cur['from']
                elif self.capture == 'forward_from':
                    self.cur['forwarded_from'] = val
                elif self.capture == 'text':
                    self.cur['text'] = (self.cur['text'] + '\n' + val).strip() if self.cur['text'] else val
                self.capture = None
            else:
                self.capture_depth -= 1

    def handle_data(self, data):
        if self.capture in ('from', 'forward_from', 'text'):
            self.buf.append(data)


def to_utc(s):
    m = re.match(r'(\d\d)\.(\d\d)\.(\d{4}) (\d\d):(\d\d):(\d\d) UTC([+-])(\d\d):(\d\d)', s or '')
    if not m:
        return None
    d, mo, y, h, mi, se, sg, oh, om = m.groups()
    t = dt.datetime(int(y), int(mo), int(d), int(h), int(mi), int(se))
    off = dt.timedelta(hours=int(oh), minutes=int(om)) * (1 if sg == '+' else -1)
    return (t - off).isoformat() + 'Z'


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    pages = sorted(src.glob('messages*.html'), key=page_key)
    last_from = None
    n = 0
    with out.open('w') as fh:
        for p in pages:
            ps = ExportParser(p.name)
            ps.feed(p.read_text(encoding='utf-8'))
            for r in ps.records:
                if r['from'] is None and r['joined']:
                    r['from'] = last_from
                last_from = r['from'] or last_from
                r['date_utc'] = to_utc(r['date'])
                del r['joined']
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
                n += 1
    print(f'{n} messages from {len(pages)} pages -> {out}')


if __name__ == '__main__':
    main()
