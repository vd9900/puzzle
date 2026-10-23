#!/usr/bin/env python3
"""openssl enc option space beyond EVP_BytesToKey(sha256/md5)+aes-256-cbc: derivations, validated against the real openssl binary."""
import hashlib, base64, subprocess
from Crypto.Cipher import AES
def evp(pw, salt, md, n):
    m = b''; prev = b''
    while len(m) < n:
        prev = hashlib.new(md, prev + pw + salt).digest(); m += prev
    return m[:n]
CIPH = {'aes-256-cbc': (32, 16), 'aes-192-cbc': (24, 16), 'aes-128-cbc': (16, 16), 'aes-256-ecb': (32, 0)}
def derive(pw, salt, kdf, cipher):
    kl, ivl = CIPH[cipher]
    if kdf.startswith('evp-'): m = evp(pw, salt, kdf[4:], kl + ivl)
    else:
        md, it = kdf.split('-')[1], int(kdf.split('-')[2])
        m = hashlib.pbkdf2_hmac(md, pw, salt, it, kl + ivl)
    return m[:kl], m[kl:kl + ivl]
def decrypt(pw, salt, ct, kdf, cipher):
    k, iv = derive(pw, salt, kdf, cipher)
    c = AES.new(k, AES.MODE_ECB) if cipher.endswith('ecb') else AES.new(k, AES.MODE_CBC, iv)
    return c.decrypt(ct)
if __name__ == '__main__':
    msg = b'control plaintext for the openssl option-space check 0123456789abcdef\n'
    pw = 'ctlpass'
    cases = [('aes-256-cbc', ['-pbkdf2'], 'pbkdf2-sha256-10000'), ('aes-256-cbc', ['-pbkdf2', '-md', 'sha512'], 'pbkdf2-sha512-10000'),
             ('aes-256-cbc', ['-pbkdf2', '-md', 'sha1'], 'pbkdf2-sha1-10000'), ('aes-256-cbc', ['-md', 'sha1'], 'evp-sha1'),
             ('aes-256-cbc', ['-md', 'sha512'], 'evp-sha512'), ('aes-128-cbc', ['-md', 'sha256'], 'evp-sha256'),
             ('aes-192-cbc', ['-md', 'sha256'], 'evp-sha256'), ('aes-256-ecb', ['-md', 'sha256'], 'evp-sha256'),
             ('aes-256-cbc', ['-md', 'sha256'], 'evp-sha256')]
    for cipher, flags, kdf in cases:
        out = subprocess.run(['openssl', 'enc', '-' + cipher, '-salt', '-a', '-A', '-pass', 'pass:' + pw] + flags,
                             input=msg, capture_output=True).stdout
        raw = base64.b64decode(out); assert raw[:8] == b'Salted__'
        pt = decrypt(pw.encode(), raw[8:16], raw[16:], kdf, cipher)
        p = pt[-1]; ok = pt[:-p] == msg
        print(f'{cipher:12s} {" ".join(flags):24s} -> {kdf:20s} roundtrip={ok}')
