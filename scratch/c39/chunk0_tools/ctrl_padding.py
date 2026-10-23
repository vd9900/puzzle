"""Control: rate of valid PKCS7 padding for RANDOM passwords on blobs (tests Y #63069 claim). Not a solution search."""
import base64, hashlib, os, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
blobs = {
 'salph': 'U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9zQvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ',
 'p32inner': 'U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46zgKlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4',
}
def evp(pw, salt, h):
    out, prev = b'', b''
    while len(out) < 48:
        prev = h(prev + pw + salt).digest(); out += prev
    return out[:32], out[32:48]
def ok(pt):
    p = pt[-1]
    return 1 <= p <= 16 and pt[-p:] == bytes([p]) * p
for name, b in blobs.items():
    raw = base64.b64decode(b); salt, ct = raw[8:16], raw[16:]
    for hn, h in (('md5', hashlib.md5), ('sha256', hashlib.sha256)):
        n = 13000; hits = 0
        for _ in range(n):
            pw = os.urandom(32).hex().encode()
            k, iv = evp(pw, salt, h)
            d = Cipher(algorithms.AES(k), modes.CBC(iv)).decryptor()
            hits += ok(d.update(ct) + d.finalize())
        print(name, len(raw), 'ct', len(ct), hn, 'valid-pad', hits, '/', n)
cd = sys.argv[1]
raw = base64.b64decode(cd); print('cosmic raw', len(raw), 'ct', len(raw) - 16)
