#!/usr/bin/env python3
"""Candidate oracle for the GSMG puzzle.

Usage:
  python3 oracle.py --selftest
  python3 oracle.py --file cands.txt [--label NAME] [--doors N] [--forms N]
  echo "candidate" | python3 oracle.py --stdin

Input file: one candidate per line (UTF-8). Lines starting with '#' are ignored.
For every candidate C the oracle tries, as the openssl `-pass` password:
  C itself, sha256hex(C), and common normalizations (lower, UPPER, alnum-only, nospace)
against the three unsolved blobs (Phase 3.2 inner 80B, SalPhaseIon small 80B, Cosmic Duality 1328B)
under both EVP_BytesToKey digests (sha256, md5).  A hit = valid PKCS#7 padding AND
(printable ratio > 0.8 or an embedded 'Salted__'/'U2FsdGVk' marker).
Padding-only hits are expected at ~1/256 per trial and are NOT reported as hits.

--doors N : additionally probe https://gsmg.io/<sha256hex(C)> for the first N *unique* candidates
            (rate limited 0.5 s; anything but '404 Hello :-)' is reported).
--forms N : additionally POST the first N candidates to the hidden Phase 1 form.
Any structured hit is also appended to scratch/wf/HITS.log (never put key material elsewhere).
"""
import sys, re, hashlib, argparse, subprocess, time, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BLOBS, evp, printable_ratio, sha256hex
from Crypto.Cipher import AES

HITLOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wf', 'HITS.log')

def forms_of(c):
    out = {c, c.lower(), c.upper(), re.sub(r'[^A-Za-z0-9]', '', c), re.sub(r'[^a-z0-9]', '', c.lower()), re.sub(r'\s+', '', c), c.strip()}
    out = {x for x in out if x}
    return out | {sha256hex(x) for x in out}

def pad_ok(pt):
    p = pt[-1]
    return 1 <= p <= 16 and pt.endswith(bytes([p]) * p)

def check_pw(pw):
    pb = pw.encode('utf-8', 'surrogatepass')
    hits = []
    for name, (salt, ct) in BLOBS.items():
        for dg in ('sha256', 'md5'):
            k, iv = evp(pb, salt, dg)
            pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
            if pad_ok(pt):
                body = pt[:-pt[-1]]
                if printable_ratio(body) > 0.8 or b'Salted__' in body or b'U2FsdGVk' in body:
                    hits.append((name, dg, body))
    return hits

def selftest():
    import html as H
    doc = open('/home/vin/bitcoin_puzzle/research/sources/phase2.html').read()
    tas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', doc, re.S)
    import base64
    blob = ''.join(H.unescape(tas[0]).split())
    raw = base64.b64decode(blob); salt, ct = raw[8:16], raw[16:]
    pw = sha256hex('causality').encode()
    k, iv = evp(pw, salt, 'sha256')
    pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
    ok = pad_ok(pt) and pt.startswith(b'The ironic')
    print('SELFTEST phase2 decrypt with sha256("causality"):', 'PASS' if ok else 'FAIL')
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file'); ap.add_argument('--stdin', action='store_true'); ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--label', default=''); ap.add_argument('--doors', type=int, default=0); ap.add_argument('--forms', type=int, default=0)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    lines = (open(a.file, encoding='utf-8', errors='replace').read().split('\n') if a.file else sys.stdin.read().split('\n'))
    cands = [l.rstrip('\r') for l in lines if l.strip() and not l.startswith('#')]
    seen = set(); n = 0; hits = []
    for c in cands:
        for pw in forms_of(c):
            if pw in seen: continue
            seen.add(pw); n += 1
            for name, dg, body in check_pw(pw):
                hits.append({'candidate': c, 'password_form': pw[:80], 'blob': name, 'kdf': dg, 'plaintext_head': body[:120].decode('latin-1')})
                print('!!! STRUCTURED HIT', json.dumps(hits[-1]))
                with open(HITLOG, 'a') as f: f.write(json.dumps({'label': a.label, **hits[-1]}) + '\n')
    print(f'[{a.label}] candidates={len(cands)} unique_password_forms={n} structured_hits={len(hits)}')
    if a.doors:
        probed = 0; seen_h = set()
        for c in cands:
            if probed >= a.doors: break
            for s in (c, re.sub(r'[^A-Za-z0-9]', '', c), re.sub(r'[^a-z0-9]', '', c.lower())):
                h = hashlib.sha256(s.encode()).hexdigest()
                if h in seen_h: continue
                seen_h.add(h); probed += 1
                r = subprocess.run(['curl', '-s', '-o', '/tmp/oracle_d.html', '-w', '%{http_code} %{size_download}', '--max-time', '20', 'https://gsmg.io/' + h], capture_output=True, text=True)
                if r.stdout.strip() != '404 9':
                    print('!!! DOOR RESPONSE', repr(s), h, r.stdout, open('/tmp/oracle_d.html', 'rb').read()[:200])
                    with open(HITLOG, 'a') as f: f.write(json.dumps({'label': a.label, 'door': s, 'hash': h, 'resp': r.stdout}) + '\n')
                time.sleep(0.5)
                if probed >= a.doors: break
        print(f'[{a.label}] door probes={probed}')
    if a.forms:
        posted = 0; seen_f = set()
        for c in cands:
            if posted >= a.forms: break
            for s in (c, re.sub(r'[^a-z0-9]', '', c.lower())):
                if s in seen_f: continue
                seen_f.add(s); posted += 1
                r = subprocess.run(['curl', '-s', '-o', '/tmp/oracle_f.html', '-D', '/tmp/oracle_f.h', '-w', '%{http_code}', '--max-time', '20', '-X', 'POST', '--data-urlencode', 'password=' + s, 'https://gsmg.io/phase1verification'], capture_output=True, text=True)
                if r.stdout.strip() != '404':
                    print('!!! FORM RESPONSE', repr(s), r.stdout, open('/tmp/oracle_f.h').read()[:300])
                    with open(HITLOG, 'a') as f: f.write(json.dumps({'label': a.label, 'form': s, 'resp': r.stdout}) + '\n')
                time.sleep(0.5)
                if posted >= a.forms: break
        print(f'[{a.label}] form posts={posted}')

if __name__ == '__main__':
    main()
