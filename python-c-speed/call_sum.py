"""
call_sum.py
Loads the compiled sum_array function and calls it on [1, 2, 3, 4, 5].

Run on macOS (after compiling sum.c into libsum.dylib):
  python3 call_sum.py
"""
import ctypes

from libload import load_library

# 1. Load the shared library into this Python process.
lib = load_library("sum")

# 2. Declare the C signature. The compiled file has no type information,
#    so Python must be told what the function takes and returns.
#    C:  int64_t sum_array(const int32_t *arr, int64_t n)
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
lib.sum_array.restype = ctypes.c_int64

# 3. Marshal the Python list into a real C array of five packed int32 values.
nums = [1, 2, 3, 4, 5]
c_array = (ctypes.c_int32 * len(nums))(*nums)

# 4. Call the C function.
result = lib.sum_array(c_array, len(nums))

print(f"Input list:            {nums}")
print(f"sum_array (C):         {result}")
print(f"sum() (Python check):  {sum(nums)}")
print("Match:", "yes" if result == sum(nums) else "NO")
