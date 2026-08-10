# head_file.py
# Prints the first N lines of a file (like Unix 'head').
# Defaults to 10 lines if N is not specified.

from pathlib import Path
from . import color_print

def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
HEAD
Usage:
  head {file} <count>

Parameters:
  count: first <count> lines to print

Files:
  file: a txt-like file for the print function

Notes:
  This makes life easier.
        """)
        return
    path = Path(args[0])
    n = int(args[1]) if len(args) >= 2 and args[1].isdigit() else 10
    if not path.is_file():
        color_print.cprint(f"head: '{args[0]}' not found.", "DARKRED")
        return
    try:
        lines = path.read_text().splitlines()
        print("\n".join(lines[:n]))
    except Exception as e:
        color_print.cprint(f"head: {e}", "DARKRED")
