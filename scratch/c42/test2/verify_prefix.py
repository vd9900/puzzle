# Independent check of the MPFR digit files: first N digits recomputed with pure-Python integer arithmetic
# (Machin arctan for pi, factorial series for e, isqrt for sqrt2/sqrt3/phi, sum 1/(k 2^k) for ln2).
import sys
from math import isqrt
sys.set_int_max_str_digits(0)
N = int(sys.argv[1]); S = 10 ** (N + 20)
def atan_inv(x):
    tot = t = S // x; x2 = x * x; k = 1; sg = -1
    while t:
        t //= x2; tot += sg * (t // (2 * k + 1)); sg = -sg; k += 1
    return tot
def e_():
    tot = 0; t = S; k = 0
    while t: tot += t; k += 1; t //= k
    return tot
def ln2_():
    tot = 0; k = 1; t = S // 2
    while t: tot += t // k; k += 1; t //= 2
    return tot
ref = {'pi': str(4 * (4 * atan_inv(5) - atan_inv(239))), 'e': str(e_()), 'sqrt2': str(isqrt(2 * S * S)),
       'sqrt3': str(isqrt(3 * S * S)), 'phi': str((S + isqrt(5 * S * S)) // 2), 'ln2': str(ln2_())}
for nm, r in ref.items():
    try: f = open(f'{nm}.txt', 'rb').read(N).decode()
    except FileNotFoundError: print(nm, 'missing'); continue
    print(nm, 'first', N, 'digits agree:', f == r[:N])
