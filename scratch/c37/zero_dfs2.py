import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37')
from common import DBBI, FAED, primes_upto
from zero_dfs import dfs
import string
CS = {
 'lower': set(range(0x61,0x7b)),
 'print': set(range(0x20,0x7f)),
 'hex': set(b'0123456789abcdef'),
 'HEX': set(b'0123456789ABCDEF'),
 'b64': set((string.ascii_letters+string.digits+'+/=').encode()),
 'b58': set(b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'),
 'alnum': set((string.ascii_letters+string.digits).encode()),
}
P = set(primes_upto(1000))
for name, s0 in (('FAED', FAED), ('DBBI', DBBI)):
    for rev in (False, True):
        s = s0[::-1] if rev else s0
        n = len(s)
        allows = {
          'prime1L': {i for i in range(n) if (i+1) in P},
          'prime0L': {i for i in range(n) if i in P},
          'prime1R': {i for i in range(n) if (n-i) in P},
          'prime0R': {i for i in range(n) if (n-1-i) in P},
        }
        for an, al in allows.items():
            for cn, cs in CS.items():
                sols, best, nodes = dfs(s, 'abcdefghi', cs, max_nodes=300000, allow=al)
                tag = f'{name}{"-rev" if rev else ""} {an} {cn}'
                if sols or best[0] >= 10:
                    print(tag, 'sols', len(sols), 'deepest', best[0], 'nodes', nodes)
                    for v,z in sols[:2]: print('  ', v.to_bytes((v.bit_length()+7)//8,'big')[:120], len(z))
print('done')
