"""
libload.py
Shared helper: finds and loads a compiled C library that sits in the
same folder as these scripts, using the right file extension for the OS.
"""
import ctypes
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_library(name):
    """Load lib<name>.dylib on macOS (or lib<name>.so on Linux)."""
    ext = ".dylib" if sys.platform == "darwin" else ".so"
    path = os.path.join(HERE, "lib" + name + ext)
    if not os.path.exists(path):
        sys.exit(
            f"Could not find {path}\n"
            f"Compile it first, for example:\n"
            f"  cc -O2 -shared -fPIC -o lib{name}{ext} {name}.c"
        )
    try:
        return ctypes.CDLL(path)
    except OSError as err:
        sys.exit(
            f"Found {path} but could not load it:\n  {err}\n"
            "If the message mentions an incompatible architecture, your Python\n"
            "and the library were built for different CPUs (arm64 vs x86_64).\n"
            "See the Troubleshooting section of README.md."
        )
