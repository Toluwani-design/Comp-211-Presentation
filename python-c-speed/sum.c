/*
 * sum.c
 * A small C function that adds up an array of 32-bit integers.
 * It is compiled into a shared library (libsum.dylib on macOS)
 * so that Python can call it through ctypes.
 *
 * Build on macOS:
 *   cc -O2 -shared -fPIC -o libsum.dylib sum.c
 */
#include <stdint.h>

/*
 * arr: pointer to the first element of a packed array of int32 values
 * n:   number of elements in the array
 * Returns the total as a 64-bit integer so large sums do not overflow.
 */
int64_t sum_array(const int32_t *arr, int64_t n) {
    int64_t total = 0;
    for (int64_t i = 0; i < n; i++) {
        total += arr[i];
    }
    return total;
}
