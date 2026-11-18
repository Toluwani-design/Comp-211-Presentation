"""
wrong_types.py
Calls big() twice: once without declaring restype, once with it.
Without restype, ctypes assumes the function returns a 32-bit C int,
so it keeps only the low 32 bits of the real 64-bit answer.

Run on macOS (after compiling wrong_types.c into libwrong_types.dylib):
  python3 wrong_types.py
"""
import ctypes

from libload import load_library

EXPECTED = 5_000_000_000

# Call 1: no restype declared. ctypes falls back to its default, c_int (32 bits).
lib = load_library("wrong_types")
without_restype = lib.big()

# Call 2: declare the real return type, long long (64 bits).
lib.big.restype = ctypes.c_longlong
with_restype = lib.big()

# Where the wrong number comes from: the low 32 bits of the true value.
low_32_bits = EXPECTED % 2**32

print("C function: long long big(void) { return 5000000000LL; }")
print()
print(f"{'':<26}{'Without restype':>18}{'With restype':>18}")
print(f"{'ctypes return type':<26}{'c_int (default)':>18}{'c_longlong':>18}")
print(f"{'Value Python received':<26}{without_restype:>18,}{with_restype:>18,}")
print(f"{'Expected value':<26}{EXPECTED:>18,}{EXPECTED:>18,}")
print(f"{'Correct?':<26}{str(without_restype == EXPECTED):>18}{str(with_restype == EXPECTED):>18}")
print()
print(f"5,000,000,000 mod 2^32 = {low_32_bits:,}")
print("The wrong answer is exactly the low 32 bits of the real one. No error was raised.")
