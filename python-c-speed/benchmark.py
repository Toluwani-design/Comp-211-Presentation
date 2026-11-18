"""
benchmark.py
Times five ways of summing 10 million integers:
  1. a plain Python for loop
  2. Python's built-in sum()
  3. NumPy's np.sum
  4. our own C sum_array, called through ctypes
  5. the one-time cost of converting the Python list into a ctypes array

Each timing is the minimum of 5 runs. All answers are checked to match
before any timing is reported. Prints a results table and saves a bar
chart to benchmark_chart.png.

Run on macOS (after compiling sum.c into libsum.dylib):
  python3 benchmark.py
"""
import ctypes
import platform
import sys
import timeit

import numpy as np
import matplotlib

matplotlib.use("Agg")  # write the chart to a file; no window needed
import matplotlib.pyplot as plt

from libload import load_library

N = 10_000_000
REPEATS = 5
CHART_FILE = "benchmark_chart.png"


def best_time(func):
    """Run func once per repeat, REPEATS times, and return the fastest run."""
    return min(timeit.repeat(func, number=1, repeat=REPEATS))


# ---- Load the C library and declare its signature ----------------------
lib = load_library("sum")
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
lib.sum_array.restype = ctypes.c_int64

# ---- Build all the data BEFORE timing, so only the summing is measured ---
print(f"Preparing {N:,} integers...")
data_list = list(range(N))                       # Python objects
data_np = np.arange(N, dtype=np.int64)           # packed int64 values
c_array = (ctypes.c_int32 * N)(*data_list)       # packed int32 values for C


def python_loop():
    total = 0
    for x in data_list:
        total += x
    return total


def builtin_sum():
    return sum(data_list)


def numpy_sum():
    return int(data_np.sum())


def ctypes_sum():
    return lib.sum_array(c_array, N)


def list_to_ctypes():
    return (ctypes.c_int32 * N)(*data_list)


# ---- Check correctness first: a fast wrong answer means nothing ----------
expected = N * (N - 1) // 2
answers = {
    "Python loop": python_loop(),
    "built-in sum()": builtin_sum(),
    "np.sum": numpy_sum(),
    "ctypes sum_array": ctypes_sum(),
}
for name, value in answers.items():
    if value != expected:
        sys.exit(f"MISMATCH: {name} returned {value:,}, expected {expected:,}")
print(f"All four methods agree: {expected:,}\n")

# ---- Time everything --------------------------------------------------------
print(f"Timing each method (min of {REPEATS} runs). This takes about 10 to 20 seconds...")
results = [
    ("Python loop", best_time(python_loop)),
    ("built-in sum()", best_time(builtin_sum)),
    ("np.sum", best_time(numpy_sum)),
    ("ctypes sum_array", best_time(ctypes_sum)),
    ("list -> ctypes conversion", best_time(list_to_ctypes)),
]
baseline = results[0][1]

# ---- Results table ----------------------------------------------------------
print()
print(f"Machine: {platform.machine()}, Python {platform.python_version()}, "
      f"NumPy {np.__version__}")
print(f"{'Method':<28}{'Time (s)':>10}{'Time (ms)':>12}{'vs. Python loop':>18}")
print("-" * 68)
for name, seconds in results:
    ratio = baseline / seconds
    if name == "Python loop":
        label = "baseline"
    elif ratio >= 1:
        label = f"{ratio:.1f}x faster"
    else:
        label = f"{1 / ratio:.1f}x slower"
    print(f"{name:<28}{seconds:>10.4f}{seconds * 1000:>12.1f}{label:>18}")
print("-" * 68)
print("Note: the conversion row is a one-time cost, not a summing method.")
print("Converting on every call makes ctypes slower than the plain loop.")

# ---- Bar chart --------------------------------------------------------------
names = [name for name, _ in results]
millis = [seconds * 1000 for _, seconds in results]
bar_color = "#2a78d6"        # summing methods
conversion_color = "#9a9a96"  # the conversion cost is a different kind of bar
colors = [bar_color] * 4 + [conversion_color]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(names, millis, color=colors, width=0.6)
ax.set_yscale("log")  # times differ by ~100x, so a log scale keeps every bar visible
ax.set_ylim(bottom=1)  # start the axis at 1 ms so bar heights compare fairly
ax.set_ylabel("Time in milliseconds (log scale, lower is faster)")
ax.set_title(f"Summing {N:,} integers on {platform.machine()} (min of {REPEATS} runs)")

for bar, ms in zip(bars, millis):
    ax.annotate(f"{ms:,.1f} ms", (bar.get_x() + bar.get_width() / 2, ms),
                xytext=(0, 4), textcoords="offset points",
                ha="center", va="bottom", fontsize=9, color="#333333")

ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", which="major", color="#e5e5e5", linewidth=0.8)
ax.set_axisbelow(True)
plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
fig.tight_layout()
fig.savefig(CHART_FILE, dpi=150)
print(f"\nChart saved to {CHART_FILE}  (open it with:  open {CHART_FILE})")
