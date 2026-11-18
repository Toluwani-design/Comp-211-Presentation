# Python Libraries Implemented in C

For this project, I wanted to find out why NumPy is so much faster than regular Python. I wrote a small C function, compiled it into a shared library, called it from Python with `ctypes`, and then timed it against a plain Python loop and NumPy.

## What I Found

I ran everything on my MacBook Air (Apple Silicon) with Python 3.14 and NumPy 2.5. Each method added up the same 10 million numbers, and the script checked that they all got the same answer (49,999,995,000,000) before timing anything.

| Method | Time | Compared with the Python loop |
|---|---|---|
| Python loop | 260.5 ms | baseline |
| Built-in `sum()` | 43.3 ms | 6x faster |
| `np.sum` | 1.8 ms | 143x faster |
| My C function through `ctypes` | 1.3 ms | 208x faster |
| Converting the list into a C array | 984.9 ms | 3.8x slower |

What I learned:

1. **How the data is stored matters most.** A Python list does not hold the numbers themselves. It holds pointers to separate number objects spread out in memory, so Python has to follow a pointer, check the type, and make a new object for every number. NumPy and C just read numbers that sit right next to each other in one block.
2. **Calling C is only faster if the data is already in C form.** Turning my Python list into a C array took about 750 times longer than the C sum itself, and it was even slower than just using the Python loop.
3. **NumPy skips that problem.** A NumPy array keeps its numbers packed together from the start, so it never has to convert anything.

## Presentation
You can view the full slide deck here: [Comp 211 Python vs C Presentation (Google Slides)](https://docs.google.com/presentation/d/1Ph8b4soXo1sHJvGfCFQco9IgniUpAqfMihIkPzfUMn0/edit?usp=sharing)

## Files

| File | What it does |
|---|---|
| `sum.c` | A C function, `sum_array`, that adds up an array of integers. |
| `call_sum.py` | Loads the compiled C library with `ctypes`, calls `sum_array` on `[1, 2, 3, 4, 5]`, and checks the answer against Python's `sum()`. |
| `wrong_types.c` | A C function, `big()`, that returns 5,000,000,000. |
| `wrong_types.py` | Calls `big()` once without telling Python the return type and once with it, and shows both results side by side. |
| `benchmark.py` | Times the Python loop, `sum()`, `np.sum`, my C function, and the list-to-C conversion. It prints a table and saves `benchmark_chart.png`. |
| `libload.py` | A helper that finds the compiled library so the scripts work from any folder. |
| `requirements.txt` | The Python packages needed (NumPy and Matplotlib). |
| `.gitignore` | Keeps compiled `.dylib` files and the `.venv` folder out of the repo. |

## Setup (run once)

These commands are for macOS. Run them from inside the `python-c-speed` folder.

```bash
xcode-select --install            # installs the C compiler; skip if `cc --version` works
python3 -m venv .venv             # creates a virtual environment
source .venv/bin/activate         # turns it on; repeat in every new terminal window
pip install -r requirements.txt   # installs NumPy and Matplotlib
```

## How to Run

### 1. Compile the C code

```bash
cc -O2 -shared -fPIC -o libsum.dylib sum.c
cc -O2 -shared -fPIC -o libwrong_types.dylib wrong_types.c
```

| Flag | What it does |
|---|---|
| `-O2` | Turns on optimization so the C code runs fast. |
| `-shared` | Makes a shared library instead of a program, so it does not need a `main()`. |
| `-fPIC` | Lets the code work at whatever memory address it gets loaded into. |
| `-o` | Names the output file. |

A shared library is a file of compiled functions that another program can load while it is running. On a Mac it ends in `.dylib`, and on Linux it ends in `.so`.

### 2. Call C from Python

```bash
python3 call_sum.py
```

Expected output:

```
Input list:            [1, 2, 3, 4, 5]
sum_array (C):         15
sum() (Python check):  15
Match: yes
```

### 3. See what happens with the wrong types

```bash
python3 wrong_types.py
```

If you do not tell `ctypes` the return type, it assumes the C function returns a 32-bit integer. It only keeps the low 32 bits of 5,000,000,000, so Python prints **705,032,704** (5,000,000,000 mod 2^32) and gives no error. Once the return type is set to `c_longlong`, it prints the right answer.

### 4. Run the benchmark

```bash
python3 benchmark.py
open benchmark_chart.png
```

This needs `libsum.dylib` from step 1 and takes about 10 to 20 seconds. The chart uses a log scale because the times are so far apart.
