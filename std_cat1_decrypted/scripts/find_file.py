# find_file.py
# Searches recursively for files matching a pattern (like Unix 'find').
# Pattern supports glob syntax, e.g. "*.txt" or "config*".

import os
from pathlib import Path
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
FIND_FILE
Usage:
  find_file <pattern> <start_dir>

Parameters:
  pattern: what to find
  start_dir: where to start. If empty, uses cwd.

Notes:
  Organize your files, so you don't need this.
""")
        return
    pattern = args[0]
    start = Path(args[1]) if len(args) >= 2 else Path(os.getcwd())
    if not start.is_dir():
        color_print.cprint(f"find: '{start}' is not a directory.", "DARKRED")
        return
    results = list(start.rglob(pattern))
    if not results:
        print(f"find: no matches for '{pattern}'")
        return
    for p in results:
        print(p)
