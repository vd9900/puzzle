# Compute N decimal digits of a famous constant with the system libmpfr (via ctypes; no headers, no downloads).
# Usage: python3 mpfr_digits.py NAME N OUTFILE ; NAME in pi e phi sqrt2 sqrt3 ln2 gamma
# Output: the leading significant digits as one ASCII line (integer part included, no decimal point),
# truncated (RNDZ), followed by a header file OUTFILE.meta with the decimal exponent.
import ctypes, ctypes.util, sys, time, math
name, N, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
lib = ctypes.CDLL('libmpfr.so.6')
RNDN, RNDZ = 0, 1
class MPFR(ctypes.Structure):
    _fields_ = [('prec', ctypes.c_long), ('sign', ctypes.c_int), ('exp', ctypes.c_long), ('d', ctypes.c_void_p)]
P = ctypes.POINTER(MPFR)
lib.mpfr_init2.argtypes = [P, ctypes.c_long]
for f in ('mpfr_const_pi', 'mpfr_const_euler', 'mpfr_const_log2'):
    getattr(lib, f).argtypes = [P, ctypes.c_int]
lib.mpfr_set_ui.argtypes = [P, ctypes.c_ulong, ctypes.c_int]
lib.mpfr_exp.argtypes = [P, P, ctypes.c_int]
lib.mpfr_sqrt_ui.argtypes = [P, ctypes.c_ulong, ctypes.c_int]
lib.mpfr_add_ui.argtypes = [P, P, ctypes.c_ulong, ctypes.c_int]
lib.mpfr_div_2ui.argtypes = [P, P, ctypes.c_ulong, ctypes.c_int]
lib.mpfr_get_str.restype = ctypes.c_void_p
lib.mpfr_get_str.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_long), ctypes.c_int, ctypes.c_size_t, P, ctypes.c_int]
lib.mpfr_free_str.argtypes = [ctypes.c_void_p]
prec = int(math.ceil((N + 40) * math.log2(10))) + 128
x = MPFR(); y = MPFR()
lib.mpfr_init2(ctypes.byref(x), prec); lib.mpfr_init2(ctypes.byref(y), prec)
t = time.time()
if name == 'pi': lib.mpfr_const_pi(ctypes.byref(x), RNDN)
elif name == 'gamma': lib.mpfr_const_euler(ctypes.byref(x), RNDN)
elif name == 'ln2': lib.mpfr_const_log2(ctypes.byref(x), RNDN)
elif name == 'e':
    lib.mpfr_set_ui(ctypes.byref(y), 1, RNDN); lib.mpfr_exp(ctypes.byref(x), ctypes.byref(y), RNDN)
elif name in ('sqrt2', 'sqrt3'): lib.mpfr_sqrt_ui(ctypes.byref(x), int(name[-1]), RNDN)
elif name == 'phi':
    lib.mpfr_sqrt_ui(ctypes.byref(y), 5, RNDN); lib.mpfr_add_ui(ctypes.byref(y), ctypes.byref(y), 1, RNDN)
    lib.mpfr_div_2ui(ctypes.byref(x), ctypes.byref(y), 1, RNDN)
else: raise SystemExit('unknown')
t1 = time.time()
ex = ctypes.c_long()
p = lib.mpfr_get_str(None, ctypes.byref(ex), 10, N + 20, ctypes.byref(x), RNDZ)
s = ctypes.string_at(p); lib.mpfr_free_str(p)
s = s[:N + 10]  # drop the last 10 digits (guard against final-rounding ...999/000 artefacts)
open(out, 'wb').write(s)
open(out + '.meta', 'w').write(f'{name} exp10={ex.value} ndigits={len(s)} compute={t1-t:.1f}s getstr={time.time()-t1:.1f}s head={s[:30].decode()}\n')
print(open(out + '.meta').read(), end='')
