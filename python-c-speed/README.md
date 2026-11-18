# Calling C from Python: how NumPy gets its speed

This project compiles small C functions into shared libraries, calls them from
Python with `ctypes`, and measures how Python, NumPy, and C compare when summing
10 million integers. All commands below are for **macOS** in the Terminal app.

## Files

| File | What it does |
|---|---|
| `sum.c` | C function `sum_array` that adds up an array of 32-bit integers and returns a 64-bit total. |
| `call_sum.py` | Loads `libsum.dylib` with `ctypes`, declares the function's argument and return types, converts `[1, 2, 3, 4, 5]` into a C array, and calls `sum_array`. Prints 15 and checks it against Python's `sum()`. |
| `wrong_types.c` | C function `big()` that returns 5,000,000,000, a value too large for a 32-bit `int`. |
| `wrong_types.py` | Calls `big()` once without declaring `restype` and once with `restype = c_longlong`, then prints both results side by side. The first call silently returns 705,032,704 (the low 32 bits of the real answer). |
| `benchmark.py` | Times a Python `for` loop, built-in `sum()`, `np.sum`, and the C `sum_array` on 10 million integers, plus the cost of converting the list into a C array. Uses the minimum of 5 runs, checks that every method returns the same answer before timing, prints a table, and saves `benchmark_chart.png`. |
| `libload.py` | Small helper used by all three Python scripts. It finds the compiled library next to the scripts and loads it with `ctypes.CDLL`, using `.dylib` on macOS and `.so` on Linux, and prints a clear message if the library is missing or built for the wrong CPU. |
| `requirements.txt` | Python packages needed: NumPy and Matplotlib. |
| `.gitignore` | Keeps compiled libraries, the virtual environment, and macOS `.DS_Store` files out of the repository. |

## One-time setup

**1. Install the C compiler** (skip if `cc --version` already prints a version):

```bash
xcode-select --install
```

On macOS, `cc` and `gcc` both run Apple's Clang compiler. Either name works in
the commands below.

**2. Create a virtual environment and install the Python packages.** A virtual
environment is a private folder of Python packages for this project only. It
avoids the "externally-managed-environment" error that Homebrew Python gives
when you run `pip install` directly.

```bash
cd path/to/this/folder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run `source .venv/bin/activate` again each time you open a new Terminal window.
Your prompt shows `(.venv)` when it is active.

## Compile and run

Run these from inside the project folder.

### 1. `sum.c` and `call_sum.py`

```bash
cc -O2 -shared -fPIC -o libsum.dylib sum.c
python3 call_sum.py
```

Expected output:

```
Input list:            [1, 2, 3, 4, 5]
sum_array (C):         15
sum() (Python check):  15
Match: yes
```

### 2. `wrong_types.c` and `wrong_types.py`

```bash
cc -O2 -shared -fPIC -o libwrong_types.dylib wrong_types.c
python3 wrong_types.py
```

Expected output:

```
                             Without restype      With restype
ctypes return type           c_int (default)        c_longlong
Value Python received            705,032,704     5,000,000,000
Expected value                 5,000,000,000     5,000,000,000
Correct?                               False              True
```

### 3. `benchmark.py`

Needs `libsum.dylib` from step 1.

```bash
python3 benchmark.py
open benchmark_chart.png
```

It takes about 10 to 30 seconds. Close other heavy apps first so they do not
slow down individual runs.

## What the compile flags mean

| Flag | Meaning |
|---|---|
| `-O2` | Turn on optimization. Without it, the C loop runs much slower. |
| `-shared` | Build a shared library (no `main()` required) instead of a program. |
| `-fPIC` | Position-independent code, so the library works at whatever memory address it is loaded. Already the default on macOS, but kept so the command also works on Linux. |
| `-o libsum.dylib` | Output file name. `.dylib` is the macOS extension for shared libraries (Linux uses `.so`, Windows uses `.dll`). |

## Expected benchmark results

Measured on a Linux x86_64 test machine. An Apple Silicon Mac will produce
different absolute times, but the pattern should be the same.

| Method | Time | vs. Python loop |
|---|---|---|
| Python loop | 197 ms | baseline |
| built-in `sum()` | 67 ms | about 3x faster |
| `np.sum` | 2.9 ms | about 70x faster |
| ctypes `sum_array` | 3.5 ms | about 55x faster |
| list to ctypes conversion | 792 ms | about 4x slower |

**How to read it:**

- `sum()` is written in C, but it still unpacks a Python object for every
  element, so it is only a few times faster than the loop.
- `np.sum` and `sum_array` both run a compiled C loop over packed raw numbers,
  so they are 50 to 70 times faster. They trade places from run to run.
- The conversion row is the most important lesson. Turning 10 million Python
  objects into a C array costs more than simply summing them in Python. C only
  pays off when the data is already stored in C-compatible memory, which is why
  NumPy keeps its data in that form all the time.

## Why the benchmark is fair

- All data is built before any timer starts, so only the summing is measured.
- Every method's answer is checked against the formula `N * (N - 1) / 2` before
  timing. A fast wrong answer would stop the script.
- Each method runs 5 times and the fastest run is reported. The fastest run is
  the one with the least interference from other programs.
- `timeit` uses a high-resolution clock meant for benchmarking.
- The conversion cost is reported on its own row instead of being hidden.

## Troubleshooting

**`incompatible architecture` when loading the library.** Your Python and your
library were built for different CPUs. Check both:

```bash
python3 -c "import platform; print(platform.machine())"
file libsum.dylib
```

Both should say `arm64` (Apple Silicon) or both `x86_64` (Intel). If Python says
`x86_64` on an Apple Silicon Mac (common with older Anaconda installs), build an
Intel library to match:

```bash
cc -O2 -shared -fPIC -arch x86_64 -o libsum.dylib sum.c
```

**`Could not find libsum.dylib`.** Run the `cc` command for that file first,
from inside the project folder.

**`ModuleNotFoundError: No module named 'numpy'`.** The virtual environment is
not active. Run `source .venv/bin/activate`.

**`command not found: cc`.** Run `xcode-select --install`.
