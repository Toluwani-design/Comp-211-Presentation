/*
 * wrong_types.c
 * A function that returns a number too large for a 32-bit int.
 * It shows what happens when Python is not told the return type.
 *
 * Build on macOS:
 *   cc -O2 -shared -fPIC -o libwrong_types.dylib wrong_types.c
 */

/* 5,000,000,000 needs 64 bits. The largest 32-bit int is 2,147,483,647. */
long long big(void) {
    return 5000000000LL;
}
